from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from catalog.models import Chapter, Book, Category
from catalog.serializers import ChapterReadSerializer, ChapterWriteSerializer, BookSerializer, CategorySerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'categories': reverse('category-list', request=request, format=format),
        'books': reverse('book-list', request=request, format=format),
        'chapters': reverse('chapter-list', request=request, format=format),
    })
    
class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class BookList(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class ChapterList(generics.ListCreateAPIView):
    queryset = Chapter.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChapterWriteSerializer
        return ChapterReadSerializer

class ChapterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterWriteSerializer
