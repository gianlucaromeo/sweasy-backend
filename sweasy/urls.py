from django.urls import path, include


BASE_API_PATH = "api/v1"

urlpatterns = [
    path(f"{BASE_API_PATH}/auth/", include("accounts.urls")),
    # path(f"{BASE_API_PATH}/catalog/", include("catalog.urls")),
]
