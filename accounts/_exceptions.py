from rest_framework.views import exception_handler as drf_handler
from rest_framework.response import Response
from rest_framework import status

from accounts.constants import (
    CODE_USERNAME_REQUIRED,
    CODE_EMAIL_REQUIRED,
    CODE_PASSWORD1_REQUIRED,
    CODE_PASSWORD2_REQUIRED,
    CODE_USERNAME_UNIQUE,
    CODE_EMAIL_UNIQUE,
    CODE_PASSWORDS_DO_NOT_MATCH,
)


def registration_exception_handler(exc, ctx):
    resp = drf_handler(exc, ctx)
    if resp is None or not isinstance(resp.data, dict):
        print("Resp is None or not isinstance(resp.data, dict):", resp)
        return resp

    data = resp.data

    def is_required(e):
        return getattr(e, "code", "") == "required"

    def is_unique(e, attr_name="unique"):
        return getattr(e, "code", "") == attr_name

    required_fields = {
        "username": CODE_USERNAME_REQUIRED,
        "email": CODE_EMAIL_REQUIRED,
        "password1": CODE_PASSWORD1_REQUIRED,
        "password2": CODE_PASSWORD2_REQUIRED,
    }

    for field, code in required_fields.items():
        if any(is_required(e) for e in data.get(field, [])):
            return Response({"code": code}, status=status.HTTP_400_BAD_REQUEST)

    # Username unique returns 400
    if any(is_unique(e) for e in data.get("username", [])):
        return Response(
            {"code": CODE_USERNAME_UNIQUE},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Email unique returns 201 to avoid enumeration
    if any(is_unique(e) for e in data.get("email", [])):
        return Response(
            {"code": CODE_EMAIL_UNIQUE},
            status=status.HTTP_201_CREATED,
        )

    if "non_field_errors" in data:
        for error in data["non_field_errors"]:
            if CODE_PASSWORDS_DO_NOT_MATCH in error.code:
                return Response(
                    {"code": CODE_PASSWORDS_DO_NOT_MATCH},
                    status=status.HTTP_400_BAD_REQUEST,
                )

    return resp
