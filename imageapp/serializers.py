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
class health_assistance_serializers(serializers.ModelSerializer):
    class Meta:
        model = chatbot
        exclude = ['id' , 'answer']
class UserIdSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
            return user.id
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")
class RagBotSerializers(serializers.ModelSerializer):
    class Meta:
        model = ragbotmodel
        exclude = ['id']
class ragbotqa(serializers.Serializer):
    input_text = serializers.CharField(max_length=1050)
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