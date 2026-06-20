from django.urls import path

from . import views

urlpatterns = [
    path('', views.teacher_list, name='teacher_list'),
    path('add/', views.teacher_create, name='teacher_create'),
    path('assign/', views.assignment_create, name='teacher_assignment_create'),
    path('<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),
    path('<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),
]
