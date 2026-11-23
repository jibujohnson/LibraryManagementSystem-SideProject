from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book,Category,BorrowRecord,Fine

class UserRegistrationSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['id','username','email','password']

    def create(self,validated_data):
        user=User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model=Book
        fields="__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"

class BorrowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model=BorrowRecord
        fields="__all__"
        read_only_fields=['user','borrow_date','return_date','status']

class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model=Fine
        fields="__all__"