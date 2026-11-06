from rest_framework import serializers

from .models import Notice


class StudentNoticeSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    batch_name = serializers.CharField(source="batch.name", read_only=True)

    class Meta:
        model = Notice
        fields = ("id", "title", "body", "target_role", "batch", "batch_name", "created_at", "is_read")

    def get_is_read(self, obj):
        return obj.reads.filter(user=self.context["request"].user).exists()