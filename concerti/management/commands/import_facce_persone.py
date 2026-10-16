"""
Carica i ritratti da "FACCE DELLA GENTE 25-26-....zip" (foto nominate per cognome di
compositori/interpreti) sul campo Persona.ritratto corrispondente. Non tutte le
persone hanno una foto nello zip, e alcuni file non sono nominati esattamente come la
Persona in DB — la mappatura è esplicita qui sotto (verificata a mano).

Idempotente e non distruttivo: salta le Persona che hanno già un ritratto, non crea
nuove Persona.

Uso:
    manage.py import_facce_persone /percorso/alla/cartella/estratta --dry-run
    manage.py import_facce_persone /percorso/alla/cartella/estratta
"""
import os

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from concerti.models import Persona

# nome file nella cartella estratta -> (nome esatto Persona, ruolo)
MAPPING = {
    "emma photo.jpg": ("Emma Longo", "interprete"),
    "Chiara Ferraresi a colori.jpeg": ("Chiara Ferraresi", "compositore"),
    "Falascone.jpg": ("Giovanni Falascone", "compositore"),
    "AGRESTI.jpg": ("Maria Vittoria Agresti", "compositore"),
    "Rizza.JPG": ("Davide Rizza", "compositore"),
    "Gaia Aloisi.jpeg": ("Gaia Aloisi", "compositore"),
    "Foto MASSIMO.jpg": ("Massimo Restifo Pecorella", "interprete"),
    "Cenerini.jpg": ("Matteo Cenerini", "compositore"),
    "Broggini_ph.jpg": ("Davide Broggini", "compositore"),
    "Cattaneo.png": ("Giulio Cattaneo", "compositore"),
    "D_Agostino.jpg": ("Mariacostanza D'Agostino", "interprete"),
    # HEIC non è leggibile da Pillow/Django: usare la versione già convertita in .jpg
    # (stesso contenuto, vedi comando eseguito in sessione con ffmpeg).
    "Coiana.jpg": ("Antonio Coiana", "compositore"),
    "Elide_Sulsenti_Probe_08.web.jpeg": ("Elide Sulsenti", "interprete"),
}


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument("cartella", help="Cartella con i file immagine estratti dallo zip")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Esegue tutto ma non scrive (rollback a fine transazione).",
        )

    def handle(self, *args, **options):
        cartella = options["cartella"]
        if not os.path.isdir(cartella):
            raise CommandError(f"Cartella non trovata: {cartella}")

        caricate = non_trovate = gia_presenti = file_mancanti = 0

        with transaction.atomic():
            for filename, (nome, ruolo) in MAPPING.items():
                path = os.path.join(cartella, filename)
                if not os.path.isfile(path):
                    file_mancanti += 1
                    self.stdout.write(self.style.ERROR(f"FILE MANCANTE: {filename}"))
                    continue

                try:
                    persona = Persona.objects.get(nome=nome, ruolo=ruolo)
                except Persona.DoesNotExist:
                    non_trovate += 1
                    self.stdout.write(self.style.ERROR(f"NON TROVATA: {nome} ({ruolo})"))
                    continue

                if persona.ritratto:
                    gia_presenti += 1
                    self.stdout.write(f"  già presente, skip: {nome}")
                    continue

                if options["dry_run"]:
                    caricate += 1
                    self.stdout.write(self.style.SUCCESS(f"  (dry-run) caricherei: {nome} <- {filename}"))
                    continue

                ext = os.path.splitext(filename)[1].lower()
                target_name = f"{persona.pk}{ext}"
                with open(path, "rb") as f:
                    persona.ritratto.save(target_name, File(f), save=True)
                caricate += 1
                self.stdout.write(self.style.SUCCESS(f"  ritratto caricato: {nome}"))

            if options["dry_run"]:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(
            f"\nCaricate: {caricate} | già presenti: {gia_presenti} | "
            f"non trovate: {non_trovate} | file mancanti: {file_mancanti}"
        ))
        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("\n--dry-run: nessuna modifica salvata (rollback)."))
