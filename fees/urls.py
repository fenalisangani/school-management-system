from django.urls import path

from . import views

urlpatterns = [
    path('structures/', views.fee_structure_list, name='fee_structure_list'),
    path('structures/add/', views.fee_structure_create, name='fee_structure_create'),
    path('structures/<int:pk>/edit/', views.fee_structure_edit, name='fee_structure_edit'),
    path('structures/<int:pk>/delete/', views.fee_structure_delete, name='fee_structure_delete'),
    path('assignments/', views.student_fee_list, name='student_fee_list'),
    path('assignments/add/', views.student_fee_assign, name='student_fee_assign'),
    path('assignments/<int:pk>/delete/', views.student_fee_delete, name='student_fee_delete'),
    path('payments/add/', views.fee_payment_create, name='fee_payment_create'),
    path('payments/<int:pk>/receipt/', views.fee_receipt, name='fee_receipt'),
    path('payments/export/', views.fee_payments_export, name='fee_payments_export'),
    path('reports/', views.fee_report, name='fee_report'),
    path('reports/pdf/', views.fee_report_pdf, name='fee_report_pdf'),
]
