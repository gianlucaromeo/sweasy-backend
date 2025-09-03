from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from dj_rest_auth.registration.views import (
    ResendEmailVerificationView,
    VerifyEmailView, 
)
from accounts.views import CustomRegisterView

def confirm_email_redirect(request, key):
    return redirect(f"http://localhost:3000/confirm-email?key={key}")

urlpatterns = [
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path(
        'api/v1/auth/account-confirm-email/',
        VerifyEmailView.as_view(),
        name='account_email_verification_sent'
    ),
    path(
        'api/v1/auth/registration/',
        CustomRegisterView.as_view(),
        name='rest_register'
    ),
    path(
        'api/v1/auth/registration/verify-email/',
        VerifyEmailView.as_view(),
        name='rest_verify_email'
    ),
    path(
        'api/v1/auth/registration/resend-email/',
        ResendEmailVerificationView.as_view(),
        name='rest_resend_email'
    ),
    re_path(
        r"^api/v1/auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$",
        confirm_email_redirect,
        name="account_confirm_email"
    ),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/admin/', admin.site.urls),
    path('api/v1/catalog/', include('catalog.urls')),
]
