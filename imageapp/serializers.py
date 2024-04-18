from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class UserSerilizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username' , 'email' , 'password']
class translationSerilizer(serializers.Serializer):
    input_text = serializers.CharField(max_length=1050)
    input_language = serializers.CharField(max_length=100)
    output_language = serializers.CharField(max_length=100)

# class LoginUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'email', 'password')

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user
    
    
# class SignUpUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'first_name', 'last_name', 'username' ,'email', 'password')

# class ImageSerializer(serializers.Serializer):
#     input_image = serializers.ListField(
#         child=serializers.ImageField(allow_empty_file=False),
#         allow_empty=False
#     )

# class UserNameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username']