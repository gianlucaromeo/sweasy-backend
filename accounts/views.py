from django.db import transaction
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import IsAuthenticated
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import User
from .serializers import UserSerializer

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
    })
    
class CustomRegisterView(RegisterView):
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        GENERIC_MSG = {
            "detail": "If this account was not registered before, a confirmation email will be sent to this address."
        }

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            detail = exc.detail if isinstance(exc.detail, dict) else {}
            
            print(detail)

            email_dup = "email" in detail
            username_dup = "username" in detail

            if email_dup or username_dup:
                return Response(GENERIC_MSG, status=status.HTTP_201_CREATED)

            raise  # propagate normal 400s

        print("Performing create")
        self.perform_create(serializer)  # sends verification email
        return Response(GENERIC_MSG, status=status.HTTP_201_CREATED)
        
        
class DestroyMeView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        request.user.is_active = False
        request.user.save(update_fields=['is_active'])
        return Response(
            {"detail": "We succesfully stored your request of account deletion and will process it soon."},
            status=status.HTTP_204_NO_CONTENT
        )

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer