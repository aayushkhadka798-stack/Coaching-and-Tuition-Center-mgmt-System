from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.accounts.views import StudentListView, TeacherListCreateView
from apps.core.dashboard import AdminDashboardView, StudentDashboardView, TeacherDashboardView

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/", include("apps.core.urls")),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/teachers/", TeacherListCreateView.as_view()),
    path("api/students/", StudentListView.as_view()),
    path("api/admin/dashboard/", AdminDashboardView.as_view()),
    path("api/teacher/dashboard/", TeacherDashboardView.as_view()),
    path("api/student/dashboard/", StudentDashboardView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/academics/", include("apps.academics.urls")),
    path("api/attendance/", include("apps.attendance.urls")),
    path("api/fees/", include("apps.fees.urls")),
    path("api/exams/", include("apps.exams.urls")),
    path("api/notices/", include("apps.notices.urls")),
]
