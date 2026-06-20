from django.db import models

from classes.models import SchoolClass, Section, Subject


class EmploymentStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    ON_LEAVE = 'on_leave', 'On Leave'
    RESIGNED = 'resigned', 'Resigned'


class Teacher(models.Model):
    teacher_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)
    qualification = models.CharField(max_length=200, blank=True)
    years_experience = models.PositiveSmallIntegerField(default=0)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    employment_status = models.CharField(
        max_length=15,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
    )

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f'{self.teacher_id} - {self.full_name}'


class TeacherRole(models.TextChoices):
    SUBJECT_TEACHER = 'subject_teacher', 'Subject Teacher'
    CLASS_TEACHER = 'class_teacher', 'Class Teacher'
    ADMINISTRATOR = 'administrator', 'Administrator'


class ClassTeacherAssignment(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='teacher_assignments',
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='teacher_assignments',
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='teacher_assignments',
    )
    role = models.CharField(max_length=20, choices=TeacherRole.choices)
    workload_hours = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Teacher assignment'

    def __str__(self):
        parts = [str(self.teacher), str(self.school_class)]
        if self.section:
            parts.append(f'Sec {self.section.name}')
        if self.subject:
            parts.append(str(self.subject))
        return ' / '.join(parts)
