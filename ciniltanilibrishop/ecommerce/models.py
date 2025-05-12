from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

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
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=50, blank=True)
    cognome = models.CharField(max_length=50, blank=True)
    ruolo = models.CharField(max_length=20, choices=RUOLI, default='cliente')

    data_registrazione = models.DateTimeField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    indirizzo = models.CharField(max_length=255, blank=True)
    citta= models.CharField(max_length=100, blank=True)
    cap = models.CharField(max_length=20, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    paese = models.CharField(max_length=2, blank=True)  # es. 'IT'

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Utente"
        verbose_name_plural = "Utenti"

def ora_italiana_default():
    return timezone.now() + timedelta(hours=2)

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
    data_ordine = models.DateTimeField(default=ora_italiana_default())
    data_pagamento = models.DateTimeField(null=True, blank=True)
    stato = models.CharField(max_length=20, choices=STATUS_CHOICES)
    totale = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Ordine"
        verbose_name_plural = "Ordini"
        ordering = ['-data_ordine']

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)  # salva l'ordine prima per avere un ID
        self.totale = sum(riga.quantita * riga.prezzo_unitario for riga in self.righe.all())
        super().save(*args, **kwargs)

    @classmethod
    def crea_con_elementi(cls, utente, prodotti_quantita, stato='on-hold'):
        """
        Crea un ordine con una lista di tuple: [(prodotto, quantità), ...]
        """
        ordine = cls.objects.create(
            utente=utente,
            data_ordine=timezone.now(),
            stato=stato,
            totale=Decimal('0.00')  # sarà aggiornato dopo
        )

        totale = Decimal('0.00')
        for prodotto, quantita in prodotti_quantita:
            prezzo = prodotto.prezzo_scontato or prodotto.prezzo
            ElementoOrdine.objects.create(
                ordine=ordine,
                prodotto=prodotto,
                quantita=quantita,
                prezzo_unitario=prezzo
            )
            totale += prezzo * quantita

        ordine.totale = totale
        ordine.save()
        return ordine

    def __str__(self):
        return f"Ordine #{self.numero_ordine} - {self.utente.username}"

class ElementoOrdine(models.Model):
    ordine = models.ForeignKey(Ordine, on_delete=models.CASCADE, related_name='righe')
    prodotto = models.ForeignKey(Prodotto, on_delete=models.PROTECT)
    quantita = models.PositiveIntegerField(default=1)
    prezzo_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # prezzo al momento dell’acquisto

    def __str__(self):
        return f"{self.quantita} x {self.prodotto.nome} (Ordine #{self.ordine.numero_ordine})"

    class Meta:
        verbose_name = "Elemento ordine"
        verbose_name_plural = "Elementi ordine"

class Carrello(models.Model):
    utente = models.ForeignKey(Utente, on_delete=models.CASCADE)
    prodotto = models.ForeignKey(Prodotto, on_delete=models.CASCADE)
    quantita = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.prodotto.nome} - Quantità: {self.quantita}"