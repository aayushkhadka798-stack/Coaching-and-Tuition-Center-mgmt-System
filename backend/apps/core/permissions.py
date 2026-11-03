from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    required_role = None

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == self.required_role
        )


class IsAdmin(HasRole):
    required_role = "admin"


class IsTeacher(HasRole):
    required_role = "teacher"


class IsStudent(HasRole):
    required_role = "student"


class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {"admin", "teacher"}
        )
