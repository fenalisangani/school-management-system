from django import template

from fees.currency import format_inr

register = template.Library()


@register.filter(name='inr')
def inr_filter(value, arg=''):
    """{{ amount|inr }} or {{ amount|inr:"no_paise" }}"""
    return format_inr(value, show_paise=arg != 'no_paise')


@register.simple_tag(name='inr')
def inr_tag(amount, show_paise=True):
    return format_inr(amount, show_paise=show_paise)
