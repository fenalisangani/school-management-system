from django import forms
from django.utils import timezone

from classes.models import SchoolClass, Section

from .models import AttendanceRule, AttendanceStatus, StudentAttendance, TeacherAttendance


class StudentAttendanceForm(forms.ModelForm):
    class Meta:
        model = StudentAttendance
        fields = ['student', 'school_class', 'section', 'subject', 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'value': timezone.localdate().isoformat()}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_id = self.data.get('school_class') if self.data else None
        if class_id:
            self.fields['section'].queryset = Section.objects.filter(school_class_id=class_id)
        else:
            self.fields['section'].queryset = Section.objects.none()
        self.fields['subject'].required = False


class BulkStudentAttendanceForm(forms.Form):
    school_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.filter(status='active').select_related('academic_year'),
    )
    section = forms.ModelChoiceField(queryset=Section.objects.none())
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
        class_id = self.data.get('school_class') if self.data else None
        if class_id:
            self.fields['section'].queryset = Section.objects.filter(school_class_id=class_id)


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
