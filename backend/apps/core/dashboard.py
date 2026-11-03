from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiTypes

from .permissions import IsAdmin, IsStudent, IsTeacher


class DashboardView(APIView):
    permission_classes = []
    role = ""

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        return Response(
            {
                "message": f"Welcome to the {self.role} dashboard.",
                "role": request.user.role,
                "center": request.user.center.name,
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
