from django.urls import path
from .views import UserRegistrationView,UserProfileView,UserLogoutView,LibrarianDashboardView,MemberDashboardView,BookListCreateView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns=[
    path('register/',UserRegistrationView.as_view(),name='register'),
    path('login/',obtain_auth_token,name='login'),
    path('profile/',UserProfileView.as_view(),name='profile'),
    path('logout/',UserLogoutView.as_view(),name='logout'),
    path('librarian-dashboard/',LibrarianDashboardView.as_view(),name='librarian_dashboard'),
    path('member-dashboard/',MemberDashboardView.as_view(),name='member_dashboard'),

    path('books/',BookListCreateView.as_view(),name='book_list_create'),
    

]