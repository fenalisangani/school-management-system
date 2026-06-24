from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from classes.models import InstitutionType, SchoolClass, Section

from core.report_helpers import default_report_dates


class ClassScopeFilterForm(forms.Form):
    """Filter records by class/course, division/section, and semester (college)."""

    institution_type = forms.ChoiceField(
        choices=[('', 'All types')] + list(InstitutionType.choices),
        required=False,
        label='Type',
    )
    school_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.filter(status='active').select_related('academic_year'),
        required=False,
        empty_label='All classes / courses',
        label='Class / course',
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        required=False,
        empty_label='All divisions',
        label='Division / section',
    )
    semester = forms.ChoiceField(
        required=False,
        choices=[('', 'All semesters')],
        label='Semester',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.data.get('institution_type') or self.initial.get('institution_type') or ''
        classes = SchoolClass.objects.filter(status='active').select_related('academic_year')
        if inst in ('school', 'college'):
            classes = classes.filter(institution_type=inst)

        class_id = self.data.get('school_class') or self.initial.get('school_class')
        self.fields['school_class'].queryset = classes.order_by('institution_type', 'name')

        if class_id:
            self.fields['section'].queryset = Section.objects.filter(
                school_class_id=class_id,
            ).order_by('name')
            school_class = SchoolClass.objects.filter(pk=class_id).first()
            if school_class and school_class.uses_semesters:
                self.fields['semester'].choices = [('', 'All semesters')] + [
                    (str(n), f'Semester {n}') for n in school_class.get_semester_choices()
                ]
            else:
                self.fields['semester'].choices = [('', 'Not applicable (school)')]
        else:
            self.fields['section'].queryset = Section.objects.none()

    def selected_semester(self):
        value = self.cleaned_data.get('semester') if hasattr(self, 'cleaned_data') else None
        if not value:
            value = self.data.get('semester') or self.initial.get('semester')
        if value in (None, ''):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None


class ReportFilterForm(ClassScopeFilterForm):
    """Class scope filters plus a date range for PDF / export reports."""

    date_from = forms.DateField(
        required=False,
        label='From date',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    date_to = forms.DateField(
        required=False,
        label='To date',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.data:
            today = timezone.localdate()
            self.fields['date_from'].initial = today.replace(day=1)
            self.fields['date_to'].initial = today

    def clean(self):
        cleaned = super().clean()
        date_from = cleaned.get('date_from')
        date_to = cleaned.get('date_to')
        default_from, default_to = default_report_dates()
        cleaned['date_from'] = date_from or default_from
        cleaned['date_to'] = date_to or default_to
        if cleaned['date_from'] > cleaned['date_to']:
            raise ValidationError('From date must be on or before To date.')
        return cleaned
