from django.urls import path

from .views import EsewaInitiateView, EsewaVerifyView, FeeListView, PaymentListView

urlpatterns = [
    path("", FeeListView.as_view(), name="fees"),
    path("payments/", PaymentListView.as_view(), name="payments"),
    path("payments/esewa/initiate/", EsewaInitiateView.as_view(), name="esewa-initiate"),
    path("payments/esewa/verify/", EsewaVerifyView.as_view(), name="esewa-verify"),
]
