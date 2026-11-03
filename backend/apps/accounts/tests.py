from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Center, User


class AccountsTests(APITestCase):
    def setUp(self):
        self.center = Center.objects.create(name="Main Center", code="MAIN")

    def test_registration_forces_student_role(self):
        response = self.client.post(
            reverse("register"),
            {
                "center_code": "main",
                "first_name": "A",
                "last_name": "Student",
                "email": "student@example.com",
                "password": "Strong-password-123",
                "password2": "Strong-password-123",
                "role": "admin",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.get(email="student@example.com").role, User.Role.STUDENT)

    def test_admin_cannot_use_regular_login(self):
        User.objects.create_user(email="admin@example.com", password="Strong-password-123", role="admin", center=self.center)
        response = self.client.post(reverse("login"), {"email": "admin@example.com", "password": "Strong-password-123"})
        self.assertEqual(response.status_code, 400)
