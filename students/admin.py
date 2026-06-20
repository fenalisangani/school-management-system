from django.contrib import admin

from .models import Student, StudentDocument, StudentEnrollment


class DocumentInline(admin.TabularInline):
    model = StudentDocument
    extra = 0


class EnrollmentInline(admin.TabularInline):
    model = StudentEnrollment
    extra = 0


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'date_of_birth', 'gender', 'status')
    list_filter = ('status', 'gender')
    search_fields = ('student_id', 'full_name', 'email', 'phone')
    inlines = [EnrollmentInline, DocumentInline]


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'school_class', 'section', 'academic_year', 'admission_date', 'is_current')
    list_filter = ('is_current', 'academic_year', 'school_class')


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'document_type', 'title', 'uploaded_at')
