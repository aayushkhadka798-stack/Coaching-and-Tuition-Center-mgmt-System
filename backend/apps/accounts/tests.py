from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO
from rest_framework.test import APITestCase

from .models import Center, User


class AccountsTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.center = Center.objects.create(name="Main Center", code="MAIN")
        self.other_center = Center.objects.create(name="Other Center", code="OTHER")

    def google_payload(self, **overrides):
        payload = {
            "iss": "https://accounts.google.com",
            "email_verified": True,
            "email": "google@example.com",
            "sub": "google-sub-1",
            "given_name": "Google",
            "family_name": "User",
        }
        payload.update(overrides)
        return payload

    @patch("apps.accounts.services.google_auth.id_token.verify_oauth2_token")
    def test_invalid_google_token_is_rejected(self, verify):
        verify.side_effect = ValueError()
        response = self.client.post(reverse("google-login"), {"credential": "bad"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Invalid credentials.")

    @patch("apps.accounts.services.google_auth.id_token.verify_oauth2_token")
    def test_unverified_google_email_is_rejected(self, verify):
        verify.return_value = self.google_payload(email_verified=False)
        response = self.client.post(reverse("google-login"), {"credential": "unverified"})
        self.assertEqual(response.status_code, 400)

    @patch("apps.accounts.views.verify_google_credential")
    def test_existing_student_is_linked_and_logged_in(self, verify):
        verify.return_value = self.google_payload()
        user = User.objects.create_user(email="google@example.com", password="Strong-password-123", center=self.center)
        response = self.client.post(reverse("google-login"), {"credential": "valid"})
        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.google_id, "google-sub-1")
        self.assertEqual(response.data["user"]["role"], User.Role.STUDENT)

    @patch("apps.accounts.views.verify_google_credential")
    def test_existing_teacher_can_log_in_with_google(self, verify):
        verify.return_value = self.google_payload(email="teacher@example.com", sub="teacher-sub")
        User.objects.create_user(email="teacher@example.com", password="Strong-password-123", role=User.Role.TEACHER, center=self.center)
        response = self.client.post(reverse("google-login"), {"credential": "valid"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["role"], User.Role.TEACHER)

    @patch("apps.accounts.views.verify_google_credential")
    def test_admin_email_is_rejected(self, verify):
        verify.return_value = self.google_payload(email="admin@example.com")
        User.objects.create_user(email="admin@example.com", password="Strong-password-123", role=User.Role.ADMIN, center=self.center)
        response = self.client.post(reverse("google-login"), {"credential": "valid"})
        self.assertEqual(response.status_code, 400)

    @patch("apps.accounts.views.verify_google_credential")
    def test_new_email_without_center_returns_center_step(self, verify):
        verify.return_value = self.google_payload()
        response = self.client.post(reverse("google-login"), {"credential": "valid"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["needs_center_code"])
        self.assertFalse(User.objects.filter(email="google@example.com").exists())

    @patch("apps.accounts.views.verify_google_credential")
    def test_new_email_with_center_creates_student(self, verify):
        verify.return_value = self.google_payload()
        response = self.client.post(reverse("google-login"), {"credential": "valid", "center_code": "main"})
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="google@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertEqual(user.center, self.center)
        self.assertEqual(user.google_id, "google-sub-1")
        self.assertFalse(user.has_usable_password())

    @patch("apps.accounts.views.verify_google_credential")
    def test_invalid_or_inactive_center_is_rejected(self, verify):
        verify.return_value = self.google_payload()
        response = self.client.post(reverse("google-login"), {"credential": "valid", "center_code": "wrong"})
        self.assertEqual(response.status_code, 400)
        self.center.is_active = False
        self.center.save(update_fields=["is_active"])
        response = self.client.post(reverse("google-login"), {"credential": "valid", "center_code": "main"})
        self.assertEqual(response.status_code, 400)

    @patch("apps.accounts.views.verify_google_credential")
    def test_role_in_request_is_ignored(self, verify):
        verify.return_value = self.google_payload()
        response = self.client.post(reverse("google-login"), {"credential": "valid", "center_code": "MAIN", "role": "admin"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.get(email="google@example.com").role, User.Role.STUDENT)

    @patch("apps.accounts.views.verify_google_credential")
    def test_mismatched_google_id_is_rejected(self, verify):
        verify.return_value = self.google_payload()
        User.objects.create_user(email="google@example.com", password="Strong-password-123", center=self.center, google_id="different-sub")
        response = self.client.post(reverse("google-login"), {"credential": "valid"})
        self.assertEqual(response.status_code, 400)

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

    def profile_image(self):
        stream = BytesIO()
        Image.new("RGB", (4, 4), "blue").save(stream, format="PNG")
        return SimpleUploadedFile("avatar.png", stream.getvalue(), content_type="image/png")

    def test_authenticated_user_can_update_profile_and_photo(self):
        teacher = User.objects.create_user(
            email="profile-teacher@example.com",
            password="Strong-password-123",
            role=User.Role.TEACHER,
            center=self.center,
        )
        self.client.force_authenticate(teacher)
        response = self.client.patch(
            reverse("profile"),
            {"first_name": "Updated", "phone": "9800000000", "profile_photo": self.profile_image()},
            format="multipart",
        )
        self.assertEqual(response.status_code, 200, response.data)
        teacher.refresh_from_db()
        self.assertEqual(teacher.first_name, "Updated")
        self.assertTrue(teacher.profile_photo)

    def test_authenticated_user_can_change_password(self):
        student = User.objects.create_user(
            email="profile-student@example.com",
            password="Strong-password-123",
            role=User.Role.STUDENT,
            center=self.center,
        )
        self.client.force_authenticate(student)
        response = self.client.post(reverse("change-password"), {
            "current_password": "Strong-password-123",
            "new_password": "New-strong-password-123",
            "new_password2": "New-strong-password-123",
        })
        self.assertEqual(response.status_code, 200)
        student.refresh_from_db()
        self.assertTrue(student.check_password("New-strong-password-123"))

    def admin_client(self, center=None):
        admin = User.objects.create_user(
            email=f"admin-{center.code if center else 'main'}@example.com",
            password="Strong-password-123",
            role=User.Role.ADMIN,
            center=center or self.center,
        )
        self.client.force_authenticate(admin)

    def test_admin_teacher_crud_is_center_scoped_and_generates_password(self):
        self.admin_client()
        response = self.client.post(reverse("teachers"), {
            "first_name": "Ada", "last_name": "Lovelace", "email": "ada@example.com",
            "specialization": "Mathematics",
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["temporary_password"])
        teacher = User.objects.get(email="ada@example.com")
        self.assertEqual(teacher.center, self.center)
        self.assertTrue(teacher.teacher_profile)

        response = self.client.patch(reverse("teacher-detail", args=[teacher.pk]), {"is_active": False})
        self.assertEqual(response.status_code, 200)
        teacher.refresh_from_db()
        self.assertFalse(teacher.is_active)
        response = self.client.patch(reverse("teacher-detail", args=[teacher.pk]), {"is_active": True})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("teacher-reset-password", args=[teacher.pk]), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["temporary_password"])
        teacher.refresh_from_db()
        self.assertTrue(teacher.check_password(response.data["temporary_password"]))
        self.client.force_authenticate(None)
        login = self.client.post(reverse("login"), {"email": teacher.email, "password": response.data["temporary_password"]})
        self.assertEqual(login.status_code, 200, login.data)
        self.assertEqual(login.data["user"]["role"], User.Role.TEACHER)

    def test_teacher_api_rejects_non_admin_and_cross_center_access(self):
        teacher = User.objects.create_user(
            email="teacher@example.com", password="Strong-password-123",
            role=User.Role.TEACHER, center=self.center,
        )
        other_teacher = User.objects.create_user(
            email="other@example.com", password="Strong-password-123",
            role=User.Role.TEACHER, center=self.other_center,
        )
        self.client.force_authenticate(teacher)
        self.assertEqual(self.client.get(reverse("teachers")).status_code, 403)
        self.admin_client(self.center)
        self.assertEqual(self.client.get(reverse("teacher-detail", args=[other_teacher.pk])).status_code, 404)
