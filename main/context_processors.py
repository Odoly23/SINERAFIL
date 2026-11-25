from django.conf import settings
from django.db.models import F

from config.auth_utils import get_role


def sinerafil(request):
    """Variabel global ba template: identidade ofisina, papél (role) no alerta stock."""
    ctx = {
        'SHOP_NAME': settings.SHOP_NAME,
        'SHOP_TAGLINE': settings.SHOP_TAGLINE,
        'SHOP_ADDRESS': settings.SHOP_ADDRESS,
        'SHOP_PHONE': settings.SHOP_PHONE,
    }
    user = request.user
    if user.is_authenticated:
        from inventory.models import Part
        ctx['role'] = get_role(user)
        ctx['role_label'] = user.get_role_display()
        ctx['alert_stock'] = Part.objects.filter(stock__lte=F('minimum_stock')).count()
    return ctx
