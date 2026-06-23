"""Add demo entries for classes, students, attendance (7 days), and fee reports."""

import random
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
    FeeFrequency,
    FeePayment,
    FeeStructure,
    FeeStructureItem,
    PaymentMode,
    StudentCategory,
    StudentFeeAssignment,
)
from students.models import Gender, Student, StudentEnrollment


SCHOOL_CLASSES = [
    ('CLS-GRADE8', 'Grade 8', ('A', 'B')),
    ('CLS-GRADE9', 'Grade 9', ('A', 'B')),
    ('CLS-GRADE10', 'Grade 10', ('A', 'B')),
]

SCHOOL_STUDENTS = [
    ('STU-G10-001', 'Riya Patel', 'Grade 10', 'A', Gender.FEMALE, '9876501001'),
    ('STU-G10-002', 'Arjun Mehta', 'Grade 10', 'A', Gender.MALE, '9876501002'),
    ('STU-G10-003', 'Sneha Reddy', 'Grade 10', 'B', Gender.FEMALE, '9876501003'),
    ('STU-G10-004', 'Karan Malhotra', 'Grade 10', 'B', Gender.MALE, '9876501004'),
    ('STU-G10-005', 'Ananya Iyer', 'Grade 10', 'A', Gender.FEMALE, '9876501005'),
    ('STU-G9-001', 'Dev Sharma', 'Grade 9', 'A', Gender.MALE, '9876502001'),
    ('STU-G9-002', 'Pooja Nair', 'Grade 9', 'B', Gender.FEMALE, '9876502002'),
]

COLLEGE_STUDENTS = [
    ('STU-C201', 'Amit Singh', 'BCA', 1, 'A', Gender.MALE, '9876510001'),
    ('STU-C202', 'Neha Gupta', 'BCA', 3, 'A', Gender.FEMALE, '9876510002'),
    ('STU-C203', 'Rahul Desai', 'BCA', 5, 'B', Gender.MALE, '9876510003'),
    ('STU-C204', 'Kavya Nair', 'B.Tech Integrated', 1, 'A', Gender.FEMALE, '9876510004'),
    ('STU-C205', 'Vikram Joshi', 'B.Tech Integrated', 5, 'B', Gender.MALE, '9876510005'),
    ('STU-C206', 'Anjali Rao', 'MCA', 1, 'A', Gender.FEMALE, '9876510006'),
    ('STU-C207', 'Sanjay Mehta', 'MCA', 2, 'B', Gender.MALE, '9876510007'),
]


class Command(BaseCommand):
    help = 'Add sample classes, students, attendance history, and fee data (safe to re-run).'

    def handle(self, *args, **options):
        year = self._ensure_academic_year()
        school_map = self._ensure_school_classes(year)
        college_map = self._ensure_college_courses(year)
        self._ensure_subjects(school_map, college_map)
        students_added = 0
        students_added += self._add_school_students(year, school_map)
        students_added += self._add_college_students(year, college_map)
        attendance_added = self._seed_attendance_history()
        fees_added = self._seed_fee_data(year, school_map, college_map)
        self._ensure_attendance_rule()

        self.stdout.write(self.style.SUCCESS(
            f'Done — classes: {SchoolClass.objects.count()}, '
            f'students: {Student.objects.count()}, '
            f'attendance records: {StudentAttendance.objects.count()}, '
            f'(+{students_added} students, +{attendance_added} attendance, +{fees_added} fee rows this run)'
        ))

    def _ensure_academic_year(self):
        year, _ = AcademicYear.objects.get_or_create(
            name='2025-2026',
            defaults={
                'start_date': date(2025, 4, 1),
                'end_date': date(2026, 3, 31),
                'is_active': True,
            },
        )
        if not year.is_active:
            year.is_active = True
            year.save(update_fields=['is_active'])
        return year

    def _ensure_school_classes(self, year):
        result = {}
        for class_id, name, sections in SCHOOL_CLASSES:
            sc, _ = SchoolClass.objects.get_or_create(
                class_id=class_id,
                defaults={
                    'name': name,
                    'institution_type': InstitutionType.SCHOOL,
                    'program_type': ProgramType.SCHOOL,
                    'academic_year': year,
                },
            )
            for sec_name in sections:
                Section.objects.get_or_create(school_class=sc, name=sec_name)
            result[name] = sc
            self.stdout.write(f'  class ready: {name}')
        return result

    def _ensure_college_courses(self, year):
        specs = [
            ('CRS-BCA', 'BCA', ProgramType.UG_3YR),
            ('CRS-BTECH', 'B.Tech Integrated', ProgramType.UG_4YR),
            ('CRS-MCA', 'MCA', ProgramType.PG_2YR),
        ]
        result = {}
        for class_id, name, program in specs:
            sc, _ = SchoolClass.objects.get_or_create(
                class_id=class_id,
                defaults={
                    'name': name,
                    'institution_type': InstitutionType.COLLEGE,
                    'program_type': program,
                    'academic_year': year,
                },
            )
            for sec_name in ('A', 'B'):
                Section.objects.get_or_create(school_class=sc, name=sec_name)
            result[name] = sc
            self.stdout.write(f'  course ready: {name}')
        return result

    def _ensure_subjects(self, school_map, college_map):
        g10 = school_map.get('Grade 10')
        bca = college_map.get('BCA')
        if g10:
            eng, _ = Subject.objects.get_or_create(code='ENG10', defaults={'name': 'English', 'credit_hours': 3})
            math, _ = Subject.objects.get_or_create(code='MATH10', defaults={'name': 'Mathematics', 'credit_hours': 4})
            ClassSubject.objects.get_or_create(school_class=g10, subject=eng)
            ClassSubject.objects.get_or_create(school_class=g10, subject=math)
        if bca:
            py, _ = Subject.objects.get_or_create(code='PY101', defaults={'name': 'Python Programming', 'credit_hours': 4})
            ClassSubject.objects.get_or_create(school_class=bca, subject=py)

    def _add_school_students(self, year, school_map):
        added = 0
        for sid, name, class_name, section_name, gender, phone in SCHOOL_STUDENTS:
            if Student.objects.filter(student_id=sid).exists():
                continue
            sc = school_map[class_name]
            section = sc.sections.get(name=section_name)
            student = Student.objects.create(
                student_id=sid,
                institution_type=InstitutionType.SCHOOL,
                full_name=name,
                date_of_birth=date(2010, random.randint(1, 12), random.randint(1, 28)),
                gender=gender,
                phone=phone,
                parent_name=f'Parent of {name.split()[0]}',
                parent_phone='9898989898',
            )
            StudentEnrollment.objects.create(
                student=student,
                school_class=sc,
                section=section,
                academic_year=year,
                admission_date=timezone.localdate(),
                is_current=True,
            )
            added += 1
            self.stdout.write(f'  + school {sid} {name} -> {class_name} Div {section_name}')
        return added

    def _add_college_students(self, year, college_map):
        added = 0
        for sid, name, course_name, semester, section_name, gender, phone in COLLEGE_STUDENTS:
            if Student.objects.filter(student_id=sid).exists():
                continue
            course = college_map[course_name]
            section = course.sections.get(name=section_name)
            student = Student.objects.create(
                student_id=sid,
                institution_type=InstitutionType.COLLEGE,
                full_name=name,
                date_of_birth=date(2002, random.randint(1, 12), random.randint(1, 28)),
                gender=gender,
                phone=phone,
                email=f'{sid.lower()}@college.edu',
            )
            StudentEnrollment.objects.create(
                student=student,
                school_class=course,
                section=section,
                semester=semester,
                academic_year=year,
                admission_date=timezone.localdate(),
                is_current=True,
            )
            added += 1
            self.stdout.write(f'  + college {sid} {name} -> {course_name} Sem {semester} Div {section_name}')
        return added

    def _seed_attendance_history(self):
        added = 0
        today = timezone.localdate()
        statuses = [AttendanceStatus.PRESENT, AttendanceStatus.PRESENT, AttendanceStatus.PRESENT, AttendanceStatus.ABSENT]

        for enrollment in StudentEnrollment.objects.filter(is_current=True).select_related(
            'student', 'school_class', 'section',
        ):
            for day_offset in range(7):
                att_date = today - timedelta(days=day_offset)
                status = random.choice(statuses)
                _, created = StudentAttendance.objects.update_or_create(
                    student=enrollment.student,
                    school_class=enrollment.school_class,
                    section=enrollment.section,
                    subject=None,
                    date=att_date,
                    semester=enrollment.semester,
                    defaults={'status': status},
                )
                if created:
                    added += 1
        return added

    def _seed_fee_data(self, year, school_map, college_map):
        added = 0
        regular, _ = StudentCategory.objects.get_or_create(name='Regular')
        tuition, _ = FeeComponent.objects.get_or_create(name='Tuition Fees', code='TUITION')
        admission, _ = FeeComponent.objects.get_or_create(name='Admission Fees', code='ADMISSION')

        targets = [
            (school_map.get('Grade 10'), 'FEE-G10', Decimal('42000')),
            (college_map.get('BCA'), 'FEE-BCA', Decimal('65000')),
        ]
        for sc, fee_id, amount in targets:
            if not sc:
                continue
            structure = FeeStructure.objects.filter(
                school_class=sc,
                academic_year=year,
                category=regular,
            ).first()
            if not structure:
                structure = FeeStructure.objects.create(
                    structure_id=fee_id,
                    school_class=sc,
                    academic_year=year,
                    category=regular,
                )
                added += 1
            if not structure.items.exists():
                FeeStructureItem.objects.create(
                    fee_structure=structure,
                    component=tuition,
                    amount=amount,
                    frequency=FeeFrequency.ANNUAL,
                )
                FeeStructureItem.objects.create(
                    fee_structure=structure,
                    component=admission,
                    amount=Decimal('5000'),
                    frequency=FeeFrequency.ONE_TIME,
                )
                added += 2

            for enrollment in sc.enrollments.filter(is_current=True)[:3]:
                assignment, created = StudentFeeAssignment.objects.get_or_create(
                    student=enrollment.student,
                    fee_structure=structure,
                    defaults={'due_date': timezone.localdate() + timedelta(days=30)},
                )
                if created:
                    assignment.update_status()
                    added += 1
                if not assignment.payments.exists() and enrollment.student.student_id.endswith(('001', '201')):
                    FeePayment.objects.get_or_create(
                        assignment=assignment,
                        receipt_number=f'RCP-{assignment.pk}-DEMO',
                        defaults={
                            'amount': Decimal('15000'),
                            'payment_mode': PaymentMode.CASH,
                        },
                    )
                    assignment.update_status()
                    added += 1
        return added

    def _ensure_attendance_rule(self):
        AttendanceRule.objects.get_or_create(
            name='Default Rule',
            defaults={
                'min_attendance_percentage': Decimal('75.00'),
                'is_active': True,
            },
        )
