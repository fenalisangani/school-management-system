from django.conf import settings
from django.db import models

from classes.models import SchoolClass, Section, Subject
from students.models import Student
from teachers.models import Teacher


class AttendanceStatus(models.TextChoices):
    PRESENT = 'present', 'Present'
    ABSENT = 'absent', 'Absent'
    LEAVE = 'leave', 'Leave'


class AttendanceRule(models.Model):
    name = models.CharField(max_length=100)
    min_attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=75)
    lock_after_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Attendance cannot be edited after this time.',
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class StudentAttendance(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT)
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Leave blank for daily class attendance.',
    )
    date = models.DateField()
    semester = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='College attendance — semester number. Blank for school.',
    )
    status = models.CharField(max_length=10, choices=AttendanceStatus.choices)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['student', 'date', 'subject']]
        ordering = ['-date']
        verbose_name_plural = 'Student attendance records'

    def __str__(self):
        return f'{self.student} - {self.date} - {self.status}'


class TeacherAttendance(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    date = models.DateField()
    status = models.CharField(max_length=10, choices=AttendanceStatus.choices)
    shift = models.CharField(max_length=50, blank=True)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = [['teacher', 'date']]
        ordering = ['-date']

    def __str__(self):
        return f'{self.teacher} - {self.date} - {self.status}'
