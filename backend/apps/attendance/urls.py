from django.urls import path

from .views import StudentAttendanceSummaryView, StudentAttendanceView

urlpatterns = [
    path("student/attendance/", StudentAttendanceView.as_view()),
    path("student/attendance/summary/", StudentAttendanceSummaryView.as_view()),
]
