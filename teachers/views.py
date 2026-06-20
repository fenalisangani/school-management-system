from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core.view_helpers import confirm_delete, paginate, render_model_form

from .forms import ClassTeacherAssignmentForm, TeacherForm
from .models import Teacher


def teacher_list(request):
    teachers = Teacher.objects.prefetch_related('assignments__school_class', 'assignments__subject')
    query = request.GET.get('q', '').strip()
    if query:
        teachers = teachers.filter(
            Q(full_name__icontains=query)
            | Q(teacher_id__icontains=query)
            | Q(qualification__icontains=query)
            | Q(email__icontains=query)
        )
    page_obj = paginate(request, teachers)
    return render(request, 'teachers/teacher_list.html', {
        'teachers': page_obj,
        'page_obj': page_obj,
        'query': query,
    })


def teacher_create(request):
    form = TeacherForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Teacher registered.')
        return redirect('teacher_list')
    return render_model_form(request, form, 'Add Teacher', reverse('teacher_list'))


def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    form = TeacherForm(request.POST or None, instance=teacher)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Teacher updated.')
        return redirect('teacher_detail', pk=teacher.pk)
    return render_model_form(
        request, form, f'Edit Teacher — {teacher.full_name}',
        reverse('teacher_detail', args=[teacher.pk]),
    )


def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return confirm_delete(
        request, teacher, 'Teacher', reverse('teacher_list'),
        success_message=f'Teacher {teacher.full_name} deleted.',
    )


def teacher_detail(request, pk):
    teacher = get_object_or_404(
        Teacher.objects.prefetch_related(
            'assignments__school_class',
            'assignments__section',
            'assignments__subject',
        ),
        pk=pk,
    )
    return render(request, 'teachers/teacher_detail.html', {'teacher': teacher})


def assignment_create(request):
    form = ClassTeacherAssignmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Teacher assigned to class/subject.')
        return redirect('teacher_list')
    return render_model_form(
        request, form, 'Assign Teacher', reverse('teacher_list'), cascade_form=True,
    )
