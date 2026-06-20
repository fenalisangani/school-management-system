from django import forms
from django.utils import timezone

from classes.models import Section, SchoolClass

from .models import Student, StudentDocument, StudentEnrollment


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'student_id', 'full_name', 'date_of_birth', 'gender',
            'address', 'phone', 'email',
            'parent_name', 'parent_phone', 'parent_email',
            'photo', 'status',
        ]
        widgets = {
            'student_id': forms.TextInput(attrs={'placeholder': 'Leave blank to auto-generate'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_student_id(self):
        value = self.cleaned_data.get('student_id', '').strip()
        if not value:
            from core.utils import generate_unique_id
            value = generate_unique_id('STU', Student, 'student_id')
        return value


class StudentEnrollmentForm(forms.ModelForm):
    class Meta:
        model = StudentEnrollment
        fields = [
            'student', 'school_class', 'section', 'academic_year',
            'admission_date', 'is_current', 'promotion_notes',
        ]
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date', 'value': timezone.localdate().isoformat()}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(status='active').order_by('full_name')
        class_id = None
        if self.data.get('school_class'):
            class_id = self.data.get('school_class')
        elif self.initial.get('school_class'):
            class_id = getattr(self.initial.get('school_class'), 'pk', self.initial.get('school_class'))

        if class_id:
            self.fields['section'].queryset = Section.objects.filter(school_class_id=class_id)
        else:
            self.fields['section'].queryset = Section.objects.none()

    def clean(self):
        cleaned = super().clean()
        school_class = cleaned.get('school_class')
        section = cleaned.get('section')
        if school_class and section and section.school_class_id != school_class.id:
            raise forms.ValidationError('Section does not belong to the selected class.')
        if school_class and not cleaned.get('academic_year'):
            cleaned['academic_year'] = school_class.academic_year
        return cleaned


class StudentDocumentForm(forms.ModelForm):
    class Meta:
        model = StudentDocument
        fields = ['student', 'document_type', 'title', 'file']
