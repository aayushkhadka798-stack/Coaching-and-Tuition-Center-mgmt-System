from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_user_profile_photo")]
    operations = [
        migrations.CreateModel(
            name="PasswordResetOTP",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254)),
                ("code_hash", models.CharField(max_length=128)),
                ("purpose", models.CharField(max_length=30)),
                ("expires_at", models.DateTimeField()),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"indexes": [models.Index(fields=["email", "purpose", "created_at"], name="accounts_pa_email_9e03d1_idx")]},
        ),
    ]
