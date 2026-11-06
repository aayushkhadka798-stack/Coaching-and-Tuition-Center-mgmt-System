from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

from apps.accounts.views import (
    StudentListView,
    TeacherDetailView,
    TeacherListCreateView,
    TeacherPasswordResetView,
)
from apps.core.dashboard import AdminDashboardView, StudentDashboardView, TeacherDashboardView
from apps.attendance.views import StudentAttendanceSummaryView, StudentAttendanceView
from apps.academics.views import StudentEnrollmentViewSet, StudentTimetableView
from apps.exams.views import StudentReportCardView, StudentResultListView
from apps.fees.views import (
    AdminEsewaTransactionListView,
    EsewaFailureView,
    EsewaVerifyView,
    FeeListView,
    StudentFeeDetailView,
    StudentPaymentListView,
    StudentPaymentReceiptView,
)
from apps.notices.views import StudentNoticeListView, StudentNoticeReadView
from apps.accounts.views import ProfileView

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/", include("apps.core.urls")),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/teachers/", TeacherListCreateView.as_view()),
    path("api/teachers/<int:pk>/", TeacherDetailView.as_view()),
    path("api/teachers/<int:pk>/reset-password/", TeacherPasswordResetView.as_view()),
    path("api/students/", StudentListView.as_view()),
    path("api/admin/dashboard/", AdminDashboardView.as_view()),
    path("api/teacher/dashboard/", TeacherDashboardView.as_view()),
    path("api/student/dashboard/", StudentDashboardView.as_view()),
    path("api/student/profile/", ProfileView.as_view()),
    path("api/student/enrollments/", StudentEnrollmentViewSet.as_view({"get": "list"})),
    path("api/student/timetable/", StudentTimetableView.as_view()),
    path("api/student/attendance/", StudentAttendanceView.as_view()),
    path("api/student/attendance/summary/", StudentAttendanceSummaryView.as_view()),
    path("api/student/fees/", FeeListView.as_view()),
    path("api/student/fees/<int:pk>/", StudentFeeDetailView.as_view()),
    path("api/student/payments/", StudentPaymentListView.as_view()),
    path("api/student/payments/<int:pk>/receipt/", StudentPaymentReceiptView.as_view()),
    path("api/student/results/", StudentResultListView.as_view()),
    path("api/student/results/report-card/", StudentReportCardView.as_view()),
    path("api/student/notices/", StudentNoticeListView.as_view()),
    path("api/student/notices/<int:pk>/read/", StudentNoticeReadView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/academics/", include("apps.academics.urls")),
    path("api/attendance/", include("apps.attendance.urls")),
    path("api/fees/", include("apps.fees.urls")),
    path("api/payments/esewa/verify/", EsewaVerifyView.as_view()),
    path("api/payments/esewa/failure/", EsewaFailureView.as_view()),
    path("api/admin/esewa-transactions/", AdminEsewaTransactionListView.as_view()),
    path("api/exams/", include("apps.exams.urls")),
    path("api/notices/", include("apps.notices.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
