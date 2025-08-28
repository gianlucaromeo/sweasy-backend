from rest_framework import serializers
from catalog.models import Category, Book, Chapter
from rest_framework.reverse import reverse


class BookPreviewSerializer(serializers.HyperlinkedModelSerializer):
    chapters_number = serializers.SerializerMethodField()
    
    def get_chapters_number(self, obj):
        return obj.chapters.count()
    
    class Meta:
        model = Book
        fields = ['title', 'chapters_number', 'url']
  
    
        
class ChapterPreviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Chapter
        fields = ['title', 'url']

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    books = BookPreviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'books', 'url']
        

class BookSerializer(serializers.HyperlinkedModelSerializer):
    chapters = ChapterPreviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Book
        fields = ['number', 'title', 'description', 'category', 'chapters', 'url']

class ChapterReadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Chapter
        fields = ['url', 'book', 'number', 'title', 'description']
        
class ChapterWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['book', 'number', 'title', 'description', 'content']
