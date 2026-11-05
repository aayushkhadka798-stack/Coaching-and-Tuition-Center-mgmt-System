from rest_framework import viewsets

from apps.core.permissions import IsAdmin, IsAdminOrTeacher, IsStudent

from .models import Batch, BatchSchedule, Course, Enrollment
from .serializers import BatchScheduleSerializer, BatchSerializer, CourseSerializer, EnrollmentSerializer


class CenterScopedViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.queryset.filter(center=self.request.user.center)


class CourseViewSet(CenterScopedViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdmin]
    search_fields = ["name", "description"]
    filterset_fields = ["is_active"]
    ordering_fields = ["name", "fee_amount", "created_at"]
    ordering = ["name"]

    def perform_create(self, serializer):
        serializer.save(center=self.request.user.center)


class BatchViewSet(CenterScopedViewSet):
    queryset = Batch.objects.select_related("course", "teacher")
    serializer_class = BatchSerializer
    permission_classes = [IsAdminOrTeacher]
    search_fields = ["name", "course__name", "teacher__email"]
    filterset_fields = ["course", "teacher", "is_active"]
    ordering_fields = ["name", "start_date", "capacity"]
    ordering = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset if self.request.user.role == "admin" else queryset.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(center=self.request.user.center)


class BatchScheduleViewSet(viewsets.ModelViewSet):
    queryset = BatchSchedule.objects.select_related("batch")
    serializer_class = BatchScheduleSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        queryset = self.queryset.filter(batch__center=self.request.user.center)
        return queryset if self.request.user.role == "admin" else queryset.filter(batch__teacher=self.request.user)


class EnrollmentViewSet(CenterScopedViewSet):
    queryset = Enrollment.objects.select_related("student", "batch")
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAdminOrTeacher]
    search_fields = ["student__email", "student__first_name", "student__last_name", "batch__name"]
    filterset_fields = ["student", "batch", "status"]
    ordering_fields = ["enrolled_on", "status"]
    ordering = ["-enrolled_on"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset if self.request.user.role == "admin" else queryset.filter(batch__teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(center=self.request.user.center)


class StudentEnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Enrollment.objects.filter(center=self.request.user.center, student=self.request.user).select_related("batch", "batch__course")