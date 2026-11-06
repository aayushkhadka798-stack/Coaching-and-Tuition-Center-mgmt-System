from django.db import models


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"

    enrollment = models.ForeignKey("academics.Enrollment", on_delete=models.PROTECT, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices)
    marked_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="marked_attendance")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("enrollment", "date"), name="unique_attendance_per_day")]
        indexes = [models.Index(fields=("enrollment", "date")), models.Index(fields=("date", "status"))]
