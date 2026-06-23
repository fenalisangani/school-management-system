from django.db import models

from classes.models import AcademicYear, InstitutionType, SchoolClass, Section


class Gender(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'


class StudentStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    ALUMNI = 'alumni', 'Alumni'
    TRANSFER = 'transfer', 'Transfer'
    DROPPED = 'dropped', 'Dropped'


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    institution_type = models.CharField(
        max_length=10,
        choices=InstitutionType.choices,
        default=InstitutionType.SCHOOL,
        help_text='School student or college student.',
    )
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=Gender.choices)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    parent_name = models.CharField(max_length=150, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    parent_email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to='students/photos/', blank=True)
    status = models.CharField(
        max_length=10,
        choices=StudentStatus.choices,
        default=StudentStatus.ACTIVE,
    )

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f'{self.student_id} - {self.full_name}'


class DocumentType(models.TextChoices):
    ID_PROOF = 'id_proof', 'ID Proof'
    CERTIFICATE = 'certificate', 'Certificate'
    OTHER = 'other', 'Other'


class StudentDocument(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='students/documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.student_id} - {self.title}'


class StudentEnrollment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name='enrollments',
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name='enrollments',
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name='enrollments',
    )
    admission_date = models.DateField()
    is_current = models.BooleanField(default=True)
    semester = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='College only — semester number (1–8). Leave blank for school.',
    )
    promotion_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-admission_date']

    def __str__(self):
        base = f'{self.student} → {self.school_class} Sec {self.section.name}'
        if self.semester:
            return f'{base} (Sem {self.semester})'
        return base
