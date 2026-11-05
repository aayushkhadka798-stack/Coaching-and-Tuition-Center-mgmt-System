from django.urls import reverse
from rest_framework.test import APITestCase

from apps.accounts.models import Center, User

from .models import Course


class AcademicsApiTests(APITestCase):
    def setUp(self):
        self.center = Center.objects.create(name="Center A", code="A")
        self.other_center = Center.objects.create(name="Center B", code="B")
        self.admin = User.objects.create_user(email="admin@a.test", password="Strong-password-123", role="admin", center=self.center)
        self.teacher = User.objects.create_user(email="teacher@a.test", password="Strong-password-123", role="teacher", center=self.center)
        self.other_teacher = User.objects.create_user(email="teacher@b.test", password="Strong-password-123", role="teacher", center=self.other_center)

    def test_course_create_sets_center_and_isolation(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/academics/courses/", {"name": "Mathematics", "fee_amount": "1200.00"})
        self.assertEqual(response.status_code, 201)
        course = Course.objects.get(name="Mathematics")
        self.assertEqual(course.center, self.center)
        Course.objects.create(center=self.other_center, name="Physics")
        self.assertEqual(self.client.get("/api/academics/courses/").data["count"], 1)

    def test_teacher_cannot_manage_courses_or_other_center_batch_data(self):
        self.client.force_authenticate(self.teacher)
        self.assertEqual(self.client.get("/api/academics/courses/").status_code, 403)
        self.assertEqual(self.client.post("/api/academics/courses/", {"name": "Blocked"}).status_code, 403)

    def test_batch_rejects_cross_center_course_or_teacher(self):
        course = Course.objects.create(center=self.center, name="Math")
        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/academics/batches/", {
            "course": course.id, "teacher": self.other_teacher.id, "name": "Cross center",
            "start_date": "2026-01-01", "capacity": 20,
        })
        self.assertEqual(response.status_code, 400)