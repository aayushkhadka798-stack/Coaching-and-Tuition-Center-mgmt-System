from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0003_user_profile_photo"), ("academics", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Fee",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount_due", models.DecimalField(decimal_places=2, max_digits=12)),
                ("due_date", models.DateField()),
                ("status", models.CharField(choices=[("unpaid", "Unpaid"), ("partial", "Partial"), ("paid", "Paid")], default="unpaid", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("center", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fees", to="accounts.center")),
                ("enrollment", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="fees", to="academics.enrollment")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="fees", to="accounts.user")),
            ],
            options={"indexes": [models.Index(fields=["center", "status", "due_date"], name="fees_fee_center__d4f1d4_idx"), models.Index(fields=["student", "status"], name="fees_fee_student_4b1f26_idx")]},
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transaction_uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(choices=[("initiated", "Initiated"), ("pending", "Pending"), ("confirmed", "Confirmed"), ("canceled", "Canceled"), ("failed", "Failed"), ("error", "Error")], default="initiated", max_length=20)),
                ("product_code", models.CharField(max_length=100)),
                ("gateway_reference", models.CharField(blank=True, max_length=150)),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("fee", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payments", to="fees.fee")),
                ("initiated_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="initiated_payments", to="accounts.user")),
            ],
            options={"ordering": ["-created_at"], "indexes": [models.Index(fields=["status", "created_at"], name="fees_paymen_status_6a8a43_idx"), models.Index(fields=["fee", "status"], name="fees_paymen_fee_id_1a5d5a_idx")]},
        ),
    ]
