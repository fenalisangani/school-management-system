from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from attendance.models import AttendanceRule, AttendanceStatus, StudentAttendance
from classes.models import (
    AcademicYear,
    ClassSubject,
    InstitutionType,
    ProgramType,
    SchoolClass,
    Section,
    Subject,
)
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
    help = 'Load demo data for school + college (sections & semesters).'

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

        # ── School classes (Std 8–10, sections Class 1 & 2) ──
        school_classes = {}
        for std in ('Std 8', 'Std 9', 'Std 10'):
            sc = SchoolClass.objects.create(
                class_id=f'CLS-{std.replace(" ", "")}',
                name=std,
                institution_type=InstitutionType.SCHOOL,
                program_type=ProgramType.SCHOOL,
                academic_year=year,
            )
            Section.objects.create(school_class=sc, name='1')
            Section.objects.create(school_class=sc, name='2')
            school_classes[std] = sc

        std9 = school_classes['Std 9']
        eng = Subject.objects.create(code='ENG9', name='English', credit_hours=3)
        math = Subject.objects.create(code='MATH9', name='Mathematics', credit_hours=4)
        ClassSubject.objects.create(school_class=std9, subject=eng)
        ClassSubject.objects.create(school_class=std9, subject=math)

        # ── College courses with semester counts ──
        bca = SchoolClass.objects.create(
            class_id='CRS-BCA',
            name='BCA',
            institution_type=InstitutionType.COLLEGE,
            program_type=ProgramType.UG_3YR,
            academic_year=year,
        )
        btech = SchoolClass.objects.create(
            class_id='CRS-BTECH',
            name='B.Tech Integrated',
            institution_type=InstitutionType.COLLEGE,
            program_type=ProgramType.UG_4YR,
            academic_year=year,
        )
        mca = SchoolClass.objects.create(
            class_id='CRS-MCA',
            name='MCA',
            institution_type=InstitutionType.COLLEGE,
            program_type=ProgramType.PG_2YR,
            academic_year=year,
        )
        college_courses = [bca, btech, mca]
        for course in college_courses:
            Section.objects.create(school_class=course, name='1')
            Section.objects.create(school_class=course, name='2')

        py = Subject.objects.create(code='PY101', name='Python Programming', credit_hours=4)
        db = Subject.objects.create(code='DB201', name='Database Systems', credit_hours=3)
        ClassSubject.objects.create(school_class=bca, subject=py)
        ClassSubject.objects.create(school_class=bca, subject=db)
        ClassSubject.objects.create(school_class=mca, subject=db)

        # ── Teachers (school + college) ──
        school_teacher = Teacher.objects.create(
            teacher_id='TCH-S001',
            full_name='Mrs. Priya Sharma',
            qualification='B.Ed',
            years_experience=6,
            phone='555-0101',
            email='priya@school.edu',
        )
        college_teacher = Teacher.objects.create(
            teacher_id='TCH-C001',
            full_name='Dr. Rajesh Kumar',
            qualification='Ph.D Computer Science',
            years_experience=12,
            phone='555-0201',
            email='rajesh@college.edu',
        )
        ClassTeacherAssignment.objects.create(
            teacher=school_teacher,
            school_class=std9,
            section=std9.sections.first(),
            subject=math,
            role=TeacherRole.CLASS_TEACHER,
            workload_hours=24,
        )
        ClassTeacherAssignment.objects.create(
            teacher=college_teacher,
            school_class=bca,
            section=bca.sections.first(),
            subject=py,
            role=TeacherRole.SUBJECT_TEACHER,
            workload_hours=18,
        )

        # ── School students ──
        school_students = [
            ('STU-S001', 'Riya Patel'),
            ('STU-S002', 'Arjun Mehta'),
            ('STU-S003', 'Sneha Reddy'),
        ]
        sec9 = std9.sections.first()
        for sid, name in school_students:
            student = Student.objects.create(
                student_id=sid,
                institution_type=InstitutionType.SCHOOL,
                full_name=name,
                date_of_birth=date(2011, 3, 10),
                gender='female' if name.startswith('Riya') or name.startswith('Sneha') else 'male',
                parent_name='Parent of ' + name.split()[0],
                parent_phone='555-3000',
            )
            StudentEnrollment.objects.create(
                student=student,
                school_class=std9,
                section=sec9,
                academic_year=year,
                admission_date=date.today(),
                is_current=True,
            )
            StudentAttendance.objects.create(
                student=student,
                school_class=std9,
                section=sec9,
                date=timezone.localdate(),
                status=AttendanceStatus.PRESENT,
            )

        # ── College students (semester-based) ──
        college_students = [
            ('STU-C001', 'Amit Singh', bca, 1),
            ('STU-C002', 'Neha Gupta', bca, 3),
            ('STU-C003', 'Vikram Joshi', mca, 1),
            ('STU-C004', 'Kavya Nair', btech, 5),
        ]
        for sid, name, course, sem in college_students:
            student = Student.objects.create(
                student_id=sid,
                institution_type=InstitutionType.COLLEGE,
                full_name=name,
                date_of_birth=date(2002, 7, 20),
                gender='female' if name in ('Neha Gupta', 'Kavya Nair') else 'male',
                phone='555-4000',
                email=f'{sid.lower()}@college.edu',
            )
            sec = course.sections.first()
            StudentEnrollment.objects.create(
                student=student,
                school_class=course,
                section=sec,
                semester=sem,
                academic_year=year,
                admission_date=date.today(),
                is_current=True,
            )
            StudentAttendance.objects.create(
                student=student,
                school_class=course,
                section=sec,
                semester=sem,
                date=timezone.localdate(),
                status=AttendanceStatus.PRESENT,
            )

        # ── Fees (school + college) ──
        regular = StudentCategory.objects.create(name='Regular')
        tuition = FeeComponent.objects.create(name='Tuition Fees', code='TUITION')
        admission = FeeComponent.objects.create(name='Admission Fees', code='ADMISSION')

        for sc, amount in ((std9, '35000'), (bca, '65000')):
            structure = FeeStructure.objects.create(
                structure_id=f'FEE-{sc.class_id}',
                school_class=sc,
                academic_year=year,
                category=regular,
            )
            FeeStructureItem.objects.create(
                fee_structure=structure,
                component=tuition,
                amount=Decimal(amount),
                frequency=FeeFrequency.ANNUAL,
            )
            FeeStructureItem.objects.create(
                fee_structure=structure,
                component=admission,
                amount=Decimal('5000.00'),
                frequency=FeeFrequency.ONE_TIME,
            )

        student = Student.objects.filter(institution_type=InstitutionType.COLLEGE).first()
        structure = FeeStructure.objects.filter(school_class=bca).first()
        if student and structure:
            assignment = StudentFeeAssignment.objects.create(
                student=student,
                fee_structure=structure,
                due_date=date.today() + timedelta(days=30),
            )
            assignment.update_status()
            FeePayment.objects.create(
                assignment=assignment,
                receipt_number='RCP-DEMO-001',
                amount=Decimal('25000.00'),
                payment_mode=PaymentMode.CASH,
            )

        AttendanceRule.objects.create(
            name='Default Rule',
            min_attendance_percentage=Decimal('75.00'),
            is_active=True,
        )

        self.stdout.write(self.style.SUCCESS(
            'Demo data created: school (Std 8–10) + college (BCA 6 sem, B.Tech 8 sem, MCA 4 sem). '
            'Open the live site or http://127.0.0.1:8000/'
        ))
