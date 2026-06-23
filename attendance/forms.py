from django import forms
from django.utils import timezone

from classes.models import InstitutionType, SchoolClass, Section

from .models import AttendanceRule, AttendanceStatus, StudentAttendance, TeacherAttendance


class StudentAttendanceForm(forms.ModelForm):
    institution_type = forms.ChoiceField(
        choices=InstitutionType.choices,
        initial=InstitutionType.SCHOOL,
        label='Student type',
    )

    class Meta:
        model = StudentAttendance
        fields = ['student', 'school_class', 'section', 'semester', 'subject', 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'value': timezone.localdate().isoformat()}),
            'semester': forms.Select(choices=[('', 'Not applicable')]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.data.get('institution_type') if self.data else InstitutionType.SCHOOL
        self.fields['school_class'].queryset = SchoolClass.objects.filter(
            institution_type=inst, status='active',
        )
        self.fields['school_class'].label = 'Course' if inst == InstitutionType.COLLEGE else 'Class / Standard'
        self.fields['section'].label = 'Division / Section'

        class_id = self.data.get('school_class') if self.data else None
        if class_id:
            self.fields['section'].queryset = Section.objects.filter(school_class_id=class_id)
            sc = SchoolClass.objects.filter(pk=class_id).first()
            if sc and sc.uses_semesters:
                self.fields['semester'].required = True
                self.fields['semester'].widget = forms.Select(
                    choices=[('', 'Select semester')]
                    + [(n, f'Semester {n}') for n in sc.get_semester_choices()]
                )
        else:
            self.fields['section'].queryset = Section.objects.none()
        self.fields['subject'].required = False


class BulkStudentAttendanceForm(forms.Form):
    institution_type = forms.ChoiceField(
        choices=InstitutionType.choices,
        initial=InstitutionType.SCHOOL,
        label='Student type',
    )
    school_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.none(),
        label='Class / Standard',
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        label='Division / Section',
    )
    semester = forms.ChoiceField(
        required=False,
        choices=[('', 'Not applicable')],
        label='Semester',
    )
    date = forms.DateField(
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    default_status = forms.ChoiceField(
        choices=AttendanceStatus.choices,
        initial=AttendanceStatus.PRESENT,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.data.get('institution_type') if self.data else InstitutionType.SCHOOL
        self.fields['school_class'].queryset = SchoolClass.objects.filter(
            institution_type=inst, status='active',
        ).select_related('academic_year')
        self.fields['school_class'].label = 'Course' if inst == InstitutionType.COLLEGE else 'Class / Standard'

        class_id = self.data.get('school_class') if self.data else None
        if class_id:
            self.fields['section'].queryset = Section.objects.filter(school_class_id=class_id)
            sc = SchoolClass.objects.filter(pk=class_id).first()
            if sc and sc.uses_semesters:
                self.fields['semester'].required = True
                self.fields['semester'].choices = [
                    ('', 'Select semester'),
                ] + [(str(n), f'Semester {n}') for n in sc.get_semester_choices()]
            else:
                self.fields['semester'].required = False
                self.fields['semester'].choices = [('', 'Not applicable (school)')]

    def clean(self):
        cleaned = super().clean()
        school_class = cleaned.get('school_class')
        semester = cleaned.get('semester')
        if school_class and school_class.uses_semesters:
            if not semester:
                raise forms.ValidationError('Select a semester for college attendance.')
            cleaned['semester'] = int(semester)
        else:
            cleaned['semester'] = None
        return cleaned


class TeacherAttendanceForm(forms.ModelForm):
    class Meta:
        model = TeacherAttendance
        fields = ['teacher', 'date', 'status', 'shift']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'value': timezone.localdate().isoformat()}),
        }


class AttendanceRuleForm(forms.ModelForm):
    class Meta:
        model = AttendanceRule
        fields = ['name', 'min_attendance_percentage', 'lock_after_time', 'is_active']
        widgets = {
            'lock_after_time': forms.TimeInput(attrs={'type': 'time'}),
        }
