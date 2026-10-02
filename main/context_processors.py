from django.conf import settings
from django.db.models import F

from config.auth_utils import get_group


def sinerafil(request):
    """Variabel global ba template: identidade ofisina, grupu (papél) no alerta stock."""
    ctx = {
        'SHOP_NAME': settings.SHOP_NAME,
        'SHOP_TAGLINE': settings.SHOP_TAGLINE,
        'SHOP_ADDRESS': settings.SHOP_ADDRESS,
        'SHOP_PHONE': settings.SHOP_PHONE,
    }
    user = request.user
    if user.is_authenticated:
        from pesa.models import Pesa
        ctx['group'] = get_group(user)
        ctx['alerta_stock'] = Pesa.objects.filter(is_active=True, stock__lte=F('stock_min')).count()
    return ctx
