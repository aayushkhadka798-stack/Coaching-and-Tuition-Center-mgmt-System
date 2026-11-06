from django.db import models


class Notice(models.Model):
    class Target(models.TextChoices):
        ALL = "all", "Everyone"
        TEACHER = "teacher", "Teachers"
        STUDENT = "student", "Students"

    center = models.ForeignKey("accounts.Center", on_delete=models.CASCADE, related_name="notices")
    title = models.CharField(max_length=200)
    body = models.TextField()
    target_role = models.CharField(max_length=20, choices=Target.choices, default=Target.ALL)
    batch = models.ForeignKey("academics.Batch", null=True, blank=True, on_delete=models.CASCADE, related_name="notices")
    posted_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="posted_notices")
    created_at = models.DateTimeField(auto_now_add=True)


class NoticeRead(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name="reads")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="notice_reads")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("notice", "user"), name="unique_notice_read")]
