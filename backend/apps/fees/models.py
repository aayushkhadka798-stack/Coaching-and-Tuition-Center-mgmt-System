import uuid

from django.core.validators import MinValueValidator
from django.db import models


class Fee(models.Model):
    class Status(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PARTIAL = "partial", "Partial"
        PAID = "paid", "Paid"

    center = models.ForeignKey("accounts.Center", on_delete=models.CASCADE, related_name="fees")
    student = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="fees")
    enrollment = models.ForeignKey("academics.Enrollment", on_delete=models.PROTECT, related_name="fees")
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def paid_amount(self):
        return self.payments.filter(status=Payment.Status.CONFIRMED).aggregate(
            total=models.Sum("amount")
        )["total"] or 0

    @property
    def balance(self):
        return max(self.amount_due - self.paid_amount, 0)

    def refresh_status(self):
        paid = self.paid_amount
        self.status = self.Status.PAID if paid >= self.amount_due else self.Status.PARTIAL if paid else self.Status.UNPAID
        self.save(update_fields=["status"])

    class Meta:
        indexes = [models.Index(fields=("center", "status", "due_date")), models.Index(fields=("student", "status"))]


class Payment(models.Model):
    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELED = "canceled", "Canceled"
        FAILED = "failed", "Failed"
        ERROR = "error", "Error"

    fee = models.ForeignKey(Fee, on_delete=models.PROTECT, related_name="payments")
    transaction_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
    product_code = models.CharField(max_length=100)
    gateway_reference = models.CharField(max_length=150, blank=True)
    error_message = models.TextField(blank=True)
    initiated_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="initiated_payments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=("status", "created_at")), models.Index(fields=("fee", "status"))]
