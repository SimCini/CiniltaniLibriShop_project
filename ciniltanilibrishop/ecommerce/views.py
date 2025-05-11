from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
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
    '''
    prodotti = Prodotto.objects.filter(disponibile=True)
    prodotti_per_pagina = 20
    paginator = Paginator(prodotti, prodotti_per_pagina)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'catalogo.html', {'page_obj': page_obj})
    '''
    categoria = request.GET.get('categoria')
    prezzo_min = request.GET.get('prezzo_minimo')
    ordine = request.GET.get('ordine')

    prodotti = Prodotto.objects.filter(disponibile=True)
    if categoria and categoria != 'tutti':
        prodotti = prodotti.filter(categoria=categoria)
    
    if prezzo_min:
        try:
            prezzo_min = int(prezzo_min)
            prodotti = prodotti.filter(prezzo__gte=prezzo_min)
        except (TypeError, ValueError):
            prezzo_min = 0  # ignora valori non validi

    if ordine == 'prezzo_asc':
        prodotti = prodotti.order_by('prezzo')
    elif ordine == 'prezzo_desc':
        prodotti = prodotti.order_by('-prezzo')
    #elif ordine == 'recenti':
    #    prodotti = prodotti.order_by('-data_creazione')

    prodotti_per_pagina = 20
    paginator = Paginator(prodotti, prodotti_per_pagina)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categorie = [('tutti', 'Tutti')] + list(Prodotto.CATEGORIE)

    context = {
        'page_obj': page_obj,
        'categoria_attiva': categoria,
        'categorie': categorie,
        'prezzo_min': prezzo_min,
        'ordine_attivo': ordine,
    }
    return render(request, 'catalogo.html', context)

def dettaglio_prodotto(request, pk):
    prodotto = get_object_or_404(Prodotto, id=pk)  # Ottieni il prodotto per ID
    return render(request, 'dettaglio_prodotto.html', {'prodotto': prodotto})

def contatti(request):
    return render(request, 'contatti.html')

def profilo(request):
    return render(request, 'profilo_utente.html')

def risultati_ricerca(request):
    query = request.GET.get('q')
    #print("🔍 Query cercata:", query)
    prodotti = Prodotto.objects.filter(
        Q(nome__icontains=query) | Q(categoria__icontains=query)
    )
    #print("📦 Prodotti trovati:", prodotti.count())
    paginator = Paginator(prodotti, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'risultati_ricerca.html', {'page_obj': page_obj})