from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core.view_helpers import confirm_delete, paginate, render_model_form

from .forms import StudentDocumentForm, StudentEnrollmentForm, StudentForm
from .models import Student, StudentEnrollment


def student_list(request):
    students = Student.objects.prefetch_related(
        'enrollments__school_class',
        'enrollments__section',
        'enrollments__academic_year',
    )
    query = request.GET.get('q', '').strip()
    if query:
        students = students.filter(
            Q(full_name__icontains=query)
            | Q(student_id__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
        )
    page_obj = paginate(request, students)
    return render(request, 'students/student_list.html', {
        'students': page_obj,
        'page_obj': page_obj,
        'query': query,
    })


def student_create(request):
    form = StudentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Student registered.')
        return redirect('student_list')
    return render_model_form(
        request, form, 'Register Student', reverse('student_list'), multipart=True,
    )


def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, request.FILES or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Student updated.')
        return redirect('student_detail', pk=student.pk)
    return render_model_form(
        request, form, f'Edit Student — {student.full_name}',
        reverse('student_detail', args=[student.pk]), multipart=True,
    )


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return confirm_delete(
        request, student, 'Student', reverse('student_list'),
        success_message=f'Student {student.full_name} deleted.',
    )


def student_detail(request, pk):
    student = get_object_or_404(
        Student.objects.prefetch_related(
            'enrollments__school_class',
            'enrollments__section',
            'enrollments__academic_year',
            'documents',
        ),
        pk=pk,
    )
    return render(request, 'students/student_detail.html', {'student': student})


def enrollment_create(request):
    form = StudentEnrollmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if form.cleaned_data['is_current']:
            StudentEnrollment.objects.filter(
                student=form.cleaned_data['student'],
                is_current=True,
            ).update(is_current=False)
        form.save()
        messages.success(request, 'Student enrolled in class.')
        return redirect('student_list')
    return render_model_form(
        request, form, 'Enroll Student in Class', reverse('student_list'), cascade_form=True,
    )


def document_upload(request):
    form = StudentDocumentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        doc = form.save()
        messages.success(request, 'Document uploaded.')
        return redirect('student_detail', pk=doc.student.pk)
    return render_model_form(
        request, form, 'Upload Student Document', reverse('student_list'), multipart=True,
    )
