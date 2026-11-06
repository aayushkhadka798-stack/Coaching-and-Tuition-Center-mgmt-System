from rest_framework import generics
from apps.core.permissions import IsStudent

from .models import Result
from .serializers import StudentResultSerializer


class StudentResultListView(generics.ListAPIView):
    permission_classes = [IsStudent]
    serializer_class = StudentResultSerializer

    def get_queryset(self):
        return Result.objects.filter(student=self.request.user, exam__batch__center=self.request.user.center).select_related("exam")


class StudentReportCardView(StudentResultListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get("batch"):
            queryset = queryset.filter(exam__batch_id=self.request.query_params["batch"])
        return queryset