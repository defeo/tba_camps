from django import template
#from django.utils.safestring import mark_safe
from decimal import Decimal

register = template.Library()

@register.filter
def with_cents(dec):
    return dec.quantize(Decimal('0.01'))

@register.filter
def strip_cents(dec):
    return dec.to_integral() if dec == dec.to_integral() else dec
