from django.urls import path
from catalog.views import BookList, ChapterList, ChapterDetail, api_root, BookDetail, CategoryList, CategoryDetail

urlpatterns = [
    path('', api_root, name='api-root'),
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
    path('books/', BookList.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetail.as_view(), name='book-detail'),
    path('chapters/', ChapterList.as_view(), name='chapter-list'),
    path('chapters/<int:pk>/', ChapterDetail.as_view(), name='chapter-detail'),
]