from django.urls import reverse
from rest_framework.test import APITestCase

from apps.academics.models import Batch, Course

from .models import Center, TeacherProfile, User


class TeacherAdminTests(APITestCase):
    def setUp(self):
        self.center = Center.objects.create(name="Main Center", code="MAIN")
        self.other_center = Center.objects.create(name="Other Center", code="OTHER")
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="Strong-password-123",
            role=User.Role.ADMIN,
            center=self.center,
        )
        self.other_admin = User.objects.create_user(
            email="other-admin@example.com",
            password="Strong-password-123",
            role=User.Role.ADMIN,
            center=self.other_center,
        )

    def teacher_payload(self, email="teacher@example.com"):
        return {
            "first_name": "Tara",
            "last_name": "Teacher",
            "email": email,
            "password": "Strong-password-123",
            "qualification": "MSc",
            "specialization": "Mathematics",
        }

    def test_admin_can_create_teacher_and_teacher_can_log_in(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/teachers/", self.teacher_payload())
        self.assertEqual(response.status_code, 201, response.data)
        teacher = User.objects.get(email="teacher@example.com")
        self.assertEqual(teacher.center, self.center)
        self.assertEqual(teacher.role, User.Role.TEACHER)
        self.assertTrue(TeacherProfile.objects.filter(user=teacher).exists())

        self.client.force_authenticate(None)
        login = self.client.post(reverse("login"), {
            "email": teacher.email,
            "password": "Strong-password-123",
        })
        self.assertEqual(login.status_code, 200, login.data)
        self.assertEqual(login.data["user"]["role"], User.Role.TEACHER)

    def test_teacher_endpoints_require_admin(self):
        teacher = User.objects.create_user(
            email="teacher@example.com",
            password="Strong-password-123",
            role=User.Role.TEACHER,
            center=self.center,
        )
        self.client.force_authenticate(teacher)
        response = self.client.get("/api/teachers/")
        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_see_other_center_teachers(self):
        other_teacher = User.objects.create_user(
            email="other-teacher@example.com",
            password="Strong-password-123",
            role=User.Role.TEACHER,
            center=self.other_center,
        )
        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/teachers/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(other_teacher.id, [row["id"] for row in response.data["results"]])
        detail = self.client.get(f"/api/teachers/{other_teacher.id}/")
        self.assertEqual(detail.status_code, 404)

    def test_delete_assigned_teacher_returns_conflict(self):
        self.client.force_authenticate(self.admin)
        create = self.client.post("/api/teachers/", self.teacher_payload())
        teacher = User.objects.get(pk=create.data["id"])
        course = Course.objects.create(center=self.center, name="Math")
        Batch.objects.create(
            center=self.center,
            course=course,
            teacher=teacher,
            name="Morning Math",
            start_date="2026-01-01",
        )
        response = self.client.delete(f"/api/teachers/{teacher.id}/")
        self.assertEqual(response.status_code, 409, response.data)
        self.assertTrue(User.objects.filter(pk=teacher.id).exists())

    def test_other_center_admin_cannot_edit_teacher(self):
        teacher = User.objects.create_user(
            email="teacher@example.com",
            password="Strong-password-123",
            role=User.Role.TEACHER,
            center=self.center,
        )
        self.client.force_authenticate(self.other_admin)
        response = self.client.patch(f"/api/teachers/{teacher.id}/", {"first_name": "Changed"})
        self.assertEqual(response.status_code, 404)
