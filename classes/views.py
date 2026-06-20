from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core.view_helpers import confirm_delete, paginate, render_model_form

from .forms import (
    AcademicYearForm,
    ClassSubjectForm,
    SchoolClassForm,
    SectionForm,
    SubjectForm,
)
from .models import AcademicYear, SchoolClass, Subject


def class_list(request):
    classes = SchoolClass.objects.select_related('academic_year').prefetch_related(
        'sections', 'class_subjects__subject',
    )
    query = request.GET.get('q', '').strip()
    if query:
        classes = classes.filter(
            Q(name__icontains=query) | Q(class_id__icontains=query)
        )
    page_obj = paginate(request, classes)
    return render(request, 'classes/class_list.html', {
        'classes': page_obj,
        'page_obj': page_obj,
        'query': query,
    })


def academic_year_list(request):
    years = AcademicYear.objects.all()
    return render(request, 'classes/academic_year_list.html', {'years': years})


def academic_year_create(request):
    form = AcademicYearForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Academic year created.')
        return redirect('academic_year_list')
    return render_model_form(request, form, 'Add Academic Year', reverse('academic_year_list'))


def academic_year_edit(request, pk):
    year = get_object_or_404(AcademicYear, pk=pk)
    form = AcademicYearForm(request.POST or None, instance=year)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Academic year updated.')
        return redirect('academic_year_list')
    return render_model_form(request, form, f'Edit Academic Year — {year.name}', reverse('academic_year_list'))


def academic_year_delete(request, pk):
    year = get_object_or_404(AcademicYear, pk=pk)
    return confirm_delete(request, year, 'Academic Year', reverse('academic_year_list'))


def school_class_create(request):
    form = SchoolClassForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Class created.')
        return redirect('class_list')
    return render_model_form(request, form, 'Add Class', reverse('class_list'))


def school_class_edit(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    form = SchoolClassForm(request.POST or None, instance=school_class)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Class updated.')
        return redirect('school_class_detail', pk=school_class.pk)
    return render_model_form(
        request, form, f'Edit Class — {school_class.name}',
        reverse('school_class_detail', args=[school_class.pk]),
    )


def school_class_delete(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    return confirm_delete(request, school_class, 'Class', reverse('class_list'))


def section_create(request):
    form = SectionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Section added.')
        return redirect('class_list')
    return render_model_form(request, form, 'Add Section', reverse('class_list'), cascade_form=True)


def subject_list(request):
    subjects = Subject.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        subjects = subjects.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )
    page_obj = paginate(request, subjects)
    return render(request, 'classes/subject_list.html', {
        'subjects': page_obj,
        'page_obj': page_obj,
        'query': query,
    })


def subject_create(request):
    form = SubjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Subject created.')
        return redirect('subject_list')
    return render_model_form(request, form, 'Add Subject', reverse('subject_list'))


def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(request.POST or None, instance=subject)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Subject updated.')
        return redirect('subject_list')
    return render_model_form(request, form, f'Edit Subject — {subject.name}', reverse('subject_list'))


def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    return confirm_delete(request, subject, 'Subject', reverse('subject_list'))


def class_subject_create(request):
    form = ClassSubjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Subject assigned to class.')
        return redirect('class_list')
    return render_model_form(request, form, 'Assign Subject to Class', reverse('class_list'))


def school_class_detail(request, pk):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related('academic_year').prefetch_related(
            'sections', 'class_subjects__subject',
        ),
        pk=pk,
    )
    return render(request, 'classes/class_detail.html', {'school_class': school_class})
