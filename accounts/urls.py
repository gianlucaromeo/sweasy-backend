from django.urls import path
from .views import DestroyMeView, UserList, UserDetail, api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('users/', UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('delete-account/', DestroyMeView.as_view(), name='delete-user'),
]