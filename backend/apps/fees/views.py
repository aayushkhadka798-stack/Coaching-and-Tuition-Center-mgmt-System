import base64
import hashlib
import hmac
from decimal import Decimal
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin, IsStudent

from .models import Fee, Payment


def fee_data(fee):
    return {
        "id": fee.id,
        "student": {"id": fee.student_id, "email": fee.student.email},
        "amount_due": str(fee.amount_due),
        "paid_amount": str(fee.paid_amount),
        "balance": str(fee.balance),
        "due_date": fee.due_date,
        "status": fee.status,
    }


def payment_data(payment):
    return {
        "id": payment.id,
        "fee": payment.fee_id,
        "transaction_uuid": str(payment.transaction_uuid),
        "amount": str(payment.amount),
        "status": payment.status,
        "gateway_reference": payment.gateway_reference,
        "error_message": payment.error_message,
        "created_at": payment.created_at,
        "updated_at": payment.updated_at,
    }


def esewa_signature(total_amount, transaction_uuid, product_code):
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    digest = hmac.new(settings.ESEWA_SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


class FeeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Fee.objects.filter(center=request.user.center).select_related("student")
        if request.user.role == "student":
            queryset = queryset.filter(student=request.user)
        return Response([fee_data(fee) for fee in queryset])


class PaymentListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        queryset = Payment.objects.filter(fee__center=request.user.center).select_related("fee", "fee__student")
        return Response([payment_data(payment) for payment in queryset])


class EsewaInitiateView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        try:
            fee = Fee.objects.get(id=request.data.get("fee_id"), center=request.user.center, student=request.user)
        except Fee.DoesNotExist:
            return Response({"detail": "Fee not found."}, status=status.HTTP_404_NOT_FOUND)
        if not settings.ESEWA_PRODUCT_CODE or not settings.ESEWA_SECRET_KEY:
            return Response({"detail": "eSewa Sandbox is not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            amount = Decimal(str(request.data.get("amount", fee.balance)))
        except Exception:
            return Response({"detail": "Invalid payment amount."}, status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0 or amount > fee.balance:
            return Response({"detail": "Payment amount must be greater than zero and no more than the outstanding balance."}, status=status.HTTP_400_BAD_REQUEST)
        payment = Payment.objects.create(
            fee=fee, amount=amount, product_code=settings.ESEWA_PRODUCT_CODE,
            initiated_by=request.user, status=Payment.Status.PENDING,
        )
        fields = {
            "amount": str(amount), "tax_amount": "0", "total_amount": str(amount),
            "transaction_uuid": str(payment.transaction_uuid), "product_code": settings.ESEWA_PRODUCT_CODE,
            "product_service_charge": "0", "product_delivery_charge": "0",
            "success_url": request.data.get("success_url", ""),
            "failure_url": request.data.get("failure_url", ""),
            "signed_field_names": "total_amount,transaction_uuid,product_code",
            "signature": esewa_signature(amount, payment.transaction_uuid, settings.ESEWA_PRODUCT_CODE),
        }
        return Response({"payment": payment_data(payment), "gateway_url": settings.ESEWA_GATEWAY_URL, "fields": fields}, status=status.HTTP_201_CREATED)


class EsewaVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        transaction_uuid = request.data.get("transaction_uuid")
        try:
            payment = Payment.objects.select_related("fee").get(transaction_uuid=transaction_uuid, fee__center=request.user.center)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment transaction not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role == "student" and payment.fee.student_id != request.user.id:
            return Response({"detail": "Payment transaction not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            query = urlencode({"product_code": payment.product_code, "total_amount": str(payment.amount), "transaction_uuid": str(payment.transaction_uuid)})
            gateway_response = requests.get(f"{settings.ESEWA_STATUS_URL}?{query}", timeout=10)
            gateway_response.raise_for_status()
            result = gateway_response.json()
        except (requests.RequestException, ValueError):
            payment.status = Payment.Status.ERROR
            payment.error_message = "Unable to verify the transaction with eSewa."
            payment.save(update_fields=["status", "error_message", "updated_at"])
            return Response({"detail": payment.error_message, "payment": payment_data(payment)}, status=status.HTTP_502_BAD_GATEWAY)

        gateway_status = str(result.get("status", "")).upper()
        if gateway_status == "COMPLETE":
            with transaction.atomic():
                payment.status = Payment.Status.CONFIRMED
                payment.gateway_reference = str(result.get("refId", ""))
                payment.error_message = ""
                payment.save(update_fields=["status", "gateway_reference", "error_message", "updated_at"])
                payment.fee.refresh_status()
        elif gateway_status in {"CANCELED", "CANCELLED"}:
            payment.status = Payment.Status.CANCELED
            payment.error_message = "Payment was canceled in eSewa."
            payment.save(update_fields=["status", "error_message", "updated_at"])
        else:
            payment.status = Payment.Status.FAILED
            payment.error_message = result.get("message", "eSewa did not confirm this payment.")
            payment.save(update_fields=["status", "error_message", "updated_at"])
        return Response({"payment": payment_data(payment), "fee": fee_data(payment.fee)})