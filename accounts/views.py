import jwt

from django.utils import timezone
from django.conf import settings
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts._exceptions import registration_exception_handler
from accounts.constants import *
from .models import User
from .serializers import RegisterSerializer, LoginSerializer
from django.core.mail import send_mail
from .utils import (
    decode_and_validate_email_verification_token,
    generate_email_verification_token,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    
    def get_exception_handler(self):
        return registration_exception_handler

    def perform_create(self, serializer):
        serializer.save()

        token = generate_email_verification_token(serializer.instance.id)

        # Send email-verification email.
        # TODO: Remove hardcoded strings and use real URL
        send_mail(
            "Subject here",
            "Here is the token: " + token,
            settings.DEFAULT_FROM_EMAIL,
            [serializer.validated_data["email"]],
            fail_silently=False,
        )


class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response(
                {"code": CODE_TOKEN_REQUIRED},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            claims = decode_and_validate_email_verification_token(token)
        except jwt.InvalidTokenError:
            return Response(
                {"code": CODE_INVALID_OR_EXPIRED_TOKEN},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=claims["sub"])
        except User.DoesNotExist:
            return Response(
                {"code": CODE_USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.email_verified_at:
            user.email_verified_at = timezone.now()
            user.is_active = True
            user.save(update_fields=["email_verified_at", "is_active"])

            return Response(
                {"detail": MSG_EMAIL_VERIFIED},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": MSG_EMAIL_ALREADY_VERIFIED},
            status=status.HTTP_200_OK,
        )


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
