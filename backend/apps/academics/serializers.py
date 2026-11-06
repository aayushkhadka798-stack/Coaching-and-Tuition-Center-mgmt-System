from rest_framework import serializers

from apps.accounts.models import User

from .models import Batch, BatchSchedule, Course, Enrollment


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "name", "description", "fee_amount", "is_active")
        read_only_fields = ("id",)


class BatchScheduleSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source="batch.name", read_only=True)
    course_name = serializers.CharField(source="batch.course.name", read_only=True)
    teacher_name = serializers.SerializerMethodField()

    def get_teacher_name(self, obj):
        return obj.batch.teacher.get_full_name() or obj.batch.teacher.email

    class Meta:
        model = BatchSchedule
        fields = ("id", "batch", "batch_name", "course_name", "teacher_name", "day_of_week", "start_time", "end_time", "room")
        read_only_fields = ("id",)

    def validate_batch(self, value):
        if value.center_id != self.context["request"].user.center_id:
            raise serializers.ValidationError("Batch must belong to your center.")
        return value


class BatchSerializer(serializers.ModelSerializer):
    schedules = BatchScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Batch
        fields = ("id", "course", "teacher", "name", "start_date", "end_date", "capacity", "is_active", "schedules")
        read_only_fields = ("id", "schedules")

    def validate(self, attrs):
        center = self.context["request"].user.center
        course = attrs.get("course", getattr(self.instance, "course", None))
        teacher = attrs.get("teacher", getattr(self.instance, "teacher", None))
        if course and course.center_id != center.id:
            raise serializers.ValidationError({"course": "Course must belong to your center."})
        if teacher and (teacher.center_id != center.id or teacher.role != User.Role.TEACHER):
            raise serializers.ValidationError({"teacher": "Teacher must belong to your center."})
        return attrs


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ("id", "student", "batch", "enrolled_on", "status")
        read_only_fields = ("id", "enrolled_on")

    def validate(self, attrs):
        center = self.context["request"].user.center
        student = attrs.get("student", getattr(self.instance, "student", None))
        batch = attrs.get("batch", getattr(self.instance, "batch", None))
        if student and (student.center_id != center.id or student.role != User.Role.STUDENT):
            raise serializers.ValidationError({"student": "Student must belong to your center."})
        if batch and batch.center_id != center.id:
            raise serializers.ValidationError({"batch": "Batch must belong to your center."})
        return attrs


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source="batch.course.name", read_only=True)
    batch_name = serializers.CharField(source="batch.name", read_only=True)
    teacher = serializers.SerializerMethodField()
    schedules = BatchScheduleSerializer(source="batch.schedules", many=True, read_only=True)

    class Meta:
        model = Enrollment
        fields = ("id", "batch", "batch_name", "course", "teacher", "start_date", "end_date", "status", "enrolled_on", "schedules")

    start_date = serializers.DateField(source="batch.start_date", read_only=True)
    end_date = serializers.DateField(source="batch.end_date", read_only=True)

    def get_teacher(self, obj):
        return {"id": obj.batch.teacher_id, "name": obj.batch.teacher.get_full_name() or obj.batch.teacher.email}