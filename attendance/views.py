import csv
from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from core.forms import ClassScopeFilterForm, ReportFilterForm
from core.report_helpers import report_date_label, scope_label
from core.report_pdf import build_report_pdf, pdf_inr
from core.scope_filters import apply_date_range, filter_attendance_queryset
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
    filter_form = ClassScopeFilterForm(request.GET or None)
    if filter_form.is_valid():
        records = filter_attendance_queryset(records, filter_form)

    query = request.GET.get('q', '').strip()
    if query:
        records = records.filter(student__full_name__icontains=query)
    page_obj = paginate(request, records, per_page=25)
    return render(request, 'attendance/student_attendance_list.html', {
        'records': page_obj,
        'page_obj': page_obj,
        'query': query,
        'filter_form': filter_form,
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
    get_initial = {}
    if request.method != 'POST':
        if request.GET.get('institution_type') in ('school', 'college'):
            get_initial['institution_type'] = request.GET['institution_type']
        class_pk = request.GET.get('class')
        if class_pk:
            get_initial['school_class'] = class_pk
        if request.GET.get('section'):
            get_initial['section'] = request.GET['section']
        if request.GET.get('semester'):
            get_initial['semester'] = request.GET['semester']

    bulk_form = BulkStudentAttendanceForm(request.POST or None, initial=get_initial or None)
    students = []
    school_class = section = date = None
    selected_semester = None

    if request.method == 'POST':
        if 'save_attendance' in request.POST:
            bulk_form = BulkStudentAttendanceForm(request.POST)
            if bulk_form.is_valid():
                school_class = bulk_form.cleaned_data['school_class']
                section = bulk_form.cleaned_data['section']
                semester = bulk_form.cleaned_data.get('semester')
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
                            semester=semester,
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
            semester = bulk_form.cleaned_data.get('semester')
            date = bulk_form.cleaned_data['date']
            selected_semester = semester
            default_status = bulk_form.cleaned_data['default_status']
            enrollments = StudentEnrollment.objects.filter(
                school_class=school_class,
                section=section,
                is_current=True,
            )
            if semester:
                enrollments = enrollments.filter(semester=semester)
            else:
                enrollments = enrollments.filter(semester__isnull=True)
            enrollments = enrollments.select_related('student')
            students = [(e.student, default_status) for e in enrollments]
            if not students:
                messages.warning(
                    request,
                    'No active enrollments for this class/section'
                    + (f' and semester {semester}.' if semester else '.'),
                )

    return render(request, 'attendance/bulk_attendance.html', {
        'bulk_form': bulk_form,
        'students': students,
        'selected_class': school_class,
        'selected_section': section,
        'selected_semester': selected_semester,
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


def _attendance_summary(filter_form=None):
    if filter_form is not None:
        filter_form.is_valid()
    records = StudentAttendance.objects.all()
    if filter_form and filter_form.is_valid():
        records = filter_attendance_queryset(records, filter_form)
        records = apply_date_range(records, filter_form, 'date')

    total_by_student = (
        records.values('student_id', 'student__full_name')
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
    filter_form = ReportFilterForm(request.GET or None)
    summaries, min_pct = _attendance_summary(filter_form)
    return render(request, 'attendance/attendance_report.html', {
        'summaries': summaries,
        'defaulters': [s for s in summaries if s['short']],
        'min_pct': min_pct,
        'filter_form': filter_form,
        'scope_label': scope_label(filter_form),
        'date_range_label': report_date_label(filter_form),
    })


def _report_pdf_filename(prefix, filter_form):
    if filter_form.is_valid():
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        if date_from and date_to:
            return f'{prefix}_{date_from:%Y%m%d}_to_{date_to:%Y%m%d}.pdf'
    return f'{prefix}_{timezone.localdate():%Y%m%d}.pdf'


def attendance_report_export(request):
    """Download the attendance summary as a CSV (opens in Excel)."""
    filter_form = ReportFilterForm(request.GET or None)
    summaries, min_pct = _attendance_summary(filter_form)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="{_report_pdf_filename("attendance_report", filter_form).replace(".pdf", ".csv")}"'
    )
    writer = csv.writer(response)
    writer.writerow(['Student', 'Present', 'Total Days', 'Attendance %', f'Below {min_pct}%?'])
    for s in summaries:
        writer.writerow([
            s['name'], s['present'], s['total'], s['percentage'],
            'Yes' if s['short'] else 'No',
        ])
    return response


def attendance_report_pdf(request):
    filter_form = ReportFilterForm(request.GET or None)
    summaries, min_pct = _attendance_summary(filter_form)
    defaulters = [s for s in summaries if s['short']]
    rows = [
        [
            s['name'],
            str(s['present']),
            str(s['total']),
            f"{s['percentage']}%",
            'Below minimum' if s['short'] else 'On track',
        ]
        for s in summaries
    ]
    return build_report_pdf(
        title='Attendance Report',
        filename=_report_pdf_filename('attendance_report', filter_form),
        meta_lines=[
            f'<b>Period:</b> {report_date_label(filter_form)}',
            f'<b>Scope:</b> {scope_label(filter_form)}',
            f'<b>Minimum required:</b> {min_pct}%',
        ],
        headers=['Student', 'Present', 'Total days', 'Attendance %', 'Status'],
        rows=rows,
        summary_stats=[
            {'label': 'Total students', 'value': len(summaries), 'tone': 'default'},
            {'label': 'On track', 'value': len(summaries) - len(defaulters), 'tone': 'success'},
            {'label': f'Below {min_pct}%', 'value': len(defaulters), 'tone': 'danger'},
        ],
        row_statuses=['bad' if s['short'] else 'ok' for s in summaries],
        status_col=4,
    )


def attendance_rule_create(request):
    form = AttendanceRuleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Attendance rule saved.')
        return redirect('attendance_report')
    return render_model_form(
        request, form, 'Configure Attendance Rule', reverse('attendance_report'),
    )
