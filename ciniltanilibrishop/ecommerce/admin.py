from django.contrib import admin
from ecommerce.models import Prodotto, Utente, Ordine, ElementoOrdine
from django.contrib.auth.admin import UserAdmin

class ProdottoAdmin(admin.ModelAdmin):
    # Aggiungi i campi sui quali eseguire la ricerca
    search_fields = ['nome', 'descrizione', 'categoria']

    # Puoi anche personalizzare altri aspetti dell'admin, come l'ordinamento predefinito, la visualizzazione dei campi, ecc.
    list_display = ['nome', 'prezzo', 'categoria', 'quantita', 'disponibile']
    list_filter = ['categoria', 'disponibile']
    ordering = ['nome']

# Registrare il modello Prodotto con la configurazione admin personalizzata
admin.site.register(Prodotto, ProdottoAdmin)

class ElementoOrdineInline(admin.TabularInline):
    model = ElementoOrdine
    extra = 0  # Nessuna riga vuota aggiuntiva per default
    readonly_fields = ['prodotto', 'quantita', 'prezzo_unitario']  # opzionale, per impedire modifiche retroattive

@admin.register(Utente)
class UtenteAdmin(UserAdmin):
    model = Utente
    list_display = ['username', 'email', 'ruolo', 'is_staff', 'is_active']
    list_filter = ('ruolo', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informazioni personali', {'fields': ('nome', 'cognome', 'email', 'telefono', 'indirizzo', 'citta', 'cap', 'provincia', 'paese')}),
        ('Ruoli', {'fields': ('ruolo',)}),
        ('Permessi', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Date importanti', {'fields': ('last_login', 'date_joined', 'data_registrazione')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'ruolo', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

@admin.register(Ordine)
class OrdineAdmin(admin.ModelAdmin):
    list_display = ['numero_ordine', 'utente', 'data_ordine', 'stato', 'totale']
    list_filter = ['stato', 'data_ordine']
    search_fields = ['numero_ordine', 'utente__username', 'utente__email']
    inlines = [ElementoOrdineInline]
    readonly_fields = ['data_ordine', 'data_pagamento']  # opzionale, se le imposti da codice

@admin.register(ElementoOrdine)
class ElementoOrdineAdmin(admin.ModelAdmin):
    list_display = ['ordine', 'prodotto', 'quantita', 'prezzo_unitario']
    search_fields = ['ordine__numero_ordine', 'prodotto__nome']


