from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ChangePasswordView,
    AdminLoginView,
    GoogleLoginView,
    LoginView,
    LogoutView,
    MeView,
    ProfileView,
    RegisterView,
    StudentListView,
    TeacherListCreateView,
    TeacherDetailView,
    TeacherPasswordResetView,
    StudentDetailView,
    ForgotPasswordRequestView,
    ForgotPasswordResetView,
    ChangePasswordRequestView,
    ChangePasswordConfirmView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("admin/login/", AdminLoginView.as_view(), name="admin-login"),
    path("google/", GoogleLoginView.as_view(), name="google-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("password/forgot/request/", ForgotPasswordRequestView.as_view(), name="forgot-password-request"),
    path("password/forgot/reset/", ForgotPasswordResetView.as_view(), name="forgot-password-reset"),
    path("password/change/request/", ChangePasswordRequestView.as_view(), name="change-password-request"),
    path("password/change/confirm/", ChangePasswordConfirmView.as_view(), name="change-password-confirm"),
    path("teachers/", TeacherListCreateView.as_view(), name="teachers"),
    path("teachers/<int:pk>/", TeacherDetailView.as_view(), name="teacher-detail"),
    path("teachers/<int:pk>/reset-password/", TeacherPasswordResetView.as_view(), name="teacher-reset-password"),
    path("students/", StudentListView.as_view(), name="students"),
    path("students/<int:pk>/", StudentDetailView.as_view(), name="student-detail"),
]
