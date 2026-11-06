from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import BatchScheduleViewSet, BatchViewSet, CourseViewSet, EnrollmentViewSet, StudentEnrollmentViewSet, StudentTimetableView

router = DefaultRouter()
router.register("courses", CourseViewSet)
router.register("batches", BatchViewSet)
router.register("schedules", BatchScheduleViewSet)
router.register("enrollments", EnrollmentViewSet)
router.register("my-enrollments", StudentEnrollmentViewSet, basename="my-enrollment")
urlpatterns = router.urls
urlpatterns += [
    path("student/enrollments/", StudentEnrollmentViewSet.as_view({"get": "list"})),
    path("student/timetable/", StudentTimetableView.as_view()),
]
