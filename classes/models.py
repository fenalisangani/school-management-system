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


class SchoolClass(models.Model):
    class_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
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
        verbose_name_plural = 'Classes'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.academic_year})'


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
