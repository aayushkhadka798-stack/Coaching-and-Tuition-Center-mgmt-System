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


class TeacherCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    qualification = serializers.CharField(max_length=150, required=False, allow_blank=True)
    specialization = serializers.CharField(max_length=150, required=False, allow_blank=True)

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
            key: validated_data.pop(key, "")
            for key in ("qualification", "specialization")
        }
        password = validated_data.pop("password")
        user = User.objects.create_user(
            password=password,
            role=User.Role.TEACHER,
            center=self.context["request"].user.center,
            **validated_data,
        )
        TeacherProfile.objects.create(user=user, **profile_fields)
        return user


class UserSerializer(serializers.ModelSerializer):
    center = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "center", "phone")

    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_center(self, obj):
        return {"id": obj.center_id, "name": obj.center.name, "code": obj.center.code} if obj.center_id else None
