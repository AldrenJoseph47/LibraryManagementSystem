"""
URL configuration for LMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from .views import user_login,register,main,userhomepage,user_logout_view,subscription_list,process_payment,payment_success,list_of_books
from .views import feedback_view, feedback_success, rental_payment, rental_list, user_homepage, user_profile


urlpatterns = [
    path('', main, name='main'),
    path('account/register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('userhomepage/', userhomepage, name='userhomepage'),
    path('logout/', user_logout_view, name='logout'),
    path('useraccount/subscription/', subscription_list, name='plans'),
    path('process-payment/<int:plan_id>/', process_payment, name='process_payment'),
    path('useraccount/payment_success/', payment_success, name='payment_success'),  # Optional success view
    path('useraccount/list_of_books/', list_of_books, name='list_of_books'),
    path('books/<int:book_id>/', views.book_details, name='book_detail'),
    path('authors/', views.list_of_authors, name='list_of_authors'),
    path('authors/<int:author_id>/', views.author_details, name='author_details'),
    path('feedback/', feedback_view, name='feedback'),
    path('feedback/success/', feedback_success, name='feedback_success'),
    path('rental_payment/<int:rental_id>/', rental_payment, name='process_rental_payment'),
    path('payment/<int:book_id>/', rental_payment, name='rental_payment'),
    path('rental/payment/<int:rental_id>/', rental_payment, name='rental_payment'),
    path('rental-list/', rental_list, name='rental_list'),
    path('user-homepage/', user_homepage, name='user_homepage'),
    path('genres/', views.genre_list, name='genre_list'),
    path('profile/', user_profile, name='user_profile'),

]