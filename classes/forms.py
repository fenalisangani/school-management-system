from django import forms

from .models import (
    AcademicYear,
    ClassSubject,
    InstitutionType,
    ProgramType,
    SchoolClass,
    Section,
    Subject,
)


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
        fields = [
            'class_id', 'name', 'institution_type', 'program_type',
            'academic_year', 'status',
        ]
        widgets = {
            'class_id': forms.TextInput(attrs={'placeholder': 'Leave blank to auto-generate'}),
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Std 8, BCA, MCA'}),
        }

    def clean_class_id(self):
        value = self.cleaned_data.get('class_id', '').strip()
        if not value:
            from core.utils import generate_unique_id
            value = generate_unique_id('CLS', SchoolClass, 'class_id')
        return value

    def clean(self):
        cleaned = super().clean()
        institution = cleaned.get('institution_type')
        program = cleaned.get('program_type')
        if institution == InstitutionType.SCHOOL:
            cleaned['program_type'] = ProgramType.SCHOOL
        elif program == ProgramType.SCHOOL:
            raise forms.ValidationError(
                'College courses must use a semester-based program type '
                '(UG 3yr, Integrated 4yr, or PG 2yr).'
            )
        return cleaned


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['school_class', 'name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Class 1, Class 2, A, B'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['code', 'name', 'credit_hours']


class ClassSubjectForm(forms.ModelForm):
    class Meta:
        model = ClassSubject
        fields = ['school_class', 'subject']
