from django.urls import path

from .views import (
    AdminEsewaTransactionListView,
    EsewaFailureView,
    EsewaInitiateView,
    EsewaVerifyView,
    FeeListView,
    PaymentListView,
    StudentFeeDetailView,
    StudentPaymentListView,
    StudentPaymentReceiptView,
)

urlpatterns = [
    path("", FeeListView.as_view(), name="fees"),
    path("payments/", PaymentListView.as_view(), name="payments"),
    path("student/fees/", FeeListView.as_view(), name="student-fees"),
    path("student/fees/<int:pk>/", StudentFeeDetailView.as_view(), name="student-fee-detail"),
    path("student/payments/", StudentPaymentListView.as_view(), name="student-payments"),
    path("student/payments/<int:pk>/receipt/", StudentPaymentReceiptView.as_view(), name="student-payment-receipt"),
    path("payments/esewa/initiate/", EsewaInitiateView.as_view(), name="esewa-initiate"),
    path("<int:fee_id>/esewa/initiate/", EsewaInitiateView.as_view(), name="esewa-fee-initiate"),
    path("payments/esewa/verify/", EsewaVerifyView.as_view(), name="esewa-verify"),
    path("payments/esewa/failure/", EsewaFailureView.as_view(), name="esewa-failure"),
    path("admin/esewa-transactions/", AdminEsewaTransactionListView.as_view(), name="admin-esewa-transactions"),
]
