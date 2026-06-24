"""Apply class/section/semester scope filters from a ClassScopeFilterForm or GET params."""


def filter_attendance_queryset(queryset, form):
    if not form.is_valid():
        return queryset
    school_class = form.cleaned_data.get('school_class')
    section = form.cleaned_data.get('section')
    semester = form.selected_semester()
    inst = form.cleaned_data.get('institution_type')

    if inst:
        queryset = queryset.filter(school_class__institution_type=inst)
    if school_class:
        queryset = queryset.filter(school_class=school_class)
    if section:
        queryset = queryset.filter(section=section)
    if semester:
        queryset = queryset.filter(semester=semester)
    elif school_class and not school_class.uses_semesters:
        queryset = queryset.filter(semester__isnull=True)
    return queryset


def filter_enrollment_queryset(queryset, form):
    if not form.is_valid():
        return queryset
    school_class = form.cleaned_data.get('school_class')
    section = form.cleaned_data.get('section')
    semester = form.selected_semester()
    inst = form.cleaned_data.get('institution_type')

    if inst:
        queryset = queryset.filter(school_class__institution_type=inst)
    if school_class:
        queryset = queryset.filter(school_class=school_class)
    if section:
        queryset = queryset.filter(section=section)
    if semester:
        queryset = queryset.filter(semester=semester)
    elif school_class and not school_class.uses_semesters:
        queryset = queryset.filter(semester__isnull=True)
    return queryset


def apply_date_range(queryset, form, field_name):
    """Filter queryset by ReportFilterForm date_from / date_to."""
    if not form.is_valid():
        return queryset
    date_from = form.cleaned_data.get('date_from')
    date_to = form.cleaned_data.get('date_to')
    if date_from:
        queryset = queryset.filter(**{f'{field_name}__gte': date_from})
    if date_to:
        queryset = queryset.filter(**{f'{field_name}__lte': date_to})
    return queryset


def apply_payment_date_range(queryset, form):
    if not form.is_valid():
        return queryset
    date_from = form.cleaned_data.get('date_from')
    date_to = form.cleaned_data.get('date_to')
    if date_from:
        queryset = queryset.filter(paid_at__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(paid_at__date__lte=date_to)
    return queryset
