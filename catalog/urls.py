from django.urls import path
from catalog.views import ChapterList, ChapterDetail, api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('chapters/', ChapterList.as_view(), name='chapter-list'),
    path('chapters/<int:pk>/', ChapterDetail.as_view(), name='chapter-detail'),
]