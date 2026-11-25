from decimal import Decimal

from django import template
from django.utils.html import format_html

register = template.Library()

BADGES = {
    'registered': ('secondary', 'Rejistu'), 'diagnosed': ('info', 'Diagnóstiku'),
    'assigned': ('primary', 'Mekániku Hili'), 'in_progress': ('warning', 'Prosesu'),
    'completed': ('success', 'Remata'),
    'in': ('success', 'Tama'), 'out': ('danger', 'Sai'),
}


@register.filter
def usd(value):
    try:
        return '$ {:,.2f}'.format(Decimal(value or 0))
    except Exception:
        return value


@register.filter
def status_badge(value):
    """Badge Bootstrap ba status reparasaun / tipu movimentu stock."""
    css, label = BADGES.get(str(value), ('secondary', str(value)))
    return format_html('<span class="badge badge-{}">{}</span>', css, label)
