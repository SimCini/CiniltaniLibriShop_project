from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Prodotto


def chi_sono(request):
    return render(request, 'chi_sono.html')

def catalogo_prodotti(request):
    # Filtra i prodotti disponibili (o puoi aggiungere altri filtri)
    prodotti = Prodotto.objects.filter(disponibile=True)
    
    return render(request, 'catalogo_prodotti.html', {'prodotti': prodotti})
    
def dettaglio_prodotto(request, pk):
    prodotto = get_object_or_404(Prodotto, id=pk)  # Ottieni il prodotto per ID
    return render(request, 'dettaglio_prodotto.html', {'prodotto': prodotto})