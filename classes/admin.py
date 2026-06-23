from django.contrib import admin

from .models import AcademicYear, ClassSubject, SchoolClass, Section, Subject


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active', 'is_archived')
    list_filter = ('is_active', 'is_archived')


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_class')
    list_filter = ('school_class',)
    search_fields = ('name', 'school_class__name')


class ClassSubjectInline(admin.TabularInline):
    model = ClassSubject
    extra = 1


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'name', 'institution_type', 'program_type', 'academic_year', 'status')
    list_filter = ('institution_type', 'program_type', 'status', 'academic_year')
    search_fields = ('class_id', 'name')
    inlines = [SectionInline, ClassSubjectInline]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credit_hours')
    search_fields = ('code', 'name')


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'subject')
    list_filter = ('school_class__academic_year',)
