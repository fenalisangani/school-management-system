from django import forms

from .models import AcademicYear, ClassSubject, SchoolClass, Section, Subject


class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['name', 'start_date', 'end_date', 'is_active', 'is_archived']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['class_id', 'name', 'academic_year', 'status']
        widgets = {
            'class_id': forms.TextInput(attrs={'placeholder': 'Leave blank to auto-generate'}),
        }

    def clean_class_id(self):
        value = self.cleaned_data.get('class_id', '').strip()
        if not value:
            from core.utils import generate_unique_id
            value = generate_unique_id('CLS', SchoolClass, 'class_id')
        return value


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['school_class', 'name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. A, B, C'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['code', 'name', 'credit_hours']


class ClassSubjectForm(forms.ModelForm):
    class Meta:
        model = ClassSubject
        fields = ['school_class', 'subject']
