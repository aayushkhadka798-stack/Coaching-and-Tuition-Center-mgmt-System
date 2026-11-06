import base64
import hashlib
import hmac
import json
import uuid
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin, IsStudent

from .models import EsewaTransaction, Fee, Payment


class EsewaThrottle(UserRateThrottle):
    scope = "esewa"


def money(value):
    return f"{Decimal(value):.2f}"


def fee_data(fee):
    return {
        "id": fee.id,
        "student": {"id": fee.student_id, "email": fee.student.email},
        "amount_due": money(fee.amount_due),
        "paid_amount": money(fee.paid_amount),
        "balance": money(fee.balance),
        "due_date": fee.due_date,
        "status": fee.status,
    }


def payment_data(payment):
    student = payment.fee.student
    fee = payment.fee
    return {
        "id": payment.id,
        "fee": {
            "id": fee.id,
            "amount_due": money(fee.amount_due),
            "due_date": fee.due_date,
            "status": fee.status,
        },
        "student": {
            "id": student.id,
            "name": student.get_full_name() or student.email,
            "email": student.email,
        },
        "transaction_uuid": str(payment.esewa_transaction.transaction_uuid) if payment.esewa_transaction_id else str(payment.transaction_uuid),
        "amount": money(payment.amount),
        "method": payment.method,
        "status": payment.status,
        "gateway_reference": payment.gateway_reference or payment.transaction_reference,
        "transaction_reference": payment.transaction_reference,
        "error_message": payment.error_message,
        "created_at": payment.created_at,
        "updated_at": payment.updated_at,
    }


def esewa_signature(fields):
    signed_names = fields["signed_field_names"].split(",")
    message = ",".join(f"{name}={fields[name]}" for name in signed_names)
    digest = hmac.new(settings.ESEWA_SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def decode_gateway_data(value):
    try:
        padded = value + "=" * (-len(value) % 4)
        return json.loads(base64.b64decode(padded).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Invalid payment response.")


def transaction_data(item):
    return {
        "id": item.id,
        "fee": {
            "id": item.fee_id,
            "amount_due": money(item.fee.amount_due),
            "due_date": item.fee.due_date,
            "status": item.fee.status,
        },
        "student": {
            "id": item.student_id,
            "name": item.student.get_full_name() or item.student.email,
            "email": item.student.email,
        },
        "transaction_uuid": item.transaction_uuid,
        "amount": money(item.amount),
        "status": item.status,
        "esewa_transaction_code": item.esewa_transaction_code,
        "raw_response": item.raw_response,
        "created_at": item.created_at,
        "verified_at": item.verified_at,
    }


class FeeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Fee.objects.filter(center=request.user.center).select_related("student")
        if request.user.role == "student":
            queryset = queryset.filter(student=request.user)
        return Response([fee_data(fee) for fee in queryset])


class StudentFeeDetailView(APIView):
    permission_classes = [IsStudent]

    def get(self, request, pk):
        try:
            fee = Fee.objects.get(pk=pk, center=request.user.center, student=request.user)
        except Fee.DoesNotExist:
            return Response({"detail": "Fee not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(fee_data(fee))


class PaymentListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        queryset = Payment.objects.filter(fee__center=request.user.center).select_related("fee", "fee__student", "esewa_transaction")
        return Response([payment_data(payment) for payment in queryset])


class StudentPaymentListView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        payments = Payment.objects.filter(fee__center=request.user.center, fee__student=request.user).select_related("fee", "esewa_transaction")
        return Response([payment_data(item) for item in payments])


class StudentPaymentReceiptView(APIView):
    permission_classes = [IsStudent]

    def get(self, request, pk):
        try:
            payment = Payment.objects.select_related("fee", "esewa_transaction").get(pk=pk, fee__center=request.user.center, fee__student=request.user)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "receipt_number": f"TH-{payment.id:06d}",
            "payment": payment_data(payment),
            "student": request.user.get_full_name() or request.user.email,
            "fee": fee_data(payment.fee),
        })


class AdminEsewaTransactionListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        queryset = EsewaTransaction.objects.filter(center=request.user.center).select_related("student", "fee")
        if request.query_params.get("status"):
            queryset = queryset.filter(status=request.query_params["status"].upper())
        if request.query_params.get("student"):
            queryset = queryset.filter(student_id=request.query_params["student"])
        if request.query_params.get("date"):
            queryset = queryset.filter(created_at__date=request.query_params["date"])
        return Response([transaction_data(item) for item in queryset])


class EsewaInitiateView(APIView):
    permission_classes = [IsStudent]
    throttle_classes = [EsewaThrottle]

    def post(self, request, fee_id=None):
        try:
            fee = Fee.objects.get(id=fee_id or request.data.get("fee_id"), center=request.user.center, student=request.user)
        except Fee.DoesNotExist:
            return Response({"detail": "Fee not found."}, status=status.HTTP_404_NOT_FOUND)
        if not settings.ESEWA_PRODUCT_CODE or not settings.ESEWA_SECRET_KEY:
            return Response({"detail": "eSewa Sandbox is not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            amount = Decimal(str(request.data.get("amount", fee.balance))).quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError, ValueError):
            return Response({"detail": "Invalid payment amount."}, status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0 or amount > fee.balance:
            return Response({"detail": "Payment amount must be greater than zero and no more than the outstanding balance."}, status=status.HTTP_400_BAD_REQUEST)

        transaction_uuid = f"F{fee.pk}-{uuid.uuid4().hex[:16]}"
        item = EsewaTransaction.objects.create(
            center=fee.center, fee=fee, student=request.user,
            transaction_uuid=transaction_uuid, amount=amount,
        )
        fields = {
            "amount": money(amount),
            "tax_amount": "0",
            "product_service_charge": "0",
            "product_delivery_charge": "0",
            "total_amount": money(amount),
            "transaction_uuid": transaction_uuid,
            "product_code": settings.ESEWA_PRODUCT_CODE,
            "success_url": settings.ESEWA_SUCCESS_URL,
            "failure_url": settings.ESEWA_FAILURE_URL,
            "signed_field_names": "total_amount,transaction_uuid,product_code",
        }
        fields["signature"] = esewa_signature(fields)
        return Response({"form_url": settings.ESEWA_FORM_URL, "fields": fields, "transaction_uuid": transaction_uuid}, status=status.HTTP_201_CREATED)


class EsewaVerifyView(APIView):
    permission_classes = [IsStudent]
    throttle_classes = [EsewaThrottle]

    def post(self, request):
        try:
            payload = decode_gateway_data(request.data.get("data", ""))
            signed_names = payload["signed_field_names"].split(",")
            supplied_signature = payload["signature"]
            signature_fields = {"signed_field_names": payload["signed_field_names"], **payload}
            expected_signature = esewa_signature(signature_fields)
            if not hmac.compare_digest(supplied_signature, expected_signature):
                raise ValueError("Invalid payment response.")
            transaction_uuid = payload["transaction_uuid"]
            item = EsewaTransaction.objects.get(transaction_uuid=transaction_uuid, student=request.user, center=request.user.center)
        except (KeyError, ValueError, EsewaTransaction.DoesNotExist):
            return Response({"detail": "Unable to verify this payment."}, status=status.HTTP_400_BAD_REQUEST)

        if signed_names != ["total_amount", "transaction_uuid", "product_code"]:
            return Response({"detail": "Unable to verify this payment."}, status=status.HTTP_400_BAD_REQUEST)
        if payload.get("product_code") != settings.ESEWA_PRODUCT_CODE or payload.get("total_amount") != money(item.amount):
            return Response({"detail": "Unable to verify this payment."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = requests.get(settings.ESEWA_STATUS_URL, params={
                "product_code": settings.ESEWA_PRODUCT_CODE,
                "total_amount": money(item.amount),
                "transaction_uuid": item.transaction_uuid,
            }, timeout=10)
            response.raise_for_status()
            result = response.json()
        except (requests.RequestException, ValueError):
            return Response({"detail": "Unable to verify the payment with eSewa."}, status=status.HTTP_502_BAD_GATEWAY)

        if str(result.get("status", "")).upper() != "COMPLETE":
            return Response({"detail": "eSewa has not confirmed this payment yet.", "status": result.get("status", "PENDING")}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            locked_item = EsewaTransaction.objects.select_for_update().select_related("fee").get(pk=item.pk)
            locked_fee = Fee.objects.select_for_update().get(pk=locked_item.fee_id)
            if locked_item.status == EsewaTransaction.Status.COMPLETE:
                payment = Payment.objects.get(esewa_transaction=locked_item)
            else:
                if locked_item.amount > locked_fee.balance:
                    return Response({"detail": "The fee balance has changed. Payment was not applied."}, status=status.HTTP_409_CONFLICT)
                reference = str(result.get("refId") or result.get("transaction_code") or "")
                payment = Payment.objects.create(
                    fee=locked_fee, amount=locked_item.amount, status=Payment.Status.CONFIRMED,
                    product_code=settings.ESEWA_PRODUCT_CODE, method=Payment.Method.ONLINE,
                    esewa_transaction=locked_item, transaction_reference=reference,
                    gateway_reference=reference, initiated_by=None, received_by=None,
                )
                locked_item.status = EsewaTransaction.Status.COMPLETE
                locked_item.esewa_transaction_code = reference
                locked_item.raw_response = result
                locked_item.verified_at = timezone.now()
                locked_item.save(update_fields=["status", "esewa_transaction_code", "raw_response", "verified_at"])
                locked_fee.refresh_status()
            return Response({"payment": payment_data(payment), "fee": fee_data(locked_fee)})


class EsewaFailureView(APIView):
    permission_classes = [IsStudent]
    throttle_classes = [EsewaThrottle]

    def post(self, request):
        item = EsewaTransaction.objects.filter(transaction_uuid=request.data.get("transaction_uuid"), student=request.user, center=request.user.center).first()
        if not item:
            return Response({"detail": "Payment transaction not found."}, status=status.HTTP_404_NOT_FOUND)
        if item.status == EsewaTransaction.Status.INITIATED:
            item.status = EsewaTransaction.Status.CANCELED
            item.raw_response = {"result": "failure"}
            item.save(update_fields=["status", "raw_response"])
        return Response({"transaction": transaction_data(item)})
