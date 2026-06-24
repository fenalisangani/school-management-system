"""Shared helpers for scoped PDF reports."""

from django.utils import timezone


def default_report_dates():
    today = timezone.localdate()
    return today.replace(day=1), today


def report_date_label(filter_form):
    if not filter_form.is_valid():
        start, end = default_report_dates()
        return f'{start:%d %b %Y} – {end:%d %b %Y}'
    date_from = filter_form.cleaned_data.get('date_from')
    date_to = filter_form.cleaned_data.get('date_to')
    if date_from and date_to:
        return f'{date_from:%d %b %Y} – {date_to:%d %b %Y}'
    if date_from:
        return f'From {date_from:%d %b %Y}'
    if date_to:
        return f'Up to {date_to:%d %b %Y}'
    start, end = default_report_dates()
    return f'{start:%d %b %Y} – {end:%d %b %Y}'


def scope_label(filter_form):
    if not filter_form.is_valid():
        return 'All classes / courses'
    parts = []
    sc = filter_form.cleaned_data.get('school_class')
    sec = filter_form.cleaned_data.get('section')
    sem = filter_form.selected_semester()
    inst = filter_form.cleaned_data.get('institution_type')
    if inst:
        parts.append('School' if inst == 'school' else 'College')
    if sc:
        parts.append(str(sc.name))
    if sec:
        parts.append(f'Division {sec.name}')
    if sem:
        parts.append(f'Semester {sem}')
    return ' · '.join(parts) if parts else 'All classes / courses'
