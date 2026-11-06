from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from apps.core.permissions import IsStudent
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notice, NoticeRead
from .serializers import StudentNoticeSerializer


class StudentNoticeListView(generics.ListAPIView):
    permission_classes = [IsStudent]
    serializer_class = StudentNoticeSerializer

    def get_queryset(self):
        user = self.request.user
        batch_ids = user.enrollments.filter(status="active").values("batch_id")
        return Notice.objects.filter(center=user.center).filter(
            Q(target_role=Notice.Target.ALL) | Q(target_role=Notice.Target.STUDENT),
            Q(batch__isnull=True) | Q(batch_id__in=batch_ids),
        ).select_related("batch").order_by("-created_at").distinct()


class StudentNoticeReadView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, pk):
        batch_ids = request.user.enrollments.filter(status="active").values("batch_id")
        notice = get_object_or_404(
            Notice.objects.filter(center=request.user.center).filter(
                Q(target_role=Notice.Target.ALL) | Q(target_role=Notice.Target.STUDENT),
                Q(batch__isnull=True) | Q(batch_id__in=batch_ids),
            ),
            pk=pk,
        )
        NoticeRead.objects.get_or_create(notice=notice, user=request.user, defaults={"read_at": timezone.now()})
        return Response({"detail": "Notice marked as read."}, status=status.HTTP_200_OK)