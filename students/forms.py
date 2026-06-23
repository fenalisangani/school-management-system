from django import forms
from django.utils import timezone

from classes.models import AcademicYear, InstitutionType, Section, SchoolClass

from .models import Gender, Student, StudentDocument, StudentEnrollment


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


class StudentRegistrationForm(forms.Form):
    """Register a student and enroll in class/course + section/semester in one step."""

    institution_type = forms.ChoiceField(
        choices=InstitutionType.choices,
        initial=InstitutionType.SCHOOL,
        label='Student type',
        help_text='School: class + division · College: course + division + semester',
    )
    full_name = forms.CharField(max_length=150, label='Full name')
    student_id = forms.CharField(
        max_length=20,
        required=False,
        label='Student ID',
        help_text='Leave blank to auto-generate.',
        widget=forms.TextInput(attrs={'placeholder': 'Auto-generated if empty'}),
    )
    date_of_birth = forms.DateField(
        label='Date of birth',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    gender = forms.ChoiceField(choices=Gender.choices)
    phone = forms.CharField(max_length=20, label='Phone number')
    school_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.none(),
        label='Class / standard',
        help_text='Pick school class or college course.',
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        label='Division / section',
    )
    semester = forms.TypedChoiceField(
        choices=[('', 'Not applicable')],
        required=False,
        coerce=lambda x: int(x) if x else None,
        empty_value=None,
        label='Semester',
        help_text='Required for college courses only.',
    )
    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.filter(is_archived=False),
        widget=forms.HiddenInput(),
        required=False,
    )
    admission_date = forms.DateField(
        initial=timezone.localdate,
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        inst = InstitutionType.SCHOOL
        if self.data.get('institution_type'):
            inst = self.data.get('institution_type')
        elif self.initial.get('institution_type'):
            inst = self.initial.get('institution_type')

        self.fields['institution_type'].initial = inst
        self.fields['school_class'].queryset = SchoolClass.objects.filter(
            institution_type=inst,
            status='active',
        ).select_related('academic_year').order_by('name')
        self.fields['school_class'].label = 'Course' if inst == InstitutionType.COLLEGE else 'Class / standard'

        class_id = self.data.get('school_class') or self.initial.get('school_class')
        if class_id:
            self.fields['section'].queryset = Section.objects.filter(school_class_id=class_id)
            if self.initial.get('section'):
                self.fields['section'].initial = self.initial['section']
            school_class = SchoolClass.objects.filter(pk=class_id).first()
            if school_class and school_class.uses_semesters:
                self.fields['semester'].required = True
                self.fields['semester'].choices = [('', 'Select semester')] + [
                    (str(n), f'Semester {n}') for n in school_class.get_semester_choices()
                ]
                if self.initial.get('semester'):
                    self.fields['semester'].initial = str(self.initial['semester'])
            else:
                self.fields['semester'].required = False
                self.fields['semester'].choices = [('', 'Not applicable (school)')]
        else:
            self.fields['section'].queryset = Section.objects.none()
            self.fields['semester'].required = False
            self.fields['semester'].choices = [('', 'Select class/course first')]

        active_year = AcademicYear.objects.filter(is_active=True, is_archived=False).first()
        if active_year and not self.data.get('academic_year') and not self.initial.get('academic_year'):
            self.fields['academic_year'].initial = active_year.pk

    def clean_student_id(self):
        value = (self.cleaned_data.get('student_id') or '').strip()
        if not value:
            from core.utils import generate_unique_id
            value = generate_unique_id('STU', Student, 'student_id')
        elif Student.objects.filter(student_id=value).exists():
            raise forms.ValidationError('This student ID is already in use.')
        return value

    def clean(self):
        cleaned = super().clean()
        institution = cleaned.get('institution_type')
        school_class = cleaned.get('school_class')
        section = cleaned.get('section')
        semester = cleaned.get('semester')

        if school_class and institution and school_class.institution_type != institution:
            raise forms.ValidationError('The selected class/course does not match the student type.')
        if school_class and section and section.school_class_id != school_class.id:
            raise forms.ValidationError('Division/section does not belong to the selected class/course.')
        if school_class:
            cleaned['academic_year'] = school_class.academic_year
            if school_class.uses_semesters:
                if semester is None:
                    raise forms.ValidationError('Semester is required for college registration.')
                max_sem = school_class.total_semesters
                if semester < 1 or semester > max_sem:
                    raise forms.ValidationError(f'Semester must be between 1 and {max_sem}.')
            else:
                cleaned['semester'] = None
        if not cleaned.get('admission_date'):
            cleaned['admission_date'] = timezone.localdate()

        return cleaned

    def save(self):
        data = self.cleaned_data
        student = Student.objects.create(
            student_id=data['student_id'],
            institution_type=data['institution_type'],
            full_name=data['full_name'],
            date_of_birth=data['date_of_birth'],
            gender=data['gender'],
            phone=data['phone'],
            status='active',
        )
        StudentEnrollment.objects.filter(student=student, is_current=True).update(is_current=False)
        StudentEnrollment.objects.create(
            student=student,
            school_class=data['school_class'],
            section=data['section'],
            academic_year=data['academic_year'],
            admission_date=data['admission_date'],
            semester=data.get('semester'),
            is_current=True,
        )
        return student


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
