import csv
from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from core.view_helpers import paginate, render_model_form
from students.models import StudentEnrollment

from .forms import (
    AttendanceRuleForm,
    BulkStudentAttendanceForm,
    StudentAttendanceForm,
    TeacherAttendanceForm,
)
from .models import AttendanceRule, AttendanceStatus, StudentAttendance, TeacherAttendance


def student_attendance_list(request):
    records = StudentAttendance.objects.select_related(
        'student', 'school_class', 'section', 'subject',
    )
    query = request.GET.get('q', '').strip()
    if query:
        records = records.filter(student__full_name__icontains=query)
    page_obj = paginate(request, records, per_page=25)
    return render(request, 'attendance/student_attendance_list.html', {
        'records': page_obj,
        'page_obj': page_obj,
        'query': query,
    })


def student_attendance_create(request):
    form = StudentAttendanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        if request.user.is_authenticated:
            record.marked_by = request.user
        record.save()
        messages.success(request, 'Attendance recorded.')
        return redirect('student_attendance_list')
    return render_model_form(
        request, form, 'Mark Student Attendance', reverse('student_attendance_list'), cascade_form=True,
    )


def bulk_student_attendance(request):
    bulk_form = BulkStudentAttendanceForm(request.POST or None)
    students = []
    school_class = section = date = None

    if request.method == 'POST':
        if 'save_attendance' in request.POST:
            bulk_form = BulkStudentAttendanceForm(request.POST)
            if bulk_form.is_valid():
                school_class = bulk_form.cleaned_data['school_class']
                section = bulk_form.cleaned_data['section']
                date = bulk_form.cleaned_data['date']
                count = 0
                for key, value in request.POST.items():
                    if key.startswith('status_'):
                        student_pk = int(key.replace('status_', ''))
                        StudentAttendance.objects.update_or_create(
                            student_id=student_pk,
                            school_class=school_class,
                            section=section,
                            subject=None,
                            date=date,
                            defaults={
                                'status': value,
                                'marked_by': request.user if request.user.is_authenticated else None,
                            },
                        )
                        count += 1
                messages.success(request, f'Attendance saved for {count} students.')
                return redirect('student_attendance_list')
        elif bulk_form.is_valid() and 'load_students' in request.POST:
            school_class = bulk_form.cleaned_data['school_class']
            section = bulk_form.cleaned_data['section']
            date = bulk_form.cleaned_data['date']
            default_status = bulk_form.cleaned_data['default_status']
            enrollments = StudentEnrollment.objects.filter(
                school_class=school_class,
                section=section,
                is_current=True,
            ).select_related('student')
            students = [(e.student, default_status) for e in enrollments]
            if not students:
                messages.warning(request, 'No active enrollments for this class and section.')

    return render(request, 'attendance/bulk_attendance.html', {
        'bulk_form': bulk_form,
        'students': students,
        'selected_class': school_class,
        'selected_section': section,
        'selected_date': date,
    })


def teacher_attendance_list(request):
    records = TeacherAttendance.objects.select_related('teacher')
    page_obj = paginate(request, records, per_page=25)
    return render(request, 'attendance/teacher_attendance_list.html', {
        'records': page_obj,
        'page_obj': page_obj,
    })


def teacher_attendance_create(request):
    form = TeacherAttendanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        if request.user.is_authenticated:
            record.marked_by = request.user
        record.save()
        messages.success(request, 'Teacher attendance recorded.')
        return redirect('teacher_attendance_list')
    return render_model_form(
        request, form, 'Mark Teacher Attendance', reverse('teacher_attendance_list'),
    )


def _attendance_summary():
    total_by_student = (
        StudentAttendance.objects.values('student_id', 'student__full_name')
        .annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status=AttendanceStatus.PRESENT)),
        )
    )
    rule = AttendanceRule.objects.filter(is_active=True).first()
    min_pct = rule.min_attendance_percentage if rule else Decimal('75')

    summaries = []
    for row in total_by_student:
        pct = (row['present'] / row['total']) * 100 if row['total'] else 0
        summaries.append({
            'name': row['student__full_name'],
            'present': row['present'],
            'total': row['total'],
            'percentage': round(pct, 1),
            'short': pct < min_pct,
        })
    return summaries, min_pct


def attendance_report(request):
    summaries, min_pct = _attendance_summary()
    return render(request, 'attendance/attendance_report.html', {
        'summaries': summaries,
        'defaulters': [s for s in summaries if s['short']],
        'min_pct': min_pct,
    })


def attendance_report_export(request):
    """Download the attendance summary as a CSV (opens in Excel)."""
    summaries, min_pct = _attendance_summary()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="attendance_report_{timezone.localdate()}.csv"'
    )
    writer = csv.writer(response)
    writer.writerow(['Student', 'Present', 'Total Days', 'Attendance %', f'Below {min_pct}%?'])
    for s in summaries:
        writer.writerow([
            s['name'], s['present'], s['total'], s['percentage'],
            'Yes' if s['short'] else 'No',
        ])
    return response


def attendance_rule_create(request):
    form = AttendanceRuleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Attendance rule saved.')
        return redirect('attendance_report')
    return render_model_form(
        request, form, 'Configure Attendance Rule', reverse('attendance_report'),
    )
