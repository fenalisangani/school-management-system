from django.contrib import admin

from fees.currency import format_inr

from .models import (
    FeeComponent,
    FeePayment,
    FeeStructure,
    FeeStructureItem,
    StudentCategory,
    StudentFeeAssignment,
)


class FeeStructureItemInline(admin.TabularInline):
    model = FeeStructureItem
    extra = 1
    fields = ('component', 'amount', 'frequency')
    verbose_name = 'Fee line (INR)'
    verbose_name_plural = 'Fee lines (INR)'


@admin.register(StudentCategory)
class StudentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(FeeComponent)
class FeeComponentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('structure_id', 'school_class', 'academic_year', 'category', 'display_total_inr')
    list_filter = ('academic_year', 'category')
    inlines = [FeeStructureItemInline]

    @admin.display(description='Total (INR)')
    def display_total_inr(self, obj):
        return format_inr(obj.total_amount)


class PaymentInline(admin.TabularInline):
    model = FeePayment
    extra = 0
    readonly_fields = ('receipt_number',)
    fields = ('receipt_number', 'amount', 'payment_mode', 'late_fee', 'paid_at')


@admin.register(StudentFeeAssignment)
class StudentFeeAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'fee_structure', 'display_due_inr', 'display_paid_inr',
        'display_balance_inr', 'status', 'due_date',
    )
    list_filter = ('status',)
    inlines = [PaymentInline]

    @admin.display(description='Due (INR)')
    def display_due_inr(self, obj):
        return format_inr(obj.total_due)

    @admin.display(description='Paid (INR)')
    def display_paid_inr(self, obj):
        return format_inr(obj.amount_paid)

    @admin.display(description='Balance (INR)')
    def display_balance_inr(self, obj):
        return format_inr(obj.balance)


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_number', 'assignment', 'display_amount_inr',
        'display_late_fee_inr', 'payment_mode', 'paid_at',
    )
    list_filter = ('payment_mode',)

    @admin.display(description='Amount (INR)')
    def display_amount_inr(self, obj):
        return format_inr(obj.amount)

    @admin.display(description='Late fee (INR)')
    def display_late_fee_inr(self, obj):
        return format_inr(obj.late_fee)
