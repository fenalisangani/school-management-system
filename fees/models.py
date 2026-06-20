from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone

from classes.models import AcademicYear, SchoolClass
from fees.currency import format_inr
from students.models import Student


class StudentCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'Student categories'

    def __str__(self):
        return self.name


class FeeFrequency(models.TextChoices):
    ONE_TIME = 'one_time', 'One Time'
    MONTHLY = 'monthly', 'Monthly'
    QUARTERLY = 'quarterly', 'Quarterly'
    ANNUAL = 'annual', 'Annual'


class FeeComponent(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    structure_id = models.CharField(max_length=20, unique=True)
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='fee_structures',
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name='fee_structures',
    )
    category = models.ForeignKey(
        StudentCategory,
        on_delete=models.PROTECT,
        related_name='fee_structures',
    )

    class Meta:
        unique_together = [['school_class', 'academic_year', 'category']]

    def __str__(self):
        return f'{self.structure_id} - {self.school_class} ({self.category})'

    @property
    def total_amount(self):
        return self.items.aggregate(total=Sum('amount'))['total'] or Decimal('0')


class FeeStructureItem(models.Model):
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
        related_name='items',
    )
    component = models.ForeignKey(FeeComponent, on_delete=models.PROTECT)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Amount (INR)',
        help_text='Fee amount in Indian Rupees.',
    )
    frequency = models.CharField(max_length=15, choices=FeeFrequency.choices)

    def __str__(self):
        return f'{self.component} - {format_inr(self.amount)}'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PARTIAL = 'partial', 'Partial'
    PAID = 'paid', 'Paid'


class StudentFeeAssignment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='fee_assignments',
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.PROTECT,
        related_name='student_assignments',
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Discount (INR)',
    )
    scholarship_notes = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    class Meta:
        unique_together = [['student', 'fee_structure']]

    def __str__(self):
        return f'{self.student} - {self.fee_structure}'

    @property
    def total_due(self):
        base = self.fee_structure.total_amount - self.discount_amount
        return max(base, Decimal('0'))

    @property
    def amount_paid(self):
        return self.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    @property
    def balance(self):
        return self.total_due - self.amount_paid

    def update_status(self):
        paid = self.amount_paid
        due = self.total_due
        if paid <= 0:
            self.status = PaymentStatus.PENDING
        elif paid >= due:
            self.status = PaymentStatus.PAID
        else:
            self.status = PaymentStatus.PARTIAL
        self.save(update_fields=['status'])


class PaymentMode(models.TextChoices):
    CASH = 'cash', 'Cash'
    ONLINE = 'online', 'Online'
    CHEQUE = 'cheque', 'Cheque'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'


class FeePayment(models.Model):
    assignment = models.ForeignKey(
        StudentFeeAssignment,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    receipt_number = models.CharField(max_length=30, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Amount (INR)')
    payment_mode = models.CharField(max_length=15, choices=PaymentMode.choices)
    installment_number = models.PositiveSmallIntegerField(default=1)
    late_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Late fee (INR)',
    )
    paid_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return self.receipt_number

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.assignment.update_status()
