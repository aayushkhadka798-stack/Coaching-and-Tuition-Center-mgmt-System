from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models import Center, User


class Course(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name="courses")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("center", "name"), name="unique_course_per_center")]
        indexes = [models.Index(fields=("center", "is_active"))]


class Batch(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name="batches")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="batches")
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, related_name="batches")
    name = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    capacity = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("center", "name"), name="unique_batch_per_center")]
        indexes = [models.Index(fields=("center", "teacher", "is_active"))]

    def clean(self):
        if self.course_id and self.course.center_id != self.center_id:
            raise ValidationError({"course": "Course must belong to the same center."})
        if self.teacher_id and (self.teacher.center_id != self.center_id or self.teacher.role != User.Role.TEACHER):
            raise ValidationError({"teacher": "Teacher must belong to the same center."})
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot be before start date."})


class BatchSchedule(models.Model):
    class Day(models.IntegerChoices):
        SUNDAY = 0, "Sunday"
        MONDAY = 1, "Monday"
        TUESDAY = 2, "Tuesday"
        WEDNESDAY = 3, "Wednesday"
        THURSDAY = 4, "Thursday"
        FRIDAY = 5, "Friday"
        SATURDAY = 6, "Saturday"

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.PositiveSmallIntegerField(choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=100, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("batch", "day_of_week", "start_time"), name="unique_batch_schedule")]
        indexes = [models.Index(fields=("day_of_week", "start_time", "end_time"))]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be after start time."})
        conflicts = BatchSchedule.objects.filter(
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk).filter(batch__center=self.batch.center)
        if self.room:
            conflicts = conflicts.filter(room=self.room)
        else:
            conflicts = conflicts.filter(batch__teacher=self.batch.teacher)
        if conflicts.exists():
            raise ValidationError("This schedule overlaps an existing teacher or room slot.")


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        DROPPED = "dropped", "Dropped"

    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name="enrollments")
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, related_name="enrollments")
    enrolled_on = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("student", "batch"),
                condition=models.Q(status="active"),
                name="unique_active_student_batch",
            )
        ]
        indexes = [models.Index(fields=("center", "student", "status")), models.Index(fields=("center", "batch", "status"))]

    def clean(self):
        if self.student.center_id != self.center_id or self.student.role != User.Role.STUDENT:
            raise ValidationError({"student": "Student must belong to the same center."})
        if self.batch.center_id != self.center_id:
            raise ValidationError({"batch": "Batch must belong to the same center."})
        if self.status == self.Status.ACTIVE and self.batch.enrollments.filter(status=self.Status.ACTIVE).exclude(pk=self.pk).count() >= self.batch.capacity:
            raise ValidationError({"batch": "This batch has reached capacity."})
