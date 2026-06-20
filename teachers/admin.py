from django.contrib import admin

from .models import ClassTeacherAssignment, Teacher


class AssignmentInline(admin.TabularInline):
    model = ClassTeacherAssignment
    extra = 1


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'full_name', 'qualification', 'employment_status')
    list_filter = ('employment_status',)
    search_fields = ('teacher_id', 'full_name', 'email')
    inlines = [AssignmentInline]


@admin.register(ClassTeacherAssignment)
class ClassTeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'school_class', 'section', 'subject', 'role', 'workload_hours')
    list_filter = ('role', 'school_class__academic_year')
