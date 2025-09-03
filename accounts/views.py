from django.db import transaction
from django.db.utils import IntegrityError
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import IsAuthenticated
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import User
from .serializers import UserSerializer
from .constants import *


@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "users": reverse("user-list", request=request, format=format),
        }
    )


class CustomRegisterView(RegisterView):
    def __is_missing_required(self, field: str, detail: dict) -> bool:
        if field in detail:
            if "required" in detail[field][0].code:
                return True
        return False

    def __required_details_400(self, detail, code):
        return Response(
            {"detail": detail, "code": code},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def __created_details_201(self, detail):
        return Response(
            {"detail": detail},
            status=status.HTTP_201_CREATED,
        )

    def __unhandled_exception_details_400(self, detail):
        return Response(
            data={"detail": detail},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            super().create(request, *args, **kwargs)
        except IntegrityError as exc:
            if "UNIQUE constraint failed: accounts_user.email" in str(exc):
                return self.__created_details_201(GENERIC_REGISTRATION_MSG)
            if "UNIQUE constraint failed: accounts_user.username" in str(exc):
                return self.__created_details_201(GENERIC_REGISTRATION_MSG)

            print("Unhandled IntegrityError", exc)
            return self.__unhandled_exception_details_400(GENERIC_ERR_MSG)
        except ValidationError as exc:
            detail = exc.detail if isinstance(exc.detail, dict) else {}

            # Required fields
            if self.__is_missing_required("email", detail):
                return self.__required_details_400(
                    ERR_EMAIL_REQUIRED, CODE_EMAIL_REQUIRED
                )
            if self.__is_missing_required("username", detail):
                return self.__required_details_400(
                    ERR_USERNAME_REQUIRED, CODE_USERNAME_REQUIRED
                )
            if self.__is_missing_required("password1", detail):
                return self.__required_details_400(
                    ERR_PASSWORD1_REQUIRED, CODE_PASSWORD1_REQUIRED
                )
            if self.__is_missing_required("password2", detail):
                return self.__required_details_400(
                    ERR_PASSWORD2_REQUIRED, CODE_PASSWORD2_REQUIRED
                )

            # This handles also duplicates fields
            return self.__created_details_201(GENERIC_REGISTRATION_MSG)
        except Exception as exc:
            print("Unhandled exception: ", exc)
            return self.__unhandled_exception_details_400(GENERIC_ERR_MSG)

        return self.__created_details_201(GENERIC_REGISTRATION_MSG)


class DestroyMeView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        request.user.is_active = False
        request.user.save(update_fields=["is_active"])
        return Response(
            data={"detail": DESTROY_ME_MSG},
            status=status.HTTP_204_NO_CONTENT,
        )


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
