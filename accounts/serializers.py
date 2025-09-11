from django.contrib.auth import password_validation
from django.db import transaction
from rest_framework import serializers
from .models import User
from django.db.models import Q
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.constants import (
    CODE_PASSWORDS_DO_NOT_MATCH,
    ERR_PASSWORDS_DO_NOT_MATCH,
)


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, trim_whitespace=False)
    password2 = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
        ]

    def validate(self, attrs):
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")
        if password1 != password2:
            raise serializers.ValidationError(
                ERR_PASSWORDS_DO_NOT_MATCH,
                code=CODE_PASSWORDS_DO_NOT_MATCH,
            )
        password_validation.validate_password(password1)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password1")
        validated_data.pop("password2")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=password,
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            is_active=False,
            email_verified_at=None,
        )
        return user


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        identifier = attrs.get("username")  # username or email
        password = attrs.get("password")

        if not identifier or not password:
            raise serializers.ValidationError(
                "Username/email and password are required."
            )

        try:
            user = User.objects.get(
                Q(username__iexact=identifier) | Q(email__iexact=identifier)
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        # Optional gate: require verified email if you track it
        if not user.email_verified_at:
            raise serializers.ValidationError("Email not verified")

        # Hand off to parent with the real username, as expected by the base class
        data = super().validate(
            {
                "username": user.get_username(),
                "password": password,
            }
        )

        return data
