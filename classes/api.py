from django.http import JsonResponse

from .models import SchoolClass, Section, Subject, ClassSubject


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
    return JsonResponse({
        'academic_year_id': school_class.academic_year_id,
        'academic_year_name': school_class.academic_year.name,
        'class_name': school_class.name,
        'subjects': [
            {'id': cs.subject_id, 'code': cs.subject.code, 'name': cs.subject.name}
            for cs in subjects
        ],
    })
