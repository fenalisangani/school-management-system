from django.http import JsonResponse

from .models import ClassSubject, InstitutionType, SchoolClass, Section


def api_institution_classes(request, institution):
    if institution not in (InstitutionType.SCHOOL, InstitutionType.COLLEGE):
        return JsonResponse({'error': 'Invalid institution type'}, status=400)
    classes = SchoolClass.objects.filter(
        institution_type=institution,
        status='active',
    ).select_related('academic_year').order_by('name')
    return JsonResponse([
        {
            'id': c.id,
            'name': c.name,
            'label': c.display_label(),
            'uses_semesters': c.uses_semesters,
            'total_semesters': c.total_semesters,
        }
        for c in classes
    ], safe=False)


def api_sections(request, class_id):
    sections = Section.objects.filter(school_class_id=class_id).order_by('name')
    return JsonResponse([
        {'id': s.id, 'name': s.name} for s in sections
    ], safe=False)


def api_class_meta(request, class_id):
    try:
        school_class = SchoolClass.objects.select_related('academic_year').get(pk=class_id)
    except SchoolClass.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    subjects = ClassSubject.objects.filter(school_class=school_class).select_related('subject')
    semesters = []
    if school_class.uses_semesters:
        semesters = [
            {'id': n, 'name': f'Semester {n}'}
            for n in school_class.get_semester_choices()
        ]
    return JsonResponse({
        'academic_year_id': school_class.academic_year_id,
        'academic_year_name': school_class.academic_year.name,
        'class_name': school_class.name,
        'institution_type': school_class.institution_type,
        'program_type': school_class.program_type,
        'uses_semesters': school_class.uses_semesters,
        'total_semesters': school_class.total_semesters,
        'semesters': semesters,
        'subjects': [
            {'id': cs.subject_id, 'code': cs.subject.code, 'name': cs.subject.name}
            for cs in subjects
        ],
    })
