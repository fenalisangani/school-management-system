import random
from datetime import date

from django.core.management.base import BaseCommand
from django.utils import timezone

from classes.models import AcademicYear, SchoolClass, Section
from students.models import Gender, Student, StudentEnrollment

FIRST_NAMES = [
    'Aarav', 'Vivaan', 'Aditya', 'Ananya', 'Diya', 'Ishaan', 'Kabir', 'Saanvi',
    'Myra', 'Reyansh', 'Aarohi', 'Anika', 'Vihaan', 'Riya', 'Arjun', 'Sara',
    'Kiara', 'Rohan', 'Tara', 'Dev', 'Meera', 'Karan', 'Pooja', 'Nikhil',
]

LAST_NAMES = [
    'Sharma', 'Verma', 'Patel', 'Gupta', 'Singh', 'Reddy', 'Nair', 'Iyer',
    'Mehta', 'Joshi', 'Kapoor', 'Malhotra', 'Chopra', 'Bose', 'Das', 'Rao',
]

CITIES = ['Mumbai', 'Delhi', 'Bengaluru', 'Pune', 'Chennai', 'Hyderabad', 'Kolkata']


class Command(BaseCommand):
    help = 'Add random student entries (default 5-10) with enrollment into an existing class/section.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=None,
            help='Exact number of students to create. Omit for a random number between 5 and 10.',
        )

    def handle(self, *args, **options):
        school_class = SchoolClass.objects.first()
        section = Section.objects.filter(school_class=school_class).first() if school_class else None
        year = AcademicYear.objects.filter(is_active=True).first() or AcademicYear.objects.first()

        if not (school_class and section and year):
            self.stdout.write(self.style.ERROR(
                'No class/section/academic year found. Run "py manage.py seed_demo" first.'
            ))
            return

        count = options['count'] or random.randint(5, 10)

        existing_ids = set(Student.objects.values_list('student_id', flat=True))
        next_num = 1
        created = 0

        for _ in range(count):
            while f'STU-{next_num:03d}' in existing_ids:
                next_num += 1
            student_id = f'STU-{next_num:03d}'
            existing_ids.add(student_id)
            next_num += 1

            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            full_name = f'{first} {last}'
            gender = random.choice([Gender.MALE, Gender.FEMALE, Gender.OTHER])
            dob = date(
                random.randint(2007, 2012),
                random.randint(1, 12),
                random.randint(1, 28),
            )

            student = Student.objects.create(
                student_id=student_id,
                full_name=full_name,
                date_of_birth=dob,
                gender=gender,
                address=f'{random.randint(1, 200)} MG Road, {random.choice(CITIES)}',
                phone=f'98{random.randint(10000000, 99999999)}',
                email=f'{first.lower()}.{last.lower()}{random.randint(1, 99)}@example.com',
                parent_name=f'{random.choice(FIRST_NAMES)} {last}',
                parent_phone=f'99{random.randint(10000000, 99999999)}',
                parent_email=f'parent.{last.lower()}{random.randint(1, 99)}@example.com',
            )
            StudentEnrollment.objects.create(
                student=student,
                school_class=school_class,
                section=section,
                academic_year=year,
                admission_date=timezone.localdate(),
                is_current=True,
            )
            created += 1
            self.stdout.write(f'  + {student_id}  {full_name}  ({gender})')

        self.stdout.write(self.style.SUCCESS(
            f'Created {created} random students, enrolled in {school_class.name} - Section {section.name}.'
        ))
