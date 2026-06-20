from django.urls import path

from . import api, views

urlpatterns = [
    path('api/<int:class_id>/sections/', api.api_sections, name='api_sections'),
    path('api/<int:class_id>/meta/', api.api_class_meta, name='api_class_meta'),
    path('', views.class_list, name='class_list'),
    path('academic-years/', views.academic_year_list, name='academic_year_list'),
    path('academic-years/add/', views.academic_year_create, name='academic_year_create'),
    path('academic-years/<int:pk>/edit/', views.academic_year_edit, name='academic_year_edit'),
    path('academic-years/<int:pk>/delete/', views.academic_year_delete, name='academic_year_delete'),
    path('add/', views.school_class_create, name='school_class_create'),
    path('sections/add/', views.section_create, name='section_create'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    path('assign-subject/', views.class_subject_create, name='class_subject_create'),
    path('<int:pk>/', views.school_class_detail, name='school_class_detail'),
    path('<int:pk>/edit/', views.school_class_edit, name='school_class_edit'),
    path('<int:pk>/delete/', views.school_class_delete, name='school_class_delete'),
]
