"""Indian Rupee (INR) formatting utilities."""

from decimal import Decimal, InvalidOperation

from django.conf import settings


def to_decimal(value):
    if value is None or value == '':
        return Decimal('0')
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal('0')


def format_inr(amount, *, symbol=None, show_paise=True):
    """
    Format amount in INR with Indian digit grouping (lakhs/crores style).
    Examples: 5000 -> ₹5,000.00 | 5500000 -> ₹55,00,000.00
    """
    symbol = symbol if symbol is not None else getattr(settings, 'CURRENCY_SYMBOL', '₹')
    dec = to_decimal(amount)
    sign = '-' if dec < 0 else ''
    dec = abs(dec)

    if show_paise:
        rupees_str, paise_str = f'{dec:.2f}'.split('.')
    else:
        rupees_str = str(int(dec))
        paise_str = ''

    if len(rupees_str) <= 3:
        grouped = rupees_str
    else:
        last_three = rupees_str[-3:]
        head = rupees_str[:-3]
        chunks = []
        while head:
            chunks.insert(0, head[-2:])
            head = head[:-2]
        grouped = ','.join(chunks + [last_three]) if chunks else last_three

    if show_paise:
        return f'{sign}{symbol}{grouped}.{paise_str}'
    return f'{sign}{symbol}{grouped}'
