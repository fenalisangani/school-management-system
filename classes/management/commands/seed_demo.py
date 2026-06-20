from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from attendance.models import AttendanceRule, AttendanceStatus, StudentAttendance
from classes.models import AcademicYear, ClassSubject, SchoolClass, Section, Subject
from fees.models import (
    FeeComponent,
    FeeStructure,
    FeeStructureItem,
    FeeFrequency,
    PaymentMode,
    FeePayment,
    StudentCategory,
    StudentFeeAssignment,
)
from students.models import Student, StudentEnrollment
from teachers.models import ClassTeacherAssignment, Teacher, TeacherRole


class Command(BaseCommand):
    help = 'Load demo data so all modules work together immediately.'

    def handle(self, *args, **options):
        if AcademicYear.objects.exists():
            self.stdout.write(self.style.WARNING('Data already exists. Skipping seed (delete db or flush first).'))
            return

        year = AcademicYear.objects.create(
            name='2025-2026',
            start_date=date(2025, 4, 1),
            end_date=date(2026, 3, 31),
            is_active=True,
        )

        school_class = SchoolClass.objects.create(
            class_id='CLS-GRADE10',
            name='Grade 10',
            academic_year=year,
        )
        section_a = Section.objects.create(school_class=school_class, name='A')
        Section.objects.create(school_class=school_class, name='B')

        math = Subject.objects.create(code='MATH10', name='Mathematics', credit_hours=4)
        eng = Subject.objects.create(code='ENG10', name='English', credit_hours=3)
        ClassSubject.objects.create(school_class=school_class, subject=math)
        ClassSubject.objects.create(school_class=school_class, subject=eng)

        teacher = Teacher.objects.create(
            teacher_id='TCH-001',
            full_name='Dr. Jane Smith',
            qualification='M.Sc Mathematics',
            years_experience=8,
            phone='555-0100',
            email='jane@school.edu',
        )
        ClassTeacherAssignment.objects.create(
            teacher=teacher,
            school_class=school_class,
            section=section_a,
            subject=math,
            role=TeacherRole.SUBJECT_TEACHER,
            workload_hours=20,
        )

        students_data = [
            ('STU-001', 'Alice Johnson'),
            ('STU-002', 'Bob Williams'),
            ('STU-003', 'Carol Davis'),
        ]
        for sid, name in students_data:
            student = Student.objects.create(
                student_id=sid,
                full_name=name,
                date_of_birth=date(2010, 5, 15),
                gender='female' if 'Alice' in name or 'Carol' in name else 'male',
                phone='555-1000',
                parent_name='Parent of ' + name.split()[0],
                parent_phone='555-2000',
            )
            StudentEnrollment.objects.create(
                student=student,
                school_class=school_class,
                section=section_a,
                academic_year=year,
                admission_date=date.today(),
                is_current=True,
            )
            StudentAttendance.objects.create(
                student=student,
                school_class=school_class,
                section=section_a,
                date=timezone.localdate(),
                status=AttendanceStatus.PRESENT,
            )

        regular = StudentCategory.objects.create(name='Regular')
        StudentCategory.objects.create(name='Scholarship')
        tuition = FeeComponent.objects.create(name='Tuition Fees', code='TUITION')
        admission = FeeComponent.objects.create(name='Admission Fees', code='ADMISSION')

        structure = FeeStructure.objects.create(
            structure_id='FEE-G10-2025',
            school_class=school_class,
            academic_year=year,
            category=regular,
        )
        # Amounts in INR (Indian Rupees)
        FeeStructureItem.objects.create(
            fee_structure=structure,
            component=tuition,
            amount=Decimal('50000.00'),  # ₹50,000 annual tuition
            frequency=FeeFrequency.ANNUAL,
        )
        FeeStructureItem.objects.create(
            fee_structure=structure,
            component=admission,
            amount=Decimal('5000.00'),  # ₹5,000 one-time admission
            frequency=FeeFrequency.ONE_TIME,
        )

        student = Student.objects.first()
        assignment = StudentFeeAssignment.objects.create(
            student=student,
            fee_structure=structure,
            due_date=date.today() + timedelta(days=30),
        )
        assignment.update_status()

        FeePayment.objects.create(
            assignment=assignment,
            receipt_number='RCP-DEMO-001',
            amount=Decimal('20000.00'),  # ₹20,000 partial payment
            payment_mode=PaymentMode.CASH,
        )

        AttendanceRule.objects.create(
            name='Default Rule',
            min_attendance_percentage=Decimal('75.00'),
            is_active=True,
        )

        self.stdout.write(self.style.SUCCESS(
            'Demo data created: 1 class, 3 students, 1 teacher, fees, attendance. Open http://127.0.0.1:8000/'
        ))
