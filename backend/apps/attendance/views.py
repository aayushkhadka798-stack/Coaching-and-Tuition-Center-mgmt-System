from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsStudent

from .models import Attendance
from .serializers import StudentAttendanceSerializer


class StudentAttendanceView(generics.ListAPIView):
    permission_classes = [IsStudent]
    serializer_class = StudentAttendanceSerializer

    def get_queryset(self):
        queryset = Attendance.objects.filter(enrollment__student=self.request.user).select_related("enrollment__batch")
        if self.request.query_params.get("batch"):
            queryset = queryset.filter(enrollment__batch_id=self.request.query_params["batch"])
        if self.request.query_params.get("month"):
            year, month = self.request.query_params["month"].split("-")
            queryset = queryset.filter(date__year=year, date__month=month)
        return queryset.order_by("-date")


class StudentAttendanceSummaryView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        rows = Attendance.objects.filter(enrollment__student=request.user).values(
            "enrollment__batch_id", "enrollment__batch__name"
        ).annotate(
            present=Count("id", filter=Q(status=Attendance.Status.PRESENT)),
            late=Count("id", filter=Q(status=Attendance.Status.LATE)),
            absent=Count("id", filter=Q(status=Attendance.Status.ABSENT)),
            total=Count("id"),
        )
        results = [{
            "batch_id": row["enrollment__batch_id"],
            "batch": row["enrollment__batch__name"],
            "present": row["present"],
            "late": row["late"],
            "absent": row["absent"],
            "total": row["total"],
            "percentage": round(((row["present"] + row["late"]) / row["total"]) * 100, 2) if row["total"] else 0,
        } for row in rows]
        return Response({"count": len(results), "next": None, "previous": None, "results": results})