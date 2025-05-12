from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .models import Prodotto
from .forms import LoginForm, RegistrazioneForm


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        form.set_request(request) # Imposta l'oggetto request per il form
        if form.is_valid():
            user = form.cleaned_data['user']
            auth_login(request, user)
            messages.success(request, f'Benvenuto, {user.nome}!') # Usa il nome dell'utente
            return redirect('ecommerce:homepage')
        else:
            return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def registrati(request):
    if request.method == 'POST':
        form = RegistrazioneForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registrazione avvenuta con successo! Puoi effettuare il login.')
            return redirect('ecommerce:login')
        else:
            return render(request, 'registrati.html', {'form': form})
    else:
        form = RegistrazioneForm()
    return render(request, 'registrati.html', {'form': form})

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
def profilo(request):
    utente = request.user # L'oggetto Utente dell'utente loggato
    context = {
        'utente': utente,
    }
    return render(request, 'profilo_utente.html', context)

def visualizza_carrello(request):
    return render(request, 'carrello.html')

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
