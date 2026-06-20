from django import forms

from classes.models import Section

from .models import ClassTeacherAssignment, Teacher


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'teacher_id', 'full_name', 'qualification', 'years_experience',
            'phone', 'email', 'address', 'employment_status',
        ]
        widgets = {
            'teacher_id': forms.TextInput(attrs={'placeholder': 'Leave blank to auto-generate'}),
        }

    def clean_teacher_id(self):
        value = self.cleaned_data.get('teacher_id', '').strip()
        if not value:
            from core.utils import generate_unique_id
            value = generate_unique_id('TCH', Teacher, 'teacher_id')
        return value


class ClassTeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = ClassTeacherAssignment
        fields = [
            'teacher', 'school_class', 'section', 'subject', 'role', 'workload_hours',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.filter(employment_status='active')
        class_id = self.data.get('school_class') if self.data else None
        if class_id:
            self.fields['section'].queryset = Section.objects.filter(school_class_id=class_id)
        else:
            self.fields['section'].queryset = Section.objects.none()
        self.fields['section'].required = False
        self.fields['subject'].required = False
