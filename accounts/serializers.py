from django.contrib.auth import password_validation
from rest_framework import serializers
from .models import User
from django.db.models import Q
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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

    def validate(self, attrs):
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")
        if password1 != password2:
            raise serializers.ValidationError("Passwords do not match.")
        password_validation.validate_password(password1)
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password1"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
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
        # if hasattr(user, "email_verified") and not user.email_verified:
        #     raise serializers.ValidationError("Email not verified")

        # Hand off to parent with the real username, as expected by the base class
        data = super().validate(
            {
                "username": user.get_username(),
                "password": password,
            }
        )

        return data
