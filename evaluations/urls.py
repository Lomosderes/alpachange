from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_list, name='teacher_list'),
    path('<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('review/<int:teacher_id>/', views.add_review, name='add_review'),
]
