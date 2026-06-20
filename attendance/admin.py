from django.contrib import admin

from .models import AttendanceRule, StudentAttendance, TeacherAttendance


@admin.register(AttendanceRule)
class AttendanceRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_attendance_percentage', 'lock_after_time', 'is_active')


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'school_class', 'section', 'date', 'status', 'subject')
    list_filter = ('date', 'status', 'school_class')
    date_hierarchy = 'date'


@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'status', 'shift')
    list_filter = ('date', 'status')
    date_hierarchy = 'date'
