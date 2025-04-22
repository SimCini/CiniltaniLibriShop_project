from django.contrib import admin
from ecommerce.models import Prodotto, Utente

class ProdottoAdmin(admin.ModelAdmin):
    # Aggiungi i campi sui quali eseguire la ricerca
    search_fields = ['nome', 'descrizione', 'categoria']

    # Puoi anche personalizzare altri aspetti dell'admin, come l'ordinamento predefinito, la visualizzazione dei campi, ecc.
    list_display = ['nome', 'prezzo', 'categoria', 'quantita', 'disponibile']
    list_filter = ['categoria', 'disponibile']
    ordering = ['nome']

# Registrare il modello Prodotto con la configurazione admin personalizzata
admin.site.register(Prodotto, ProdottoAdmin)

admin.site.register(Utente)
