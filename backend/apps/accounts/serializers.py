import secrets
import string

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Center, StudentProfile, TeacherProfile, User


def user_data(user):
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "center": {"id": user.center_id, "name": user.center.name, "code": user.center.code}
        if user.center_id
        else None,
    }


class RegisterSerializer(serializers.Serializer):
    center_code = serializers.CharField(max_length=20, write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        validate_password(attrs["password"])
        if User.objects.filter(email__iexact=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "An account with this email already exists."})
        try:
            center = Center.objects.get(code=attrs["center_code"].strip().upper(), is_active=True)
        except Center.DoesNotExist:
            raise serializers.ValidationError({"center_code": "Invalid or inactive center code."})
        attrs["center"] = center
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("password2")
        validated_data.pop("center_code", None)
        center = validated_data.pop("center")
        password = validated_data.pop("password")
        user = User.objects.create_user(
            password=password, role=User.Role.STUDENT, center=center, **validated_data
        )
        StudentProfile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs["email"], password=attrs["password"])
        if not user or not user.is_active or (
            self.context["role"] == "non_admin" and user.role == User.Role.ADMIN
        ) or (self.context["role"] == User.Role.ADMIN and user.role != User.Role.ADMIN):
            raise serializers.ValidationError("Invalid credentials.")
        attrs["user"] = user
        return attrs


class GoogleLoginSerializer(serializers.Serializer):
    credential = serializers.CharField(write_only=True, trim_whitespace=True)
    center_code = serializers.CharField(max_length=20, required=False, allow_blank=True)


class TeacherCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    qualification = serializers.CharField(max_length=150, required=False, allow_blank=True)
    specialization = serializers.CharField(max_length=150, required=False, allow_blank=True)
    joined_date = serializers.DateField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False, default=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        profile_fields = {
            key: validated_data.pop(key, None if key == "joined_date" else "")
            for key in ("qualification", "specialization", "joined_date")
        }
        is_active = validated_data.pop("is_active", True)
        password = validated_data.pop("password", None)
        if not password:
            password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(14))
        user = User.objects.create_user(
            password=password,
            role=User.Role.TEACHER,
            center=self.context["request"].user.center,
            **validated_data,
        )
        user.is_active = is_active
        user.save(update_fields=["is_active"])
        TeacherProfile.objects.create(user=user, **profile_fields)
        user._temporary_password = password
        return user


class TeacherReadSerializer(serializers.ModelSerializer):
    qualification = serializers.CharField(source="teacher_profile.qualification", read_only=True)
    specialization = serializers.CharField(source="teacher_profile.specialization", read_only=True)
    joined_date = serializers.DateField(source="teacher_profile.joined_date", read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "email", "first_name", "last_name", "phone",
            "qualification", "specialization", "joined_date", "is_active",
        )


class TeacherUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    qualification = serializers.CharField(max_length=150, required=False, allow_blank=True)
    specialization = serializers.CharField(max_length=150, required=False, allow_blank=True)
    joined_date = serializers.DateField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)

    def validate_email(self, value):
        user = self.context["user"]
        if User.objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def update(self, instance, validated_data):
        profile_fields = {
            key: validated_data.pop(key)
            for key in ("qualification", "specialization", "joined_date")
            if key in validated_data
        }
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if validated_data:
            instance.save(update_fields=list(validated_data))
        if profile_fields:
            profile, _ = TeacherProfile.objects.get_or_create(user=instance)
            for key, value in profile_fields.items():
                setattr(profile, key, value)
            profile.save(update_fields=list(profile_fields))
        return instance


class TeacherPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(required=False, write_only=True)

    def validate_password(self, value):
        validate_password(value)
        return value


class UserSerializer(serializers.ModelSerializer):
    center = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "center", "phone", "profile_photo")

    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_center(self, obj):
        return {"id": obj.center_id, "name": obj.center.name, "code": obj.center.code} if obj.center_id else None

    def get_profile_photo(self, obj):
        if not obj.profile_photo:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.profile_photo.url) if request else obj.profile_photo.url


class ProfileSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    qualification = serializers.CharField(source="teacher_profile.qualification", required=False, allow_blank=True)
    specialization = serializers.CharField(source="teacher_profile.specialization", required=False, allow_blank=True)
    joined_date = serializers.DateField(source="teacher_profile.joined_date", required=False, allow_null=True)
    guardian_name = serializers.CharField(source="student_profile.guardian_name", required=False, allow_blank=True)
    guardian_phone = serializers.CharField(source="student_profile.guardian_phone", required=False, allow_blank=True)
    address = serializers.CharField(source="student_profile.address", required=False, allow_blank=True)
    date_of_birth = serializers.DateField(source="student_profile.date_of_birth", required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id", "email", "first_name", "last_name", "phone", "role", "center",
            "profile_photo", "qualification", "specialization", "joined_date",
            "guardian_name", "guardian_phone", "address", "date_of_birth",
        )
        read_only_fields = ("id", "email", "role", "center")

    center = serializers.SerializerMethodField()

    def get_center(self, obj):
        return {"id": obj.center_id, "name": obj.center.name, "code": obj.center.code} if obj.center_id else None

    def validate_profile_photo(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Profile photo must be 5 MB or smaller.")
        if value.content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise serializers.ValidationError("Use a JPG, PNG, or WebP image.")
        return value

    def update(self, instance, validated_data):
        teacher_data = validated_data.pop("teacher_profile", {})
        student_data = validated_data.pop("student_profile", {})
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if validated_data:
            instance.save(update_fields=list(validated_data))
        if teacher_data and instance.role == User.Role.TEACHER:
            profile, _ = TeacherProfile.objects.get_or_create(user=instance)
            for key, value in teacher_data.items():
                setattr(profile, key, value)
            profile.save(update_fields=list(teacher_data))
        if student_data and instance.role == User.Role.STUDENT:
            profile, _ = StudentProfile.objects.get_or_create(user=instance)
            for key, value in student_data.items():
                setattr(profile, key, value)
            profile.save(update_fields=list(student_data))
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "Passwords do not match."})
        validate_password(attrs["new_password"], user)
        return attrs


class StudentAdminSerializer(serializers.ModelSerializer):
    roll_no = serializers.CharField(source="student_profile.roll_no", read_only=True)
    guardian_name = serializers.CharField(source="student_profile.guardian_name", required=False, allow_blank=True)
    guardian_phone = serializers.CharField(source="student_profile.guardian_phone", required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "is_active", "roll_no", "guardian_name", "guardian_phone")
        read_only_fields = ("id", "roll_no")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exclude(pk=getattr(self.instance, "pk", None)).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        profile_data = validated_data.pop("student_profile", {})
        password = profile_data.pop("password", None) or "ChangeMe123!"
        user = User.objects.create_user(password=password, role=User.Role.STUDENT, center=self.context["request"].user.center, **validated_data)
        StudentProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("student_profile", {})
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if validated_data:
            instance.save(update_fields=list(validated_data))
        if profile_data:
            profile = instance.student_profile
            for key, value in profile_data.items():
                setattr(profile, key, value)
            profile.save(update_fields=list(profile_data))
        return instance
