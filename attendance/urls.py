from django.urls import path

from . import views

urlpatterns = [
    path('students/', views.student_attendance_list, name='student_attendance_list'),
    path('students/add/', views.student_attendance_create, name='student_attendance_create'),
    path('students/bulk/', views.bulk_student_attendance, name='bulk_student_attendance'),
    path('teachers/', views.teacher_attendance_list, name='teacher_attendance_list'),
    path('teachers/add/', views.teacher_attendance_create, name='teacher_attendance_create'),
    path('reports/', views.attendance_report, name='attendance_report'),
    path('reports/export/', views.attendance_report_export, name='attendance_report_export'),
    path('rules/add/', views.attendance_rule_create, name='attendance_rule_create'),
]
