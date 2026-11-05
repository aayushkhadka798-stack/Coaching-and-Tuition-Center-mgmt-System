from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from smtplib import SMTPException
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import secrets
import string
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiTypes

from apps.core.permissions import IsAdmin

from .models import Center, PasswordResetOTP, StudentProfile, User
from .services.google_auth import GoogleTokenError, verify_google_credential
from .serializers import (
    LoginSerializer,
    GoogleLoginSerializer,
    RegisterSerializer,
    TeacherCreateSerializer,
    TeacherPasswordResetSerializer,
    TeacherReadSerializer,
    TeacherUpdateSerializer,
    UserSerializer,
    StudentAdminSerializer,
    user_data,
    ProfileSerializer,
    ChangePasswordSerializer,
)


class AuthThrottle(AnonRateThrottle):
    rate = "5/min"


class GoogleAuthThrottle(AnonRateThrottle):
    rate = "10/min"


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


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [GoogleAuthThrottle]

    @extend_schema(request=GoogleLoginSerializer, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = verify_google_credential(serializer.validated_data["credential"])
        except GoogleTokenError:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

        email = payload["email"].strip().lower()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = None

        if user:
            if not user.is_active or user.role == User.Role.ADMIN:
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
            if user.google_id and user.google_id != payload["sub"]:
                return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
            if not user.google_id:
                user.google_id = payload["sub"]
                user.save(update_fields=["google_id"])
            return Response(_google_tokens(user))

        center_code = serializer.validated_data.get("center_code", "").strip().upper()
        if not center_code:
            return Response(
                {
                    "needs_center_code": True,
                    "email": email,
                    "first_name": payload.get("given_name", ""),
                    "last_name": payload.get("family_name", ""),
                }
            )
        try:
            center = Center.objects.get(code__iexact=center_code, is_active=True)
        except Center.DoesNotExist:
            return Response({"center_code": "Invalid or inactive center code."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = User(
                email=email,
                first_name=payload.get("given_name", "")[:150],
                last_name=payload.get("family_name", "")[:150],
                role=User.Role.STUDENT,
                center=center,
                google_id=payload["sub"],
            )
            user.set_unusable_password()
            user.save()
            StudentProfile.objects.create(user=user)
        return Response(_google_tokens(user), status=status.HTTP_201_CREATED)


def _google_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh), "user": user_data(user)}


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
        return Response(UserSerializer(request.user, context={"request": request}).data)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        return {"request": self.request}


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(request.data["new_password"])
        request.user.save(update_fields=["password"])
        update_session_auth_hash(request, request.user)
        return Response({"detail": "Password changed successfully."})


def _send_otp(user, purpose):
    code = f"{secrets.randbelow(1000000):06d}"
    send_mail(
        "Your CoachingHub verification code",
        f"Your verification code is {code}. It expires in 10 minutes.",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    PasswordResetOTP.objects.filter(email__iexact=user.email, purpose=purpose, used_at__isnull=True).update(
        used_at=timezone.now()
    )
    PasswordResetOTP.objects.create(
        email=user.email.lower(),
        code_hash=make_password(code),
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=10),
    )


class ForgotPasswordRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            try:
                _send_otp(user, "forgot_password")
            except (SMTPException, OSError):
                return Response({"detail": "Unable to send the verification email."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"detail": "If an active account exists, a verification code has been sent."})


class ForgotPasswordResetView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        code = str(request.data.get("otp", "")).strip()
        password = request.data.get("new_password")
        password2 = request.data.get("new_password2")
        if password != password2:
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
        if not password or len(code) != 6:
            return Response({"detail": "A valid verification code and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
        if password != request.data.get("new_password2"):
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
        record = PasswordResetOTP.objects.filter(
            email__iexact=email, purpose="forgot_password", used_at__isnull=True
        ).order_by("-created_at").first()
        if not record or record.expires_at <= timezone.now():
            return Response({"detail": "The verification code is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
        if record.attempts >= 5:
            return Response({"detail": "Too many verification attempts."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        record.attempts += 1
        record.save(update_fields=["attempts"])
        if not check_password(code, record.code_hash):
            return Response({"detail": "The verification code is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if not user:
            return Response({"detail": "The verification code is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(password, user)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save(update_fields=["password"])
        record.used_at = timezone.now()
        record.save(update_fields=["used_at"])
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh), "user": user_data(user)})


class ChangePasswordRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.check_password(request.data.get("current_password", "")):
            return Response({"detail": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            _send_otp(request.user, "change_password")
        except (SMTPException, OSError):
            return Response({"detail": "Unable to send the verification email."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"detail": "A verification code has been sent to your email."})


class ChangePasswordConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = str(request.data.get("otp", "")).strip()
        password = request.data.get("new_password")
        record = PasswordResetOTP.objects.filter(
            email__iexact=request.user.email, purpose="change_password", used_at__isnull=True
        ).order_by("-created_at").first()
        if not record or record.expires_at <= timezone.now() or record.attempts >= 5:
            return Response({"detail": "The verification code is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
        record.attempts += 1
        record.save(update_fields=["attempts"])
        if not check_password(code, record.code_hash):
            return Response({"detail": "The verification code is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(password, request.user)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(password)
        request.user.save(update_fields=["password"])
        record.used_at = timezone.now()
        record.save(update_fields=["used_at"])
        return Response({"detail": "Password changed successfully."})


class TeacherListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    filterset_fields = ["is_active"]
    search_fields = ["first_name", "last_name", "email", "phone", "teacher_profile__qualification", "teacher_profile__specialization"]
    ordering_fields = ["first_name", "last_name", "email", "date_joined", "is_active"]
    ordering = ["first_name", "last_name"]

    def get_queryset(self):
        return User.objects.filter(center=self.request.user.center, role=User.Role.TEACHER).select_related("teacher_profile")

    def get_serializer_class(self):
        return TeacherCreateSerializer if self.request.method == "POST" else TeacherReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = TeacherCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()
        response = TeacherReadSerializer(teacher).data
        response["temporary_password"] = getattr(teacher, "_temporary_password", None)
        return Response(response, status=status.HTTP_201_CREATED)


class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return User.objects.filter(center=self.request.user.center, role=User.Role.TEACHER).select_related("teacher_profile")

    def get_serializer_class(self):
        if self.request.method in {"PATCH", "PUT"}:
            return TeacherUpdateSerializer
        return TeacherReadSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", {})
        kwargs["context"]["user"] = self.get_object()
        return super().get_serializer(*args, **kwargs)

    def perform_destroy(self, instance):
        batches = getattr(instance, "batches", None)
        if batches is not None and batches.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Teacher cannot be deleted while assigned to batches."})
        instance.delete()


class TeacherPasswordResetView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        teacher = User.objects.filter(
            pk=pk, center=request.user.center, role=User.Role.TEACHER
        ).first()
        if teacher is None:
            return Response({"detail": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TeacherPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.get("password")
        if not password:
            password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(14))
        teacher.set_password(password)
        teacher.save(update_fields=["password"])
        return Response({"detail": "Password reset successfully.", "temporary_password": password})


class StudentListView(generics.ListCreateAPIView):
    serializer_class = StudentAdminSerializer
    permission_classes = [IsAdmin]
    search_fields = ["first_name", "last_name", "email", "phone", "student_profile__roll_no"]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        return User.objects.filter(center=self.request.user.center, role=User.Role.STUDENT).select_related("student_profile")

    def perform_create(self, serializer):
        serializer.save()


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentAdminSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.filter(center=self.request.user.center, role=User.Role.STUDENT).select_related("student_profile")
