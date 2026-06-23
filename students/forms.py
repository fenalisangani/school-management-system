from django import forms
from django.utils import timezone

from classes.models import InstitutionType, Section, SchoolClass

from .models import Student, StudentDocument, StudentEnrollment


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'student_id', 'institution_type', 'full_name', 'date_of_birth', 'gender',
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
    institution_type = forms.ChoiceField(
        choices=InstitutionType.choices,
        initial=InstitutionType.SCHOOL,
        label='Student type',
        help_text='School uses sections only. College uses semester system.',
    )

    class Meta:
        model = StudentEnrollment
        fields = [
            'student', 'school_class', 'section', 'semester', 'academic_year',
            'admission_date', 'is_current', 'promotion_notes',
        ]
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date', 'value': timezone.localdate().isoformat()}),
            'semester': forms.Select(choices=[('', 'Not applicable')]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(status='active').order_by('full_name')

        inst = InstitutionType.SCHOOL
        if self.data.get('institution_type'):
            inst = self.data.get('institution_type')
        elif self.initial.get('institution_type'):
            inst = self.initial.get('institution_type')
        elif self.instance.pk and self.instance.school_class_id:
            inst = self.instance.school_class.institution_type

        self.fields['institution_type'].initial = inst
        self.fields['school_class'].queryset = SchoolClass.objects.filter(
            institution_type=inst,
            status='active',
        ).select_related('academic_year').order_by('name')
        self.fields['school_class'].label = 'Course' if inst == InstitutionType.COLLEGE else 'Class / Standard'
        self.fields['section'].label = 'Division / Section'

        class_id = self.data.get('school_class') or (
            self.instance.school_class_id if self.instance.pk else None
        )
        if class_id:
            self.fields['section'].queryset = Section.objects.filter(school_class_id=class_id)
            school_class = SchoolClass.objects.filter(pk=class_id).first()
            if school_class and school_class.uses_semesters:
                self.fields['semester'].required = True
                self.fields['semester'].widget = forms.Select(
                    choices=[('', 'Select semester')]
                    + [(n, f'Semester {n}') for n in school_class.get_semester_choices()]
                )
            else:
                self.fields['semester'].required = False
                self.fields['semester'].widget = forms.Select(
                    choices=[('', 'Not applicable (school)')]
                )
        else:
            self.fields['section'].queryset = Section.objects.none()
            self.fields['semester'].required = False

    def clean(self):
        cleaned = super().clean()
        institution = cleaned.get('institution_type')
        school_class = cleaned.get('school_class')
        section = cleaned.get('section')
        semester = cleaned.get('semester')

        if school_class and institution and school_class.institution_type != institution:
            raise forms.ValidationError(
                'The selected class/course does not match the student type.'
            )
        if school_class and section and section.school_class_id != school_class.id:
            raise forms.ValidationError('Division/section does not belong to the selected class/course.')
        if school_class and not cleaned.get('academic_year'):
            cleaned['academic_year'] = school_class.academic_year

        if school_class and school_class.uses_semesters:
            if not semester:
                raise forms.ValidationError('Semester is required for college enrollment.')
            max_sem = school_class.total_semesters
            if semester < 1 or semester > max_sem:
                raise forms.ValidationError(f'Semester must be between 1 and {max_sem}.')
        else:
            cleaned['semester'] = None

        return cleaned


class StudentDocumentForm(forms.ModelForm):
    class Meta:
        model = StudentDocument
        fields = ['student', 'document_type', 'title', 'file']
