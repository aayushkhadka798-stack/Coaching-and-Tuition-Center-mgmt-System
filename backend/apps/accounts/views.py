from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiTypes

from apps.core.permissions import IsAdmin

from .models import User
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    TeacherCreateSerializer,
    UserSerializer,
    user_data,
)


class AuthThrottle(AnonRateThrottle):
    rate = "5/min"


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]
    admin_login = False

    @extend_schema(request=LoginSerializer, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        role = User.Role.ADMIN if self.admin_login else "non_admin"
        serializer = LoginSerializer(data=request.data, context={"role": role})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh), "user": user_data(user)})


class AdminLoginView(LoginView):
    admin_login = True


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={204: None})
    def post(self, request):
        try:
            RefreshToken(request.data["refresh"]).blacklist()
        except (KeyError, ValueError):
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        if not request.user.check_password(request.data.get("current_password", "")):
            return Response({"detail": "Current password is incorrect."}, status=400)
        serializer = __import__("django.contrib.auth.password_validation", fromlist=["validate_password"])
        try:
            serializer.validate_password(request.data.get("new_password", ""), request.user)
        except Exception as error:
            return Response({"detail": str(error)}, status=400)
        request.user.set_password(request.data["new_password"])
        request.user.save(update_fields=["password"])
        update_session_auth_hash(request, request.user)
        return Response({"detail": "Password changed successfully."})


class TeacherListCreateView(generics.ListCreateAPIView):
    serializer_class = TeacherCreateSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.filter(center=self.request.user.center, role=User.Role.TEACHER).select_related("teacher_profile")


class StudentListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.filter(center=self.request.user.center, role=User.Role.STUDENT)
