from rest_framework import generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from catalog.models import Chapter
from catalog.serializers import ChapterSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'chapters': reverse('chapter-list', request=request),
    })

class ChapterList(generics.ListCreateAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer

class ChapterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer