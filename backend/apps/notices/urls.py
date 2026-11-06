from django.urls import path

from .views import StudentNoticeListView, StudentNoticeReadView

urlpatterns = [
    path("student/notices/", StudentNoticeListView.as_view()),
    path("student/notices/<int:pk>/read/", StudentNoticeReadView.as_view()),
]
