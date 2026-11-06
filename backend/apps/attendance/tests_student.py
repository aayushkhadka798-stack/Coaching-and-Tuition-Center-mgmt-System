from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Center, User
from apps.academics.models import Batch, Course, Enrollment

from .models import Attendance


class StudentAttendanceAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        center = Center.objects.create(name="Center", code="ATT")
        self.student = User.objects.create_user("student@att.test", password="Password123!", role=User.Role.STUDENT, center=center)
        teacher = User.objects.create_user("teacher@att.test", password="Password123!", role=User.Role.TEACHER, center=center)
        course = Course.objects.create(center=center, name="Science", fee_amount=0)
        batch = Batch.objects.create(center=center, course=course, teacher=teacher, name="Morning", start_date=date.today())
        enrollment = Enrollment.objects.create(center=center, student=self.student, batch=batch)
        Attendance.objects.create(enrollment=enrollment, date=date.today(), status=Attendance.Status.PRESENT, marked_by=teacher)

    def test_student_sees_only_own_attendance_and_summary(self):
        self.client.force_authenticate(self.student)
        response = self.client.get("/api/student/attendance/")
        summary = self.client.get("/api/student/attendance/summary/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(summary.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(summary.data["results"][0]["percentage"], 100.0)

    def test_non_student_is_forbidden(self):
        teacher = User.objects.get(email="teacher@att.test")
        self.client.force_authenticate(teacher)
        self.assertEqual(self.client.get("/api/student/attendance/").status_code, 403)
