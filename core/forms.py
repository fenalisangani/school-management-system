from django import forms

from classes.models import InstitutionType, SchoolClass, Section


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
