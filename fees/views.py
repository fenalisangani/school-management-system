import csv

from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from core.view_helpers import confirm_delete, paginate, render_model_form

from .forms import (
    FeePaymentForm,
    FeeStructureForm,
    FeeStructureItemForm,
    StudentFeeAssignmentForm,
)
from .models import FeePayment, FeeStructure, FeeStructureItem, PaymentStatus, StudentFeeAssignment

FeeStructureItemFormSet = inlineformset_factory(
    FeeStructure,
    FeeStructureItem,
    form=FeeStructureItemForm,
    extra=3,
    can_delete=True,
)


def fee_structure_list(request):
    structures = FeeStructure.objects.select_related(
        'school_class', 'academic_year', 'category',
    ).prefetch_related('items__component').order_by('structure_id')
    query = request.GET.get('q', '').strip()
    if query:
        structures = structures.filter(
            Q(structure_id__icontains=query)
            | Q(school_class__name__icontains=query)
            | Q(category__name__icontains=query)
        )
    page_obj = paginate(request, structures)
    return render(request, 'fees/fee_structure_list.html', {
        'structures': page_obj,
        'page_obj': page_obj,
        'query': query,
    })


@transaction.atomic
def fee_structure_create(request):
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        formset = FeeStructureItemFormSet(request.POST)
    else:
        form = FeeStructureForm()
        formset = FeeStructureItemFormSet()

    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        structure = form.save()
        formset.instance = structure
        items = formset.save()
        if not any(items):
            messages.warning(request, 'Structure saved with no fee items. Add items in Admin or edit later.')
        else:
            messages.success(request, f'Fee structure {structure.structure_id} created with {len(items)} item(s).')
        return redirect('fee_structure_list')

    return render_model_form(
        request, form, 'Create Fee Structure', reverse('fee_structure_list'), formset=formset,
    )


@transaction.atomic
def fee_structure_edit(request, pk):
    structure = get_object_or_404(FeeStructure, pk=pk)
    if request.method == 'POST':
        form = FeeStructureForm(request.POST, instance=structure)
        formset = FeeStructureItemFormSet(request.POST, instance=structure)
    else:
        form = FeeStructureForm(instance=structure)
        formset = FeeStructureItemFormSet(instance=structure)

    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, f'Fee structure {structure.structure_id} updated.')
        return redirect('fee_structure_list')

    return render_model_form(
        request, form, f'Edit Fee Structure — {structure.structure_id}',
        reverse('fee_structure_list'), formset=formset,
    )


def fee_structure_delete(request, pk):
    structure = get_object_or_404(FeeStructure, pk=pk)
    return confirm_delete(request, structure, 'Fee Structure', reverse('fee_structure_list'))


def student_fee_list(request):
    assignments = StudentFeeAssignment.objects.select_related(
        'student', 'fee_structure__school_class', 'fee_structure__academic_year',
    ).order_by('student__full_name')
    status_filter = request.GET.get('status')
    if status_filter in PaymentStatus.values:
        assignments = assignments.filter(status=status_filter)
    query = request.GET.get('q', '').strip()
    if query:
        assignments = assignments.filter(
            Q(student__full_name__icontains=query)
            | Q(student__student_id__icontains=query)
        )
    page_obj = paginate(request, assignments)
    return render(request, 'fees/student_fee_list.html', {
        'assignments': page_obj,
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'status_choices': PaymentStatus.choices,
    })


def student_fee_delete(request, pk):
    assignment = get_object_or_404(StudentFeeAssignment, pk=pk)
    return confirm_delete(request, assignment, 'Fee Assignment', reverse('student_fee_list'))


def student_fee_assign(request):
    form = StudentFeeAssignmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        assignment = form.save()
        assignment.update_status()
        messages.success(request, 'Fees assigned to student.')
        return redirect('student_fee_list')
    return render_model_form(request, form, 'Assign Fees to Student', reverse('student_fee_list'))


def fee_payment_create(request):
    form = FeePaymentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        payment = form.save()
        messages.success(request, f'Payment recorded. Receipt: {payment.receipt_number}')
        return redirect('fee_receipt', pk=payment.pk)
    if request.method != 'POST':
        form = FeePaymentForm(initial={
            'receipt_number': f'RCP-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        })
    return render_model_form(request, form, 'Record Fee Payment', reverse('student_fee_list'))


def fee_receipt(request, pk):
    payment = get_object_or_404(
        FeePayment.objects.select_related(
            'assignment__student',
            'assignment__fee_structure__school_class',
            'assignment__fee_structure__academic_year',
            'assignment__fee_structure__category',
        ),
        pk=pk,
    )
    return render(request, 'fees/receipt.html', {'payment': payment})


def fee_report(request):
    payments = FeePayment.objects.select_related(
        'assignment__student', 'assignment__fee_structure',
    )
    total_collected = payments.aggregate(total=Sum('amount'))['total'] or 0
    defaulters = StudentFeeAssignment.objects.filter(
        status__in=[PaymentStatus.PENDING, PaymentStatus.PARTIAL],
    ).select_related('student', 'fee_structure')
    return render(request, 'fees/fee_report.html', {
        'payments': payments[:50],
        'total_collected': total_collected,
        'defaulters': defaulters,
    })


def fee_payments_export(request):
    """Download all fee payments as a CSV (opens in Excel)."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="fee_payments_{timezone.localdate()}.csv"'
    )
    writer = csv.writer(response)
    writer.writerow([
        'Receipt', 'Student ID', 'Student', 'Class', 'Structure',
        'Amount (INR)', 'Late Fee (INR)', 'Mode', 'Paid At',
    ])
    payments = FeePayment.objects.select_related(
        'assignment__student', 'assignment__fee_structure__school_class',
    ).order_by('-paid_at')
    for p in payments:
        writer.writerow([
            p.receipt_number,
            p.assignment.student.student_id,
            p.assignment.student.full_name,
            p.assignment.fee_structure.school_class.name,
            p.assignment.fee_structure.structure_id,
            p.amount,
            p.late_fee,
            p.get_payment_mode_display(),
            timezone.localtime(p.paid_at).strftime('%Y-%m-%d %H:%M'),
        ])
    return response
