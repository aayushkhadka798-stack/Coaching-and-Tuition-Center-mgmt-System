from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiTypes

from .permissions import IsAdmin, IsStudent, IsTeacher


class DashboardView(APIView):
    permission_classes = []
    role = ""

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        center = request.user.center
        if not center:
            return Response({"detail": "A center is required for dashboard data."}, status=400)

        from apps.accounts.models import User
        from apps.academics.models import Batch, Course, Enrollment

        students = User.objects.filter(center=center, role=User.Role.STUDENT, is_active=True)
        teachers = User.objects.filter(center=center, role=User.Role.TEACHER, is_active=True)
        courses = Course.objects.filter(center=center, is_active=True)
        batches = Batch.objects.filter(center=center, is_active=True)
        enrollments = Enrollment.objects.filter(center=center, status=Enrollment.Status.ACTIVE)

        if self.role == "admin":
            metrics = {
                "students": students.count(),
                "teachers": teachers.count(),
                "active_batches": batches.count(),
                "monthly_revenue": "0.00",
                "attendance_rate": None,
            }
            activity = []
            recent_users = User.objects.filter(
                center=center, role__in=[User.Role.STUDENT, User.Role.TEACHER]
            ).order_by("-date_joined")[:3]
            for user in recent_users:
                activity.append({
                    "title": f"{user.get_role_display()} account",
                    "detail": user.email,
                    "created_at": user.date_joined,
                })
        elif self.role == "teacher":
            teacher_batches = batches.filter(teacher=request.user)
            metrics = {
                "students": enrollments.filter(batch__teacher=request.user).values("student_id").distinct().count(),
                "teachers": None,
                "active_batches": teacher_batches.count(),
                "monthly_revenue": None,
                "attendance_rate": None,
            }
            activity = []
        else:
            student_enrollments = enrollments.filter(student=request.user)
            metrics = {
                "students": None,
                "teachers": None,
                "active_batches": student_enrollments.values("batch_id").distinct().count(),
                "monthly_revenue": None,
                "attendance_rate": None,
            }
            activity = []

        return Response(
            {
                "message": f"Welcome to the {self.role} dashboard.",
                "role": request.user.role,
                "center": center.name,
                "metrics": metrics,
                "activity": activity,
                "data_availability": {
                    "attendance": False,
                    "fees": False,
                    "payments": False,
                },
            }
        )


class AdminDashboardView(DashboardView):
    permission_classes = [IsAdmin]
    role = "admin"


class TeacherDashboardView(DashboardView):
    permission_classes = [IsTeacher]
    role = "teacher"


class StudentDashboardView(DashboardView):
    permission_classes = [IsStudent]
    role = "student"
