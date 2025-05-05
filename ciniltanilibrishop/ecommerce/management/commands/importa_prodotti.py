import csv
import os
import requests
from decimal import Decimal, InvalidOperation
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.core.management.base import BaseCommand
from ecommerce.models import Prodotto


# Mappature personalizzate
CATEGORIE_MAPPA = {
    'Libri': 'libri',
    'Oggettistica': 'oggettistica',
    'Cereria': 'cereria',
    'Immaginette': 'immaginette',
    'Ostie e vino per S. Messa': 'santa_messa',
    'Oratorio estivo': 'oratorio',
    'Abbigliamento': 'oggettistica',
    'Incenso e carboncini': 'incenso-carboncini',
    'Incenso': 'incenso-carboncini',
    'Carboncini': 'incenso-carboncini',
    'Oratorio estivo': 'oratorio',
}

CLASSE_SPEDIZIONE_MAPPA = {
    'carboncini': 'incenso-carboncini',
    'libri': 'libri',
    'oggettistica': 'oggettistica',
    'vino': 'vino',
}


class Command(BaseCommand):
    help = 'Importa prodotti da un CSV esportato da WordPress'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Percorso del file CSV')

    def handle(self, *args, **kwargs):
        path = kwargs['csv_file']

        with open(path, newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            reader.fieldnames = [h.strip() for h in reader.fieldnames]
            creati, esistenti, errori, aggiornati = 0, 0, 0, 0

            for i, row in enumerate(reader, start=1):
                nome = row.get('post_title', '').strip()
                descrizione = row.get('post_content', '').strip()
                prezzo = self.parse_decimal(row.get('regular_price'))
                prezzo_scontato = self.parse_decimal(row.get('sale_price'))

                lunghezza = self.parse_decimal(row.get('length'))
                larghezza = self.parse_decimal(row.get('width'))
                altezza = self.parse_decimal(row.get('height'))
                peso = self.parse_decimal(row.get('weight'))

                #categoria_raw = row.get('tax:product_cat', '').strip()
                #categoria = CATEGORIE_MAPPA.get(categoria_raw, 'oggettistica')
                categoria_raw = row.get('tax:product_cat', '')
                
                def normalizza(testo):
                    return testo.lower().strip().replace('  ', ' ').replace('ò', 'o').replace('à', 'a')
                
                categoria_norm = normalizza(categoria_raw)
                categoria = {normalizza(k): v for k, v in CATEGORIE_MAPPA.items()}.get(categoria_norm, 'oggettistica')

                classe_raw = row.get('tax:product_shipping_class', '').strip()
                classe_spedizione = CLASSE_SPEDIZIONE_MAPPA.get(classe_raw, None)

                disponibile = row.get('stock_status', '') == 'instock'
                try:
                    quantita = int(float(row.get('stock', 0))) if row.get('stock') else 0
                except ValueError:
                    quantita = 0

                if not nome:
                    self.stdout.write(self.style.WARNING(f"❌ Riga {i}: titolo mancante, saltata"))
                    errori += 1
                    continue

                if prezzo is None:
                    self.stdout.write(self.style.WARNING(f"❌ Riga {i} ({nome}): prezzo non valido, saltata"))
                    errori += 1
                    continue

                prodotto, creato = Prodotto.objects.get_or_create(nome=nome)

                if creato:
                    prodotto.descrizione = descrizione
                    prodotto.categoria = categoria
                    prodotto.classe_spedizione = classe_spedizione
                    prodotto.prezzo = prezzo
                    prodotto.prezzo_scontato = prezzo_scontato if prezzo_scontato else prezzo
                    prodotto.lunghezza_cm = lunghezza
                    prodotto.larghezza_cm = larghezza
                    prodotto.altezza_cm = altezza
                    prodotto.peso_g = peso
                    prodotto.quantita = quantita
                    prodotto.disponibile = disponibile
                    prodotto.save()
                    creati += 1
                    self.stdout.write(f"✅ Creato: {nome}")
                else:
                    aggiornato = False
                    if prodotto.categoria != categoria:
                        prodotto.categoria = categoria
                        aggiornato = True
                    if prodotto.classe_spedizione != classe_spedizione:
                        prodotto.classe_spedizione = classe_spedizione
                        aggiornato = True
                    if aggiornato:
                        prodotto.save()
                        aggiornati += 1
                        self.stdout.write(f"🔁 Aggiornato: {nome}")
                    else:
                        self.stdout.write(f"⚠️ Già esistente (nessuna modifica): {nome}")
                    esistenti += 1

                # Aggiorna l'immagine solo se il prodotto è stato creato o se l'immagine deve essere aggiornata
                image_urls = row.get('images', '').split(',')
                if image_urls and image_urls[0].strip():
                    self.salva_immagine_da_url(prodotto, image_urls[0].strip(), overwrite=True)

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Importazione completata: {creati} creati, {aggiornati} aggiornati, {esistenti} già presenti, {errori} errori."
        ))

    def salva_immagine_da_url(self, prodotto, url, overwrite=False):
        url_immagine = url.split(' ')[0].strip()  # Rimuove eventuali spazi extra
        print(f"URL immagine: {url_immagine}")  # Stampa per debug
        
        if not url_immagine or not url_immagine.lower().startswith('http'):
            self.stdout.write(self.style.WARNING(f"⚠️ Immagine non valida per {prodotto.nome}: {url_immagine}"))
            return

        try:
            # Scarica l'immagine dal URL
            resp = requests.get(url_immagine, timeout=10)
            
            # Controlla che il server abbia risposto correttamente
            resp.raise_for_status()
            
            # Verifica che la risposta sia effettivamente un'immagine
            if 'image' not in resp.headers.get('Content-Type', ''):
                self.stdout.write(self.style.WARNING(f"⚠️ Il contenuto non è un'immagine per {prodotto.nome}"))
                return
            
            print(f"Immagine scaricata correttamente da: {url_immagine}")

            # Usa io.BytesIO per trattare l'immagine in memoria senza creare un file temporaneo fisico
            from io import BytesIO
            image_data = BytesIO(resp.content)

            # Se l'immagine deve essere aggiornata
            if overwrite or not prodotto.foto:
                nome_file = os.path.basename(url_immagine.split('?')[0])  # Usa il nome del file dall'URL
                image_file = File(image_data, name=nome_file)  # Crea un oggetto File
                prodotto.foto.save(nome_file, image_file, save=True)
                self.stdout.write(f"✅ Immagine aggiornata per {prodotto.nome}")
                print(f"URL immagine salvata: {prodotto.foto.url}")
                
        except requests.exceptions.RequestException as e:
            # Errori di rete o di accesso al file
            self.stdout.write(self.style.WARNING(f"⚠️ Immagine non scaricata per {prodotto.nome}: {e}"))
        except Exception as e:
            # Altri errori generici
            self.stdout.write(self.style.WARNING(f"⚠️ Errore durante il salvataggio dell'immagine per {prodotto.nome}: {e}"))

    def parse_decimal(self, val):
        try:
            return Decimal(val.strip().replace(",", ".")) if val and val.strip().lower() != 'nan' else None
        except (InvalidOperation, AttributeError):
            return None

    