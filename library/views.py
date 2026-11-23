from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .serializers import UserRegistrationSerializer,BookSerializer,CategorySerializer,BorrowRecordSerializer,FineSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsLibrarian,IsMember,IsLibrarianOrReadOnly,IsMemberOrLibrarian
from .models import Book,Category,BorrowRecord,Fine
from decimal import Decimal

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


# BOOK CRUD

class BookListCreateView(generics.ListCreateAPIView):
    queryset=Book.objects.all()
    serializer_class=BookSerializer
    permission_classes=[IsAuthenticated,IsLibrarianOrReadOnly]

class BookDetailView(generics.RetrieveUpdateAPIView):
    queryset=Book.objects.all()
    serializer_class=BookSerializer
    permission_classes=[IsAuthenticated,IsLibrarianOrReadOnly]

class BookDeleteView(generics.DestroyAPIView):
    queryset=Book.objects.all()
    serializer_class=BookSerializer
    permission_classes=[IsAuthenticated,IsLibrarian]

# CATEGORY CRUD

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsAuthenticated,IsLibrarianOrReadOnly]

class CategoryDetailView(generics.RetrieveUpdateAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsAuthenticated,IsLibrarianOrReadOnly]

class CategoryDeleteView(generics.DestroyAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsAuthenticated,IsLibrarian]

# IMPLEMENT THE BORROW BOOK API

class BorrowBookView(generics.CreateAPIView):

    serializer_class=BorrowRecordSerializer
    permission_classes=[IsAuthenticated,IsMemberOrLibrarian]

    def create(self,request,*args,**kwargs):
        book_id=request.data.get('book')
        if not book_id:
            return Response(
                {"ERROR":"Book ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            try:
                book=Book.objects.select_for_update().get(id=book_id)
            except Book.DoesNotExist:
                return Response(
                    {"ERROR":"Book not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            if book.available_copies<=0:
                return Response(
                    {"ERROR":"No copies available for borrowing."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check whether the user has already borrowed the same book.

            existing_borrow=BorrowRecord.objects.filter(
                user=request.user,
                book=book,
                status='BORROWED'
            ).exists()

            if existing_borrow:
                return Response(
                    {"ERROR":"You have already borrowed this book."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Check the maximum borrowing limit

            active_borrowings=BorrowRecord.objects.filter(
                user=request.user,
                status='BORROWED'
            ).count()

            if active_borrowings>= 3:
                return Response(
                    {"ERROR":"You cannot borrow more than 3 books at a time."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            borrow_record=BorrowRecord.objects.create(
                user=request.user,
                book=book,
                due_date=timezone.localdate()+timedelta(days=14)
            )

            book.available_copies-=1
            book.save(update_fields=['available_copies'])

        serializer=self.get_serializer(borrow_record)
        return Response(
            {
                "Message":"Book borrowed successfully.",
                "borrow_record":serializer.data
            },
            status=status.HTTP_201_CREATED
        )

# MY BORROWINGS - LIST THE BORROWING RECORDS OF A SPECIFIC USER

class MyBorrowingView(generics.ListAPIView):
    serializer_class=BorrowRecordSerializer
    permission_classes=[IsAuthenticated,IsMemberOrLibrarian]
    def get_queryset(self):
        return BorrowRecord.objects.filter(
            user=self.request.user
        )

# ALL BORROWINGS - LIBRARIANS CAN VIEW ALL THE BORROWING RECORDS OF EVERY USER

class AllBorrowingView(generics.ListAPIView):
    queryset=BorrowRecord.objects.all()
    serializer_class=BorrowRecordSerializer
    permission_classes=[IsAuthenticated,IsLibrarian]

# RETRIEVE THE BORROWING RECORD OF A SPECIFIC BOOK
# LIBRARIANS CAN ANY BORROW RECORD BY ID

class BorrowingDetailView(generics.RetrieveAPIView):
    serializer_class=BorrowRecordSerializer
    permission_classes=[IsAuthenticated,IsMemberOrLibrarian]
    def get_queryset(self):
        user=self.request.user
        if user.groups.filter(name='Librarian').exists():
            return BorrowRecord.objects.all()
        return BorrowRecord.objects.filter(user=user)

# BOOK RETURN API

class ReturnBookView(generics.GenericAPIView):
    serializer_class=BorrowRecordSerializer
    permission_classes=[IsAuthenticated,IsMemberOrLibrarian]

    def get_queryset(self):
        user=self.request.user
        if user.groups.filter(name='Librarian').exists():
            return BorrowRecord.objects.all()
        return BorrowRecord.objects.filter(user=user)

    def post(self,request,pk):
        with transaction.atomic():
            try:
                borrow_record=self.get_queryset().select_for_update().get(pk=pk)
            except BorrowRecord.DoesNotExist:
                return Response(
                    {"ERROR":"Borrowing record not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if borrow_record.status==BorrowRecord.RETURNED:
                return Response(
                    {"ERROR":"This book has already been returned."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            book=Book.objects.select_for_update().get(
                pk=borrow_record.book_id
            )

            borrow_record.status=BorrowRecord.RETURNED
            borrow_record.return_date=timezone.localdate()
            borrow_record.save(
                update_fields=['status','return_date']
            )

            book.available_copies+=1
            book.save(update_fields=['available_copies'])

            # AUTOMATIC FINE GENERATION

            overdue_days=(
                borrow_record.return_date-borrow_record.due_date
            ).days

            if overdue_days>0:
                fine_amount=Decimal(
                    str(settings.LIBRARY_FINE_PER_DAY)
                ) * overdue_days

                Fine.objects.create(
                    borrow_record=borrow_record,
                    fine_amount=fine_amount
                )

        serializer=self.get_serializer(borrow_record)
        return Response({
            "Message":"Book returned successfully.",
            "borrow_record":BorrowRecordSerializer(borrow_record).data,
            "fine":FineSerializer(
                Fine.objects.filter(borrow_record=borrow_record).first()
            ).data if Fine.objects.filter(borrow_record=borrow_record).exists() else None
        })

class MyFines(generics.ListAPIView):
    serializer_class=FineSerializer
    permission_classes=[IsAuthenticated,IsMemberOrLibrarian]
    def get_queryset(self):
        return Fine.objects.filter(
            borrow_record__user=self.request.user
        )

class AllFineViews(generics.ListAPIView):
    queryset=Fine.objects.all()
    serializer_class=FineSerializer
    permission_classes=[IsAuthenticated,IsLibrarian]





