from django.urls import path

from .views import StudentReportCardView, StudentResultListView

urlpatterns = [
    path("student/results/", StudentResultListView.as_view()),
    path("student/results/report-card/", StudentReportCardView.as_view()),
]
