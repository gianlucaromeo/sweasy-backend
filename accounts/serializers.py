from django.contrib.auth import password_validation
from rest_framework import serializers
from .models import User
from django.db.models import Q, EmailField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.constants import (
    CODE_PASSWORDS_DO_NOT_MATCH,
    CODE_EMAIL_UNIQUE,
    ERR_EMAIL_UNIQUE,
    ERR_PASSWORDS_DO_NOT_MATCH,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "username"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


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
        extra_kwargs = {
            "email": {
                # Override to [], otherwise it will use UniqueValidator by 
                # default and will be called before validate_email
                "validators": [],
            },
        }

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

    # Custom validator for email to add a code
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                ERR_EMAIL_UNIQUE,
                code=CODE_EMAIL_UNIQUE,
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password1"],
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
