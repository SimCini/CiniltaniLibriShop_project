import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from ecommerce.models import Utente


class Command(BaseCommand):
    help = 'Importa utenti da un CSV esportato da WordPress'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Percorso del file CSV')

    def handle(self, *args, **kwargs):
        path = kwargs['csv_file']
        creati, esistenti, errori = 0, 0, 0

        with open(path, newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            reader.fieldnames = [h.strip() for h in reader.fieldnames]

            for i, row in enumerate(reader, start=1):
                username = row.get('user_login', '').strip()
                email = row.get('user_email', '').strip()

                if not username or not email:
                    self.stdout.write(self.style.WARNING(f"❌ Riga {i}: dati obbligatori mancanti"))
                    errori += 1
                    continue

                try:
                    data_reg = datetime.strptime(row['user_registered'], '%Y-%m-%d %H:%M:%S') if row.get('user_registered') else None
                    utente, creato = Utente.objects.get_or_create(username=username, defaults={
                        'email': email,
                        'data_registrazione': data_reg,
                        'nome': row.get('billing_first_name', '').strip(),
                        'cognome': row.get('billing_last_name', '').strip(),
                        'indirizzo': row.get('billing_address_1', '').strip(),
                        'cap': row.get('billing_postcode', '').strip(),
                        'citta': row.get('billing_city', '').strip(),
                        'provincia': row.get('billing_state', '').strip(),
                        'paese': row.get('billing_country', '').strip(),
                        'telefono': row.get('billing_phone', '').strip(),
                        'ruolo': 'cliente',
                    })

                    if creato:
                        utente.save()
                        self.stdout.write(f"✅ Utente creato: {username}")
                        creati += 1
                    else:
                        self.stdout.write(f"⚠️ Utente già esistente: {username}")
                        esistenti += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"❌ Riga {i} ({username}): errore - {e}"))
                    errori += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Importazione completata: {creati} creati, {esistenti} già presenti, {errori} errori."
        ))