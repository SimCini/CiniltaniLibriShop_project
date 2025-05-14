from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
from .models import Prodotto, Utente, Ordine, Carrello
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils import timezone

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
    return render(request, 'profilo.html', context)

def visualizza_carrello(request):
    # Recupera tutti i prodotti nel carrello dell'utente
    carrello_prodotti = Carrello.objects.filter(utente=request.user)
    
    # Calcola subtotale (senza spese di spedizione)
    subtotale = 0
    for item in carrello_prodotti:
        prezzo_unitario = item.prodotto.prezzo_scontato if (item.prodotto.prezzo_scontato and 
                item.prodotto.prezzo_scontato < item.prodotto.prezzo) else item.prodotto.prezzo
        subtotale += prezzo_unitario * item.quantita
    
    
    # Calcola il totale finale
    totale = subtotale
    
    context = {
        'carrello_prodotti': carrello_prodotti,
        'subtotale': round(subtotale, 2),
        'totale': round(totale, 2),
    }
    
    return render(request, 'carrello_prova.html', context)

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

@login_required
def aggiorna_carrello(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(Carrello, id=item_id, utente=request.user)
        
        try:
            nuova_quantita = int(request.POST.get('quantita', 1))
            if 1 <= nuova_quantita <= 99:
                item.quantita = nuova_quantita
                item.save()
                
                # Se la richiesta è AJAX, restituisci i dati aggiornati
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    prezzo_unitario = (item.prodotto.prezzo_scontato 
                                     if item.prodotto.prezzo_scontato and 
                                     item.prodotto.prezzo_scontato < item.prodotto.prezzo 
                                     else item.prodotto.prezzo)
                    
                    totale_prodotto = prezzo_unitario * item.quantita
                    
                    # Ricalcola il totale del carrello
                    carrello_prodotti = Carrello.objects.filter(utente=request.user)
                    subtotale = 0
                    for cart_item in carrello_prodotti:
                        prod_prezzo = (cart_item.prodotto.prezzo_scontato 
                                     if cart_item.prodotto.prezzo_scontato and 
                                     cart_item.prodotto.prezzo_scontato < cart_item.prodotto.prezzo 
                                     else cart_item.prodotto.prezzo)
                        subtotale += prod_prezzo * cart_item.quantita
                    
                    spedizione_gratuita = subtotale >= 100
                    costo_spedizione = 0 if spedizione_gratuita else 5.90
                    totale = subtotale + costo_spedizione
                    
                    return JsonResponse({
                        'success': True,
                        'totale_prodotto': round(totale_prodotto, 2),
                        'subtotale': round(subtotale, 2),
                        'costo_spedizione': round(costo_spedizione, 2),
                        'spedizione_gratuita': spedizione_gratuita,
                        'totale': round(totale, 2),
                    })
        except (ValueError, TypeError):
            pass
            
    return redirect('ecommerce:visualizza_carrello')

@login_required
def rimuovi_dal_carrello(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(Carrello, id=item_id, utente=request.user)
        item.delete()
        
        # Se la richiesta è AJAX, restituisci un JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            carrello_prodotti = Carrello.objects.filter(utente=request.user)
            
            subtotale = 0
            for cart_item in carrello_prodotti:
                prod_prezzo = (cart_item.prodotto.prezzo_scontato 
                             if cart_item.prodotto.prezzo_scontato and 
                             cart_item.prodotto.prezzo_scontato < cart_item.prodotto.prezzo 
                             else cart_item.prodotto.prezzo)
                subtotale += prod_prezzo * cart_item.quantita
            
            spedizione_gratuita = subtotale >= 100
            costo_spedizione = 0 if spedizione_gratuita else 5.90
            totale = subtotale + costo_spedizione
            
            return JsonResponse({
                'success': True,
                'subtotale': round(subtotale, 2),
                'costo_spedizione': round(costo_spedizione, 2),
                'spedizione_gratuita': spedizione_gratuita,
                'totale': round(totale, 2),
                'carrello_vuoto': not carrello_prodotti.exists(),
            })
            
    return redirect('ecommerce:visualizza_carrello')

@login_required
def svuota_carrello(request):
    if request.method == 'POST':
        Carrello.objects.filter(utente=request.user).delete()
        
    return redirect('ecommerce:visualizza_carrello')

@login_required
def checkout(request):
    # Questa è una funzione placeholder per il checkout
    # In un'implementazione reale, qui gestiresti l'indirizzo di spedizione, il pagamento, ecc.
    carrello_prodotti = Carrello.objects.filter(utente=request.user)
    
    if not carrello_prodotti.exists():
        # Se il carrello è vuoto, reindirizza al carrello
        return redirect('ecommerce:visualizza_carrello')
    
    # Per ora, reindirizza semplicemente al carrello con un messaggio
    # In un'implementazione reale, renderizzeresti una pagina di checkout
    return render(request, 'carrello.html', {
        'carrello_prodotti': carrello_prodotti,
        'messaggio': 'Funzionalità di checkout in fase di sviluppo'
    })

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

def registrazione_view(request):
    if request.method == 'POST':
        nome= request.POST.get('nome')
        cognome= request.POST.get('cognome')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conferma_password = request.POST.get('conferma_password')

        # Verifica che le password coincidano
        if password != conferma_password:
            messages.error(request, 'Le password non coincidono.')
        
        # Verifica che username ed email siano unici
        elif Utente.objects.filter(username=username).exists():
            messages.error(request, 'Username già in uso.')
        elif Utente.objects.filter(email=email).exists():
            messages.error(request, 'Email già registrata.')
        
        else:
            utente = Utente.objects.create_user(
            username=username,
            email=email,
            password=password,
            nome=nome,
            cognome=cognome,
            ruolo='cliente',
            data_registrazione=timezone.now()
        )
            messages.success(request, 'Registrazione completata con successo!')
            return redirect('ecommerce:login')

    return render(request, 'registrati.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        utente = authenticate(request, username=username, password=password)
        print(f"Tentativo login con: {username} / {password}")
        print(f"Utente trovato: {utente}")

        if utente is not None:
            login(request, utente)
            messages.success(request, 'Accesso effettuato con successo!')
            return render(request, 'profilo.html', {'utente': utente})
        else:
            messages.error(request, 'Username o password non validi.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout effettuato con successo.')
    return redirect('ecommerce:homepage')