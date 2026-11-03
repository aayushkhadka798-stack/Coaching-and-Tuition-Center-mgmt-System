class CenterScopedQuerysetMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated or user.center_id is None:
            return queryset.none()
        return queryset.filter(center_id=user.center_id)
