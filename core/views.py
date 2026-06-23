import json
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_not_required

from attendance.models import AttendanceStatus, StudentAttendance
from classes.models import AcademicYear, InstitutionType, SchoolClass
from fees.models import PaymentStatus, StudentFeeAssignment
from students.models import Student
from teachers.models import Teacher


def dashboard(request):
    active_year = AcademicYear.objects.filter(is_active=True, is_archived=False).first()
    attendance_today = StudentAttendance.objects.filter(date=timezone.localdate()).count()
    present_today = StudentAttendance.objects.filter(
        date=timezone.localdate(), status=AttendanceStatus.PRESENT,
    ).count()
    attendance_rate = round((present_today / attendance_today) * 100) if attendance_today else 0

    stats = {
        'classes': SchoolClass.objects.filter(status='active').count(),
        'school_classes': SchoolClass.objects.filter(status='active', institution_type=InstitutionType.SCHOOL).count(),
        'college_courses': SchoolClass.objects.filter(status='active', institution_type=InstitutionType.COLLEGE).count(),
        'students': Student.objects.filter(status='active').count(),
        'school_students': Student.objects.filter(status='active', institution_type=InstitutionType.SCHOOL).count(),
        'college_students': Student.objects.filter(status='active', institution_type=InstitutionType.COLLEGE).count(),
        'teachers': Teacher.objects.filter(employment_status='active').count(),
        'pending_fees': StudentFeeAssignment.objects.filter(
            status__in=[PaymentStatus.PENDING, PaymentStatus.PARTIAL],
        ).count(),
        'attendance_today': attendance_today,
        'attendance_rate': attendance_rate,
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


@method_decorator(login_not_required, name='dispatch')
class ToggleLoginView(LoginView):
    """Login page with an env toggle to show maintenance instead (LOGIN_PAGE_VISIBLE)."""
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if not settings.LOGIN_PAGE_VISIBLE:
            return render(request, 'registration/login_hidden.html', status=503)
        return super().dispatch(request, *args, **kwargs)
