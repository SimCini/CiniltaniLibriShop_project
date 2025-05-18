from .models import Carrello
from django.db.models import Sum

def carrello_item_count(request):
    if request.user.is_authenticated:
        item_count = Carrello.objects.filter(utente=request.user).aggregate(
            total=Sum('quantita')
        )['total'] or 0
    else:
        item_count = 0

    return {'carrello_item_count': item_count}