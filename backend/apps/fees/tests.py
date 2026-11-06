import base64
import hashlib
import hmac
import json
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import override_settings
from rest_framework.test import APITestCase

from apps.accounts.models import Center, User
from apps.academics.models import Batch, Course, Enrollment

from .models import EsewaTransaction, Fee, Payment


@override_settings(
    ESEWA_FORM_URL="https://rc-epay.esewa.com.np/api/epay/main/v2/form",
    ESEWA_STATUS_URL="https://rc-epay.esewa.com.np/api/epay/transaction/status/",
    ESEWA_SECRET_KEY="test-secret",
    ESEWA_PRODUCT_CODE="EPAYTEST",
    ESEWA_SUCCESS_URL="http://localhost:5173/student/payments/esewa/success",
    ESEWA_FAILURE_URL="http://localhost:5173/student/payments/esewa/failure",
)
class EsewaPaymentTests(APITestCase):
    def setUp(self):
        self.center = Center.objects.create(name="Center A", code="A")
        self.other_center = Center.objects.create(name="Center B", code="B")
        self.student = User.objects.create_user("student@example.com", password="Password123!", role=User.Role.STUDENT, center=self.center)
        self.other_student = User.objects.create_user("other@example.com", password="Password123!", role=User.Role.STUDENT, center=self.other_center)
        self.admin = User.objects.create_user("admin@example.com", password="Password123!", role=User.Role.ADMIN, center=self.center)
        course = Course.objects.create(center=self.center, name="Math", fee_amount=Decimal("1000.00"))
        teacher = User.objects.create_user("teacher@example.com", password="Password123!", role=User.Role.TEACHER, center=self.center)
        batch = Batch.objects.create(center=self.center, course=course, teacher=teacher, name="A", start_date=date.today())
        enrollment = Enrollment.objects.create(center=self.center, student=self.student, batch=batch)
        self.fee = Fee.objects.create(center=self.center, student=self.student, enrollment=enrollment, amount_due=Decimal("1000.00"), due_date=date.today())

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def initiate(self, amount="100.00", fee_id=None):
        return self.client.post(f"/api/fees/{fee_id or self.fee.id}/esewa/initiate/", {"amount": amount}, format="json")

    def signed_data(self, transaction_uuid, total_amount="100.00", product_code="EPAYTEST", signature=None):
        payload = {
            "transaction_code": "000123",
            "status": "COMPLETE",
            "total_amount": total_amount,
            "transaction_uuid": transaction_uuid,
            "product_code": product_code,
            "signed_field_names": "total_amount,transaction_uuid,product_code",
        }
        message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
        payload["signature"] = signature or base64.b64encode(hmac.new(b"test-secret", message.encode(), hashlib.sha256).digest()).decode()
        return base64.b64encode(json.dumps(payload).encode()).decode()

    def test_initiate_returns_signed_form(self):
        self.authenticate(self.student)
        response = self.initiate()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["form_url"], "https://rc-epay.esewa.com.np/api/epay/main/v2/form")
        fields = response.data["fields"]
        self.assertEqual(fields["signed_field_names"], "total_amount,transaction_uuid,product_code")
        message = ",".join(f"{key}={fields[key]}" for key in fields["signed_field_names"].split(","))
        expected = base64.b64encode(hmac.new(b"test-secret", message.encode(), hashlib.sha256).digest()).decode()
        self.assertEqual(fields["signature"], expected)

    def test_student_cannot_initiate_other_student_fee(self):
        self.authenticate(self.other_student)
        response = self.initiate(fee_id=self.fee.id)
        self.assertEqual(response.status_code, 404)

    def test_amount_above_balance_is_rejected(self):
        self.authenticate(self.student)
        self.assertEqual(self.initiate("1000.01").status_code, 400)

    def test_tampered_signature_is_rejected(self):
        self.authenticate(self.student)
        transaction_uuid = self.initiate().data["transaction_uuid"]
        response = self.client.post("/api/payments/esewa/verify/", {"data": self.signed_data(transaction_uuid, signature="tampered")}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Payment.objects.count(), 0)

    @patch("apps.fees.views.requests.get")
    def test_non_complete_status_is_rejected(self, mocked_get):
        self.authenticate(self.student)
        transaction_uuid = self.initiate().data["transaction_uuid"]
        mocked_get.return_value.json.return_value = {"status": "PENDING"}
        mocked_get.return_value.raise_for_status.return_value = None
        response = self.client.post("/api/payments/esewa/verify/", {"data": self.signed_data(transaction_uuid)}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Payment.objects.count(), 0)

    def test_mismatched_amount_is_rejected(self):
        self.authenticate(self.student)
        transaction_uuid = self.initiate().data["transaction_uuid"]
        response = self.client.post("/api/payments/esewa/verify/", {"data": self.signed_data(transaction_uuid, "90.00")}, format="json")
        self.assertEqual(response.status_code, 400)

    @patch("apps.fees.views.requests.get")
    def test_valid_verify_is_idempotent(self, mocked_get):
        self.authenticate(self.student)
        transaction_uuid = self.initiate().data["transaction_uuid"]
        mocked_get.return_value.json.return_value = {"status": "COMPLETE", "refId": "ESW-123"}
        mocked_get.return_value.raise_for_status.return_value = None
        data = {"data": self.signed_data(transaction_uuid)}
        first = self.client.post("/api/payments/esewa/verify/", data, format="json")
        second = self.client.post("/api/payments/esewa/verify/", data, format="json")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Fee.objects.get(pk=self.fee.pk).status, Fee.Status.PARTIAL)

    def test_failure_does_not_change_balance(self):
        self.authenticate(self.student)
        transaction_uuid = self.initiate().data["transaction_uuid"]
        response = self.client.post("/api/payments/esewa/failure/", {"transaction_uuid": transaction_uuid}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Fee.objects.get(pk=self.fee.pk).balance, Decimal("1000.00"))
        self.assertEqual(EsewaTransaction.objects.get(transaction_uuid=transaction_uuid).status, EsewaTransaction.Status.CANCELED)

    def test_admin_cash_payment_remains_supported(self):
        payment = Payment.objects.create(fee=self.fee, amount=Decimal("100.00"), status=Payment.Status.CONFIRMED, method=Payment.Method.CASH, received_by=self.admin)
        self.fee.refresh_status()
        self.assertEqual(payment.method, Payment.Method.CASH)
        self.assertEqual(Fee.objects.get(pk=self.fee.pk).status, Fee.Status.PARTIAL)
