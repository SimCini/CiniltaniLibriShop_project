from django.db import models
from decimal import Decimal
#installare cloudinary su django (pip install cloudinary django-cloudinary-storage)


class Prodotto(models.Model):
    CATEGORIE = [
        ('libri', 'Libri'),
        ('oggettistica', 'Oggettistica'),
    ]

    SOTTOCATEGORIE_LIBRI = [
        ('vari', 'Vari'),
        ('religiosi', 'Religiosi'),
    ]

    SOTTOCATEGORIE_OGGETTISTICA = [
        ('cereria', 'Cereria'),
        ('immaginette', 'Immaginette'),
        ('santa_messa', 'Ostie e vino per S. Messa'),
        ('incenso', 'Incenso e carboncini'),
        ('oratorio', 'Oratorio estivo'),
        ('altro', 'Altro'),
    ]

    nome = models.CharField(max_length=120)
    descrizione = models.TextField(blank=True, null=True)
    prezzo = models.DecimalField(max_digits=10, decimal_places=2)
    foto = models.ImageField(upload_to="prodotti/")
    categoria = models.CharField(max_length=20, choices=CATEGORIE)
    sottocategoria = models.CharField(max_length=30)
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