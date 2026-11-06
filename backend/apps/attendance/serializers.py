from rest_framework import serializers

from .models import Attendance


class StudentAttendanceSerializer(serializers.ModelSerializer):
    batch = serializers.CharField(source="enrollment.batch.name", read_only=True)
    batch_id = serializers.IntegerField(source="enrollment.batch_id", read_only=True)

    class Meta:
        model = Attendance
        fields = ("id", "batch", "batch_id", "date", "status")