from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify/', views.verify_email, name='verify_email'),
    path('login/', views.custom_login, name='login'),
    path('profile/<int:user_id>/', views.public_profile, name='public_profile'), 
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.custom_logout, name='logout'),
]