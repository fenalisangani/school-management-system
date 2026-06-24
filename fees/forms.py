from django import forms

from .models import (
    FeeComponent,
    FeePayment,
    FeeStructure,
    FeeStructureItem,
    PaymentStatus,
    StudentCategory,
    StudentFeeAssignment,
)

INR_ATTRS = {'step': '0.01', 'min': '0', 'placeholder': '0.00'}


class StudentCategoryForm(forms.ModelForm):
    class Meta:
        model = StudentCategory
        fields = ['name']


class FeeComponentForm(forms.ModelForm):
    class Meta:
        model = FeeComponent
        fields = ['name', 'code']


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['structure_id', 'school_class', 'academic_year', 'category']
        widgets = {
            'structure_id': forms.TextInput(attrs={'placeholder': 'Leave blank to auto-generate'}),
        }

    def clean_structure_id(self):
        value = self.cleaned_data.get('structure_id', '').strip()
        if not value:
            from core.utils import generate_unique_id
            value = generate_unique_id('FEE', FeeStructure, 'structure_id')
        return value


class FeeStructureItemForm(forms.ModelForm):
    class Meta:
        model = FeeStructureItem
        fields = ['component', 'amount', 'frequency']
        labels = {
            'amount': 'Amount',
        }
        help_texts = {
            'amount': 'Enter amount in ₹.',
        }
        widgets = {
            'amount': forms.NumberInput(attrs=INR_ATTRS),
        }


class StudentFeeAssignmentForm(forms.ModelForm):
    class Meta:
        model = StudentFeeAssignment
        fields = [
            'student', 'fee_structure', 'discount_amount',
            'scholarship_notes', 'due_date',
        ]
        labels = {
            'discount_amount': 'Discount',
        }
        help_texts = {
            'discount_amount': 'Scholarship or discount amount in ₹.',
        }
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'discount_amount': forms.NumberInput(attrs=INR_ATTRS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from students.models import Student
        self.fields['student'].queryset = Student.objects.filter(status='active').order_by('full_name')
        self.fields['fee_structure'].queryset = FeeStructure.objects.select_related(
            'school_class', 'academic_year', 'category',
        )


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = [
            'assignment', 'receipt_number', 'amount', 'payment_mode',
            'installment_number', 'late_fee', 'notes',
        ]
        labels = {
            'amount': 'Payment amount',
            'late_fee': 'Late fee',
        }
        help_texts = {
            'amount': 'Amount received in ₹.',
            'late_fee': 'Optional late fee in ₹.',
        }
        widgets = {
            'amount': forms.NumberInput(attrs=INR_ATTRS),
            'late_fee': forms.NumberInput(attrs=INR_ATTRS),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assignment'].queryset = StudentFeeAssignment.objects.filter(
            status__in=[PaymentStatus.PENDING, PaymentStatus.PARTIAL],
        ).select_related('student', 'fee_structure')
