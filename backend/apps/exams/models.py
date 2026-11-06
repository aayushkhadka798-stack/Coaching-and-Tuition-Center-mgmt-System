from django.core.validators import MinValueValidator
from django.db import models


class Exam(models.Model):
    batch = models.ForeignKey("academics.Batch", on_delete=models.PROTECT, related_name="exams")
    title = models.CharField(max_length=150)
    exam_date = models.DateField()
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])


class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name="results")
    student = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="results")
    marks_obtained = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        constraints = [models.UniqueConstraint(fields=("exam", "student"), name="unique_result_per_student_exam")]

    @property
    def percentage(self):
        return round((self.marks_obtained / self.exam.total_marks) * 100, 2) if self.exam.total_marks else 0

    @property
    def grade(self):
        percentage = self.percentage
        return "A+" if percentage >= 90 else "A" if percentage >= 80 else "B+" if percentage >= 70 else "B" if percentage >= 60 else "C" if percentage >= 50 else "F"
