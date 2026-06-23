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
