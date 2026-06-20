import json
from datetime import timedelta

from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from attendance.models import AttendanceStatus, StudentAttendance
from classes.models import AcademicYear, SchoolClass
from fees.models import PaymentStatus, StudentFeeAssignment
from students.models import Student
from teachers.models import Teacher


def dashboard(request):
    active_year = AcademicYear.objects.filter(is_active=True, is_archived=False).first()
    stats = {
        'classes': SchoolClass.objects.filter(status='active').count(),
        'students': Student.objects.filter(status='active').count(),
        'teachers': Teacher.objects.filter(employment_status='active').count(),
        'pending_fees': StudentFeeAssignment.objects.filter(
            status__in=[PaymentStatus.PENDING, PaymentStatus.PARTIAL],
        ).count(),
        'attendance_today': StudentAttendance.objects.filter(date=timezone.localdate()).count(),
    }
    setup_done = all([
        AcademicYear.objects.exists(),
        SchoolClass.objects.exists(),
        Student.objects.exists(),
        Teacher.objects.exists(),
    ])

    # Fee status breakdown (doughnut chart).
    fee_counts = {row['status']: row['n'] for row in (
        StudentFeeAssignment.objects.values('status').annotate(n=Count('id'))
    )}
    fee_chart = {
        'labels': [label for _, label in PaymentStatus.choices],
        'data': [fee_counts.get(value, 0) for value, _ in PaymentStatus.choices],
    }

    # Attendance over the last 7 days (bar chart): present vs absent counts.
    today = timezone.localdate()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    present_by_day = []
    absent_by_day = []
    for day in days:
        present_by_day.append(StudentAttendance.objects.filter(
            date=day, status=AttendanceStatus.PRESENT).count())
        absent_by_day.append(StudentAttendance.objects.filter(
            date=day, status=AttendanceStatus.ABSENT).count())
    attendance_chart = {
        'labels': [d.strftime('%a %d') for d in days],
        'present': present_by_day,
        'absent': absent_by_day,
    }

    has_attendance = any(present_by_day) or any(absent_by_day)
    has_fees = any(fee_chart['data'])

    return render(request, 'dashboard.html', {
        'stats': stats,
        'active_year': active_year,
        'setup_done': setup_done,
        'fee_chart_json': json.dumps(fee_chart),
        'attendance_chart_json': json.dumps(attendance_chart),
        'has_attendance': has_attendance,
        'has_fees': has_fees,
    })
