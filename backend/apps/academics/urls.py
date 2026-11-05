from rest_framework.routers import DefaultRouter

from .views import BatchScheduleViewSet, BatchViewSet, CourseViewSet, EnrollmentViewSet, StudentEnrollmentViewSet

router = DefaultRouter()
router.register("courses", CourseViewSet)
router.register("batches", BatchViewSet)
router.register("schedules", BatchScheduleViewSet)
router.register("enrollments", EnrollmentViewSet)
router.register("my-enrollments", StudentEnrollmentViewSet, basename="my-enrollment")
urlpatterns = router.urls
