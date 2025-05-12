from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
from .models import Prodotto, Utente, Ordine, Carrello

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

@login_required
def visualizza_profilo(request):
    utente = request.user # L'oggetto Utente dell'utente loggato
    ordini = Ordine.objects.filter(utente=request.user).order_by('-data_ordine')
    context = {
        'utente': utente,
        'ordini': ordini,
    }
    return render(request, 'profilo_utente.html', context)

def logout(request):
    """
    Gestisce il logout dell'utente
    """
    logout(request)
    messages.info(request, 'Sei stato disconnesso con successo.')
    return redirect('homepage')

def visualizza_carrello(request):
    # Recupera tutti i prodotti nel carrello dell'utente
    carrello_prodotti = Carrello.objects.filter(utente=request.user)
    
    # Calcola il totale del carrello
    totale = sum(item.prodotto.prezzo * item.quantita for item in carrello_prodotti)

    return render(request, 'carrello.html', {
        'carrello_prodotti': carrello_prodotti,
        'totale': totale
    })

@login_required
def aggiungi_al_carrello(request, pk):
    prodotto = get_object_or_404(Prodotto, id=pk)
    
    # Se il prodotto è già nel carrello dell'utente, aumenta la quantità
    carrello_item, created = Carrello.objects.get_or_create(utente=request.user, prodotto=prodotto)
    
    if not created:
        # Se il prodotto è già nel carrello, incrementa la quantità
        carrello_item.quantita += 1
        carrello_item.save()
    
    return redirect('ecommerce:visualizza_carrello')

def aggiorna_carrello(request, pk):
    carrello = Carrello.objects.get(utente=request.user)  # Esempio di come ottenere il carrello dell'utente
    prodotto = Prodotto.objects.get(id=pk)  # Ottieni il prodotto tramite l'ID
    
    # Supponiamo che tu stia ricevendo la nuova quantità tramite POST
    nuova_quantita = int(request.POST.get('quantita'))
    
    # Trova l'articolo nel carrello
    carrello_item = carrello.items.get(prodotto=prodotto)
    
    # Aggiorna la quantità
    carrello_item.quantita = nuova_quantita
    carrello_item.save()

    # Redirigi indietro al carrello o dove vuoi
    return redirect('ecommerce:visualizza_carrello') 

def rimuovi_dal_carrello(request, pk):
    # Ottieni il carrello dell'utente
    try:
        # Trova l'articolo da rimuovere (questo dovrebbe essere un solo oggetto)
        carrello_item = Carrello.objects.get(utente=request.user, prodotto__id=pk)
        
        # Rimuovi l'articolo dal carrello
        carrello_item.delete()

        # Redirigi al carrello o alla pagina desiderata dopo la rimozione
        return redirect('ecommerce:visualizza_carrello')
    
    except Carrello.DoesNotExist:
        # Se l'oggetto non esiste, restituisci alla pagina del carrello senza modifiche
        return redirect('ecommerce:visualizza_carrello')

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

