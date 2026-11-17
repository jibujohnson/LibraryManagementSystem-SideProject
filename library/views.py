from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .serializers import UserRegistrationSerializer,BookSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsLibrarian,IsMember,IsLibrarianOrReadOnly
from .models import Book 

# Create your views here.

class UserRegistrationView(APIView):
    def post(self,request):
        serializer=UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class UserProfileView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user=request.user
        return Response({
            "id":user.id,
            "username":user.username,
            "email":user.email,
            "date_joined":user.date_joined
        },status=status.HTTP_200_OK)

class UserLogoutView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        request.user.auth_token.delete()
        return Response({
            "Message":"Successfully Logged Out!"
        },status=status.HTTP_200_OK)

class LibrarianDashboardView(APIView):
    permission_classes=[IsAuthenticated,IsLibrarian]
    def get(self,request):
        return Response({
            "Message":"Welcome Librarian! You have access to this dashboard."
        },status=status.HTTP_200_OK)

class MemberDashboardView(APIView):
    permission_classes=[IsAuthenticated,IsMember]
    def get(self,request):
        return Response({
            "Message":"Welcome Member! You have access to this dashboard."
        },status=status.HTTP_200_OK)


class BookListCreateView(generics.ListCreateAPIView):
    queryset=Book.objects.all()
    serializer_class=BookSerializer
    permission_classes=[IsAuthenticated,IsLibrarianOrReadOnly]