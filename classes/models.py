from django.db import models


class AcademicYear(models.Model):
    name = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = 'Academic years'

    def __str__(self):
        return self.name


class ClassStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'


class InstitutionType(models.TextChoices):
    SCHOOL = 'school', 'School'
    COLLEGE = 'college', 'College'


class ProgramType(models.TextChoices):
    SCHOOL = 'school', 'School (sections only — no semester)'
    UG_3YR = 'ug_3yr', 'Undergraduate — 3 years / 6 semesters'
    UG_4YR = 'ug_4yr_integrated', 'Integrated — 4 years / 8 semesters'
    PG_2YR = 'pg_2yr', 'Post Graduation — 2 years / 4 semesters'


PROGRAM_SEMESTER_COUNT = {
    ProgramType.SCHOOL: 0,
    ProgramType.UG_3YR: 6,
    ProgramType.UG_4YR: 8,
    ProgramType.PG_2YR: 4,
}


class SchoolClass(models.Model):
    class_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(
        max_length=100,
        help_text='School: Std 8, Std 9… · College: BCA, MCA, BBA…',
    )
    institution_type = models.CharField(
        max_length=10,
        choices=InstitutionType.choices,
        default=InstitutionType.SCHOOL,
    )
    program_type = models.CharField(
        max_length=20,
        choices=ProgramType.choices,
        default=ProgramType.SCHOOL,
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name='classes',
    )
    status = models.CharField(
        max_length=10,
        choices=ClassStatus.choices,
        default=ClassStatus.ACTIVE,
    )

    class Meta:
        verbose_name_plural = 'Classes & courses'
        ordering = ['institution_type', 'name']

    def __str__(self):
        kind = 'Course' if self.institution_type == InstitutionType.COLLEGE else 'Class'
        return f'{kind}: {self.name} ({self.academic_year})'

    @property
    def total_semesters(self):
        return PROGRAM_SEMESTER_COUNT.get(self.program_type, 0)

    @property
    def uses_semesters(self):
        return (
            self.institution_type == InstitutionType.COLLEGE
            and self.total_semesters > 0
        )

    def get_semester_choices(self):
        return list(range(1, self.total_semesters + 1))

    def display_label(self):
        if self.institution_type == InstitutionType.COLLEGE:
            return f'Course: {self.name}'
        return f'Class: {self.name}'


class Section(models.Model):
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='sections',
    )
    name = models.CharField(max_length=10)

    class Meta:
        ordering = ['name']
        unique_together = [['school_class', 'name']]

    def __str__(self):
        return f'{self.school_class.name} - Section {self.name}'


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    credit_hours = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.name}'


class ClassSubject(models.Model):
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='class_subjects',
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='class_allocations',
    )

    class Meta:
        unique_together = [['school_class', 'subject']]
        verbose_name = 'Subject allocation'

    def __str__(self):
        return f'{self.school_class} → {self.subject}'
