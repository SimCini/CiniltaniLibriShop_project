from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

#installare cloudinary su django (pip install cloudinary django-cloudinary-storage)


class Prodotto(models.Model):
    CATEGORIE = [
        ('libri', 'Libri'),
        ('oggettistica', 'Oggettistica'),
        ('cereria', 'Cereria'),
        ('immaginette', 'Immaginette'),
        ('santa_messa', 'Ostie e vino per S. Messa'),
        ('incenso-carboncini', 'Incenso e carboncini'),
        #('oratorio', 'Oratorio estivo'),
    ]

    CLASSI_SPEDIZIONE = [
        ('incenso-carboncini', 'Carboncini incenso'),
        ('libri', 'Libri'),
        ('oggettistica', 'Oggettistica'),
        ('vino', 'Vino'),
    ]

    nome = models.CharField(max_length=120)
    descrizione = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIE)

    prezzo = models.DecimalField(max_digits=10, decimal_places=2)
    prezzo_scontato = models.DecimalField(max_digits=10, decimal_places=2)
    
    foto = models.ImageField(upload_to="prodotti/")
    
    lunghezza_cm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    larghezza_cm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    altezza_cm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    peso_g = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    classe_spedizione = models.CharField(max_length=20, choices=CLASSI_SPEDIZIONE, blank=True, null=True)
    
    quantita = models.PositiveSmallIntegerField()
    disponibile = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    def get_sottocategorie_possibili(self):
        if self.categoria == 'libri':
            return [sc[0] for sc in self.SOTTOCATEGORIE_LIBRI]
        elif self.categoria == 'oggettistica':
            return [sc[0] for sc in self.SOTTOCATEGORIE_OGGETTISTICA]
        return []
    
    class Meta:
        verbose_name = "Prodotto"
        verbose_name_plural = "Prodotti"
    
class ImmagineProdotto(models.Model):
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE, related_name='immagini')
    url = models.ImageField(upload_to="prodotti/")  # oppure ImageField con storage esterno

    def __str__(self):
        return f"Immagine di {self.prodotto.nome}"
    
class Utente(AbstractUser):
    RUOLI = [
        ('amministratore', 'Amministratore'),
        ('cliente', 'Cliente'),
    ]

    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=50, blank=True)
    cognome = models.CharField(max_length=50, blank=True)
    ruolo = models.CharField(max_length=20, choices=RUOLI, default='cliente')

    data_registrazione = models.DateTimeField(null=True, blank=True)
    telefono_spedizione = models.CharField(max_length=20, blank=True)
    indirizzo_spedizione = models.CharField(max_length=255, blank=True)
    indirizzo_spedizione_2 = models.CharField(max_length=255, blank=True)
    citta_spedizione = models.CharField(max_length=100, blank=True)
    cap_spedizione = models.CharField(max_length=20, blank=True)
    stato_spedizione = models.CharField(max_length=100, blank=True)
    paese_spedizione = models.CharField(max_length=2, blank=True)  # es. 'IT'
    spesa_totale = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Utente"
        verbose_name_plural = "Utenti"

class Ordine(models.Model):
    STATUS_CHOICES = [
        ('on-hold', 'In attesa'),
        ('completed', 'Completato'),
        ('cancelled', 'Cancellato'),
        ('refunded', 'Rimborsato'),
        # Aggiungi altri stati rilevanti se necessario
    ]

    numero_ordine = models.PositiveIntegerField(unique=True)
    utente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ordini')
    data_ordine = models.DateTimeField()
    data_pagamento = models.DateTimeField(null=True, blank=True)
    stato = models.CharField(max_length=20, choices=STATUS_CHOICES)
    totale_spedizione = models.DecimalField(max_digits=10, decimal_places=2)
    totale_tasse = models.DecimalField(max_digits=10, decimal_places=2)
    totale = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Ordine"
        verbose_name_plural = "Ordini"
        ordering = ['-data_ordine']

    def __str__(self):
        return f"Ordine #{self.numero_ordine} - {self.utente.username}"
