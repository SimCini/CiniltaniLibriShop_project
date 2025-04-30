from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.db.models import Q
from .models import Prodotto

def login(request):
    return render(request, 'login.html')

def registrati(request):
    return render(request, 'registrati.html')

def homepage(request):
    return render(request, 'homepage.html')

def chi_sono(request):
    return render(request, 'chi_sono.html')

def catalogo(request):
    # Filtra i prodotti disponibili (o puoi aggiungere altri filtri)
    prodotti = Prodotto.objects.filter(disponibile=True)
    prodotti_per_pagina = 20
    paginator = Paginator(prodotti, prodotti_per_pagina)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'catalogo.html', {'page_obj': page_obj})
    
def dettaglio_prodotto(request, pk):
    prodotto = get_object_or_404(Prodotto, id=pk)  # Ottieni il prodotto per ID
    return render(request, 'dettaglio_prodotto.html', {'prodotto': prodotto})

def contatti(request):
    return render(request, 'contatti.html')

def risultati_ricerca(request):
    query = request.GET.get('q')
    #print("🔍 Query cercata:", query)
    prodotti = Prodotto.objects.filter(
        Q(nome__icontains=query) | Q(categoria__icontains=query)
    )
    #print("📦 Prodotti trovati:", prodotti.count())
    from django.core.paginator import Paginator
    paginator = Paginator(prodotti, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'risultati_ricerca.html', {'page_obj': page_obj})