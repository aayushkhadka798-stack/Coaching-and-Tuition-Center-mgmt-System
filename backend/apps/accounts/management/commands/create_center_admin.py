from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from decouple import config

from apps.accounts.models import Center


class Command(BaseCommand):
    help = "Create a center and its admin account."

    def add_arguments(self, parser):
        for name in ("center-name", "center-code", "email", "password"):
            parser.add_argument(f"--{name}")

    def handle(self, *args, **options):
        values = {}
        prompts = {
            "center-name": "Center name: ",
            "center-code": "Center code: ",
            "email": "Admin email: ",
            "password": "Admin password: ",
        }
        for key, prompt in prompts.items():
            env_key = {
                "center-name": "CENTER_NAME",
                "center-code": "CENTER_CODE",
                "email": "ADMIN_EMAIL",
                "password": "ADMIN_PASSWORD",
            }[key]
            option_key = key.replace("-", "_")
            values[key] = options.get(option_key) or config(env_key, default="") or input(prompt)
        if Center.objects.filter(code=values["center-code"].upper()).exists():
            raise CommandError("A center with this code already exists.")
        User = get_user_model()
        if User.objects.filter(email__iexact=values["email"]).exists():
            raise CommandError("An account with this email already exists.")
        center = Center.objects.create(name=values["center-name"], code=values["center-code"])
        User.objects.create_user(
            email=values["email"],
            password=values["password"],
            role=User.Role.ADMIN,
            center=center,
            is_staff=True,
        )
        self.stdout.write(self.style.SUCCESS(f"Created admin for {center}."))
