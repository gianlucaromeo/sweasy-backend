from rest_framework import serializers
from .models import User
from allauth.account.adapter import get_adapter
from dj_rest_auth.registration.serializers import RegisterSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'username']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user