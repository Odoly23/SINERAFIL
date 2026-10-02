from decimal import Decimal

from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter
def usd(value):
    try:
        return '$ {:,.2f}'.format(Decimal(value or 0))
    except Exception:
        return value


@register.filter
def status_badge(value):
    """Badge Bootstrap ba status servisu / tipu movimentu."""
    css = {'pendente': 'secondary', 'prosesu': 'warning', 'remata': 'success',
           'tama': 'success', 'sai': 'danger'}.get(str(value), 'secondary')
    return format_html('<span class="badge badge-{}">{}</span>', css, str(value).capitalize())
