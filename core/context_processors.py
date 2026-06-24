from django.conf import settings
from django.utils import timezone


def site_settings(request):
    now = timezone.localtime()
    path = request.path

    page_titles = {
        '/': ('Dashboard', 'Overview & quick actions'),
        '/classes/': ('Classes & Courses', 'Classes and courses'),
        '/students/': ('Students', 'Student records'),
        '/teachers/': ('Teachers', 'Faculty & assignments'),
        '/fees/': ('Fees', 'Billing & payments'),
        '/attendance/': ('Attendance', 'Daily records & reports'),
        '/admin/': ('Administration', 'System configuration'),
    }

    header_title = 'School Management System'
    header_subtitle = 'School management'

    for prefix, (title, subtitle) in page_titles.items():
        if prefix == '/' and path == '/':
            header_title, header_subtitle = title, subtitle
            break
        if prefix != '/' and path.startswith(prefix):
            header_title, header_subtitle = title, subtitle
            break

    return {
        'CURRENCY_CODE': getattr(settings, 'CURRENCY_CODE', 'INR'),
        'CURRENCY_SYMBOL': getattr(settings, 'CURRENCY_SYMBOL', '₹'),
        'current_year': now.year,
        'header_date': now.strftime('%a, %d %b %Y'),
        'header_time': now.strftime('%I:%M %p'),
        'header_title': header_title,
        'header_subtitle': header_subtitle,
        'static_assets_version': getattr(settings, 'STATIC_ASSETS_VERSION', '20260624c'),
        'build_commit': getattr(settings, 'BUILD_COMMIT', 'local'),
    }
