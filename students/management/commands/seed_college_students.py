import random
from datetime import date

from django.core.management.base import BaseCommand
from django.utils import timezone

from classes.models import (
    AcademicYear,
    InstitutionType,
    ProgramType,
    SchoolClass,
    Section,
)
from students.models import Gender, Student, StudentEnrollment

COLLEGE_COURSES = [
    ('CRS-BCA', 'BCA', ProgramType.UG_3YR, 6),
    ('CRS-BTECH', 'B.Tech Integrated', ProgramType.UG_4YR, 8),
    ('CRS-MCA', 'MCA', ProgramType.PG_2YR, 4),
]

COLLEGE_STUDENTS = [
    ('STU-C101', 'Amit Singh', 'BCA', 1, Gender.MALE),
    ('STU-C102', 'Neha Gupta', 'BCA', 3, Gender.FEMALE),
    ('STU-C103', 'Rahul Desai', 'BCA', 5, Gender.MALE),
    ('STU-C104', 'Kavya Nair', 'B.Tech Integrated', 1, Gender.FEMALE),
    ('STU-C105', 'Vikram Joshi', 'B.Tech Integrated', 5, Gender.MALE),
    ('STU-C106', 'Priya Shah', 'B.Tech Integrated', 7, Gender.FEMALE),
    ('STU-C107', 'Sanjay Mehta', 'MCA', 1, Gender.MALE),
    ('STU-C108', 'Anjali Rao', 'MCA', 2, Gender.FEMALE),
]


class Command(BaseCommand):
    help = 'Create college courses (if missing) and add sample college students with enrollments.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=None,
            help='Extra random college students to add beyond the fixed demo set.',
        )

    def handle(self, *args, **options):
        year = AcademicYear.objects.filter(is_active=True).first() or AcademicYear.objects.first()
        if not year:
            self.stdout.write(self.style.ERROR('No academic year found. Run seed_demo first.'))
            return

        courses = {}
        for class_id, name, program, _sem_count in COLLEGE_COURSES:
            course, created = SchoolClass.objects.get_or_create(
                class_id=class_id,
                defaults={
                    'name': name,
                    'institution_type': InstitutionType.COLLEGE,
                    'program_type': program,
                    'academic_year': year,
                },
            )
            if created:
                Section.objects.create(school_class=course, name='1')
                Section.objects.create(school_class=course, name='2')
                self.stdout.write(self.style.SUCCESS(f'Created course: {name}'))
            courses[name] = course

        added = 0
        for sid, full_name, course_name, semester, gender in COLLEGE_STUDENTS:
            if Student.objects.filter(student_id=sid).exists():
                self.stdout.write(f'  skip {sid} (already exists)')
                continue
            course = courses[course_name]
            section = course.sections.order_by('name').first()
            Student.objects.create(
                student_id=sid,
                institution_type=InstitutionType.COLLEGE,
                full_name=full_name,
                date_of_birth=date(2001 + random.randint(0, 3), random.randint(1, 12), random.randint(1, 28)),
                gender=gender,
                phone=f'98{random.randint(10000000, 99999999)}',
                email=f'{sid.lower()}@college.edu',
                address=f'{random.randint(1, 99)} University Road, Pune',
            )
            student = Student.objects.get(student_id=sid)
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
            self.stdout.write(f'  + {sid}  {full_name}  {course_name} Sem {semester} Div {section.name}')

        extra = options.get('count')
        if extra:
            names = [
                ('Arnav', 'Kapoor'), ('Ishita', 'Bose'), ('Karan', 'Malhotra'),
                ('Sneha', 'Iyer'), ('Dev', 'Chopra'), ('Tanya', 'Das'),
            ]
            course_list = list(courses.values())
            existing = set(Student.objects.values_list('student_id', flat=True))
            n = 200
            for first, last in random.sample(names, min(extra, len(names))):
                while f'STU-C{n}' in existing:
                    n += 1
                sid = f'STU-C{n}'
                existing.add(sid)
                course = random.choice(course_list)
                sem = random.randint(1, course.total_semesters)
                section = random.choice(list(course.sections.all()))
                Student.objects.create(
                    student_id=sid,
                    institution_type=InstitutionType.COLLEGE,
                    full_name=f'{first} {last}',
                    date_of_birth=date(2000, 6, 15),
                    gender=random.choice([Gender.MALE, Gender.FEMALE]),
                    phone=f'97{random.randint(10000000, 99999999)}',
                    email=f'{first.lower()}.{last.lower()}@college.edu',
                )
                StudentEnrollment.objects.create(
                    student=Student.objects.get(student_id=sid),
                    school_class=course,
                    section=section,
                    semester=sem,
                    academic_year=year,
                    admission_date=timezone.localdate(),
                    is_current=True,
                )
                added += 1
                self.stdout.write(f'  + {sid}  {first} {last}  {course.name} Sem {sem}')

        self.stdout.write(self.style.SUCCESS(
            f'Done — {added} college student(s) added. '
            f'Total college students: {Student.objects.filter(institution_type=InstitutionType.COLLEGE).count()}'
        ))
