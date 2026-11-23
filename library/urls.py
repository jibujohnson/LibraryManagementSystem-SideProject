from django.urls import path
from .views import UserRegistrationView,UserProfileView,UserLogoutView,LibrarianDashboardView,MemberDashboardView,BookListCreateView,BookDetailView,BookDeleteView,CategoryListCreateView,CategoryDetailView,CategoryDeleteView,BorrowBookView,MyBorrowingView,AllBorrowingView,BorrowingDetailView,ReturnBookView,MyFines,AllFineViews
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns=[
    path('register/',UserRegistrationView.as_view(),name='register'),
    path('login/',obtain_auth_token,name='login'),
    path('profile/',UserProfileView.as_view(),name='profile'),
    path('logout/',UserLogoutView.as_view(),name='logout'),
    path('librarian-dashboard/',LibrarianDashboardView.as_view(),name='librarian_dashboard'),
    path('member-dashboard/',MemberDashboardView.as_view(),name='member_dashboard'),

    path('books/',BookListCreateView.as_view(),name='book_list_create'),
    path('books/<int:pk>/',BookDetailView.as_view(),name='book_detail'),
    path('books/<int:pk>/delete/',BookDeleteView.as_view(),name='book_delete'),

    path('categories/',CategoryListCreateView.as_view(),name='category_list_create'),
    path('categories/<int:pk>/',CategoryDetailView.as_view(),name='category_detail'),
    path('categories/<int:pk>/delete/',CategoryDeleteView.as_view(),name='category_delete'),

    # IMPLEMENT THE BORROW BOOK API

    path('borrow/',BorrowBookView.as_view(),name='borrow_book'),
    path('my-borrowings/',MyBorrowingView.as_view(),name='my_borrowings'),
    path('all-borrowings/',AllBorrowingView.as_view(),name='all_borrowings'),
    path('borrow/<int:pk>/',BorrowingDetailView.as_view(),name='borrowing_detail'),

    # BOOK RETURNS

    path('return/<int:pk>/',ReturnBookView.as_view(),name='return_book'),

    path('my-fines/',MyFines.as_view(),name='my_fines'),
    path('all-fines/',AllFineViews.as_view(),name='all_fines'),
]