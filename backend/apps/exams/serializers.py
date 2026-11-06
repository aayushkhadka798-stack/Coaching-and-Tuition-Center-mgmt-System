from rest_framework import serializers

from .models import Result


class StudentResultSerializer(serializers.ModelSerializer):
    exam = serializers.CharField(source="exam.title", read_only=True)
    exam_date = serializers.DateField(source="exam.exam_date", read_only=True)
    total_marks = serializers.DecimalField(source="exam.total_marks", max_digits=8, decimal_places=2, read_only=True)
    percentage = serializers.ReadOnlyField()
    grade = serializers.ReadOnlyField()

    class Meta:
        model = Result
        fields = ("id", "exam", "exam_date", "total_marks", "marks_obtained", "percentage", "grade")