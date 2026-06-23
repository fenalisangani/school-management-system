from django.conf import settings
from django.utils import timezone


def site_settings(request):
    now = timezone.localtime()
    path = request.path

    page_titles = {
        '/': ('Dashboard', 'School & college analytics workspace'),
        '/classes/': ('Classes & Courses', 'School standards · College programs'),
        '/students/': ('Students', 'School & college enrollment'),
        '/teachers/': ('Teachers', 'Faculty & assignments'),
        '/fees/': ('Fees', f'Billing in {getattr(settings, "CURRENCY_SYMBOL", "₹")} INR'),
        '/attendance/': ('Attendance', 'Daily records & reports'),
        '/admin/': ('Administration', 'System configuration'),
    }

    header_title = 'School Management System'
    header_subtitle = 'Institution management workspace'

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
        'app_version': getattr(settings, 'APP_VERSION', '1.0.0'),
        'header_date': now.strftime('%a, %d %b %Y'),
        'header_time': now.strftime('%I:%M %p'),
        'header_title': header_title,
        'header_subtitle': header_subtitle,
        'show_demo_login_hint': getattr(settings, 'SHOW_DEMO_LOGIN_HINT', settings.DEBUG),
    }
