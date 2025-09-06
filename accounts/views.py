from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import RegisterSerializer, LoginSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()
        # Send email
        print("...Sending email...")


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer