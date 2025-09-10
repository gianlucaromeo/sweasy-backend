import jwt

from django.db.utils import IntegrityError
from django.utils import timezone
from django.conf import settings
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import Response, status
from rest_framework_simplejwt.views import TokenObtainPairView
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

    def __is_missing_required(self, field: str, detail: dict) -> bool:
        if field in detail:
            if "required" in detail[field][0].code:
                return True
        return False

    def __is_not_unique(self, field: str, detail: dict) -> bool:
        if field in detail:
            if "unique" in detail[field][0].code:
                return True
        return False

    def __code_400(self, code):
        return Response(
            {"code": code},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def __created_details_201(self, detail: str) -> Response:
        return Response(
            {"detail": detail},
            status=status.HTTP_201_CREATED,
        )

    def __unhandled_exception_details_400(self, detail: str) -> Response:
        return Response(
            data={"detail": detail},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def __handle_validation_error(
        self,
        err: serializers.ValidationError,
    ) -> Response:
        detail = err.detail if isinstance(err.detail, dict) else {}

        required_fields = [
            {"field": "username", "code": CODE_USERNAME_REQUIRED},
            {"field": "email", "code": CODE_EMAIL_REQUIRED},
            {"field": "password1", "code": CODE_PASSWORD1_REQUIRED},
            {"field": "password2", "code": CODE_PASSWORD2_REQUIRED},
        ]

        for field in required_fields:
            if self.__is_missing_required(field["field"], detail):
                return self.__code_400(field["code"])

        # USERNAME is not unique
        if self.__is_not_unique("username", detail):
            return self.__code_400(CODE_USERNAME_UNIQUE)

        # EMAIL is not unique
        if self.__is_not_unique("email", detail):
            return self.__created_details_201(GENERIC_REGISTRATION_MSG)

        if "non_field_errors" in detail:
            for error in detail["non_field_errors"]:
                # Passwords do not match
                if CODE_PASSWORDS_DO_NOT_MATCH in error.code:
                    return self.__code_400(CODE_PASSWORDS_DO_NOT_MATCH)

        # Other
        print("Unhandled validation error:", str(err))
        return self.__unhandled_exception_details_400(GENERIC_REGISTRATION_ERR_MSG)

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

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            # Should be when unique constraint is violated
            print("Integrity error:", str(e))
            return self.__handle_integrity_error(e)
        except serializers.ValidationError as e:
            return self.__handle_validation_error(e)
        except Exception as e:
            print("Unhandled exception:", str(e))
            return self.__unhandled_exception_details_400(GENERIC_REGISTRATION_ERR_MSG)


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
