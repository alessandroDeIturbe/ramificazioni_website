"""
Importa nel DB i dati dei 4 programmi di sala 2025/26 (compositori, brani, interpreti)
estratti dai PDF in "PROGRAMMI SALA-20260913T144404Z-1-001.zip" (root del repo).

Idempotente: rieseguirlo non duplica nulla. Per i concerti già presenti in DB, corregge
(senza duplicare) eventuali righe Brano con compositore/titolo invertiti, invece di
crearne di nuove.

Uso:
    manage.py import_programmi_sala --dry-run   # solo report, nessuna scrittura
    manage.py import_programmi_sala             # scrive per davvero
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from concerti.models import Brano, Concerto, Partecipazione, Persona, Sede

SEDE_NOME = "Conservatorio della Svizzera Italiana"

DATA = [
    {
        "stagione": "2025/26",
        "numero_edizione": 1,
        "data": "2025-12-04",
        "ora": "19:00",
        "pubblicato": True,
        "interpreti": [
            {"nome": "Engin Mevsin", "ruolo": "interprete", "strumento": "Viola"},
            {"nome": "Ella Biscari", "ruolo": "interprete", "strumento": "Violino"},
            {"nome": "Davide Bardi", "ruolo": "interprete", "strumento": "Elettronica"},
        ],
        "brani": [
            {"compositore": "Máté Balogh", "titolo": "Three Songs", "prima": ""},
            {"compositore": "Alessandro De Iturbe", "titolo": "Breve florilegio tecnico n. 1", "prima": "assoluta"},
            {"compositore": "Giulio Cattaneo", "titolo": "Il canto degli esseri altri", "prima": ""},
            {"compositore": "Maurizio Azzan", "titolo": "Diptych #1", "prima": ""},
            {"compositore": "Agostino Di Scipio", "titolo": "Violazioni della presenza", "prima": ""},
            {"compositore": "Cristiano Pomante", "titolo": "Instru-mental-ization¡", "prima": "assoluta"},
        ],
    },
    {
        "stagione": "2025/26",
        "numero_edizione": 2,
        "data": "2026-02-05",
        "ora": "19:00",
        "pubblicato": True,
        "interpreti": [
            {"nome": "Edoardo Casali", "ruolo": "interprete", "strumento": "Fagotto"},
            {"nome": "Manuel Teles", "ruolo": "interprete", "strumento": "Sassofono"},
        ],
        "brani": [
            {"compositore": "Pier Luigi Billone", "titolo": "Legno. Edre.: I. ME.", "prima": ""},
            {"compositore": "Filippo Lepre", "titolo": "Binario di Azione Binaria", "prima": ""},
            {"compositore": "Francesco Fausto Magaletti", "titolo": "Attraverso gli Attimi", "prima": "assoluta"},
            {"compositore": "Floriana Provenzano", "titolo": "Calce, luce, squarci", "prima": "assoluta"},
        ],
    },
    {
        "stagione": "2025/26",
        "numero_edizione": 3,
        "data": "2026-03-12",
        "ora": None,
        "pubblicato": False,
        "interpreti": [
            {"nome": "Massimo Restifo Pecorella", "ruolo": "interprete", "strumento": "Clarinetto"},
            {"nome": "Elide Sulsenti", "ruolo": "interprete", "strumento": "Violoncello"},
        ],
        "brani": [
            {"compositore": "Federico Pezzatini", "titolo": "Fossils, like slits in time", "prima": "assoluta"},
            {"compositore": "Maria Vittoria Agresti", "titolo": "Must I?", "prima": "assoluta"},
            {"compositore": "Gaia Aloisi", "titolo": "dual [ii]", "prima": "assoluta"},
            {"compositore": "Cesare Saldicco", "titolo": "IRIN", "prima": ""},
            {"compositore": "Giovanni Falascone", "titolo": "CALCO (Ecografie)", "prima": "assoluta"},
            {"compositore": "Davide Broggini", "titolo": "[a]synchronous", "prima": "assoluta"},
            {"compositore": "Matteo Tundo", "titolo": "Cuoio", "prima": ""},
        ],
    },
    {
        "stagione": "2025/26",
        "numero_edizione": 4,
        "data": "2026-05-07",
        "ora": None,
        "pubblicato": False,
        "interpreti": [
            {"nome": "Mariacostanza D'Agostino", "ruolo": "interprete", "strumento": "Pianoforte"},
            {"nome": "Antonia De Pasquale", "ruolo": "interprete", "strumento": "Pianoforte"},
            {"nome": "Clara Dossena", "ruolo": "interprete", "strumento": "Danzatrice"},
            {"nome": "Emma Longo", "ruolo": "interprete", "strumento": "Flauto"},
            {"nome": "Francesca Seggioli", "ruolo": "regia_audio", "strumento": ""},
        ],
        "brani": [
            {"compositore": "Chiara Ferraresi", "titolo": "da Bis, pezzi brevi per pianoforte n.I, II", "prima": "assoluta"},
            {"compositore": "Giulio Cattaneo", "titolo": "Atlantide I", "prima": "assoluta"},
            {"compositore": "Davide Rizza", "titolo": "tape, skin, piano", "prima": "assoluta"},
            {"compositore": "Matteo Cenerini", "titolo": "En plein air", "prima": "assoluta"},
            {"compositore": "Antonio Coiana", "titolo": "Studio in forma di fiamma", "prima": "assoluta"},
            {"compositore": "Francesco Fiorenzani", "titolo": "Trenodia per Zaytoun", "prima": ""},
        ],
    },
]


def norm(compositore, titolo):
    return (compositore.strip().casefold(), titolo.strip().casefold())


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Esegue tutto ma non scrive (rollback a fine transazione).",
        )

    def handle(self, *args, **options):
        stats = {"concerto": [0, 0], "persona": [0, 0], "brano": [0, 0, 0], "partecipazione": [0, 0]}
        # [creati, già esistenti] per concerto/persona/partecipazione; [creati, corretti, già ok] per brano

        with transaction.atomic():
            try:
                sede = Sede.objects.get(nome=SEDE_NOME)
            except Sede.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    f"Sede '{SEDE_NOME}' non trovata in DB: creala prima a mano, non indovino l'indirizzo."
                ))
                return

            for entry in DATA:
                self.stdout.write(f"\n== Edizione {entry['numero_edizione']} — {entry['data']} ==")

                concerto, created = Concerto.objects.get_or_create(
                    stagione=entry["stagione"],
                    numero_edizione=entry["numero_edizione"],
                    defaults={
                        "data": entry["data"],
                        "ora": entry["ora"],
                        "sede": sede,
                        "pubblicato": entry["pubblicato"],
                    },
                )
                stats["concerto"][0 if created else 1] += 1
                self.stdout.write(
                    f"  Concerto: {'CREATO' if created else 'già esistente, riuso'}"
                )

                persone_per_concerto = {}  # nome -> Persona, per evitare doppie Partecipazione nello stesso concerto

                def get_persona(nome, ruolo, strumento):
                    persona, created = Persona.objects.get_or_create(
                        nome=nome, ruolo=ruolo, defaults={"strumento": strumento},
                    )
                    stats["persona"][0 if created else 1] += 1
                    if created:
                        self.stdout.write(f"    Persona CREATA: {nome} ({ruolo})")
                    return persona

                def get_partecipazione(persona, ordine):
                    if persona.pk in persone_per_concerto:
                        return
                    persone_per_concerto[persona.pk] = persona
                    _, created = Partecipazione.objects.get_or_create(
                        concerto=concerto, persona=persona,
                        defaults={"strumento_in_concerto": "", "ordine": ordine},
                    )
                    stats["partecipazione"][0 if created else 1] += 1

                for i, interprete in enumerate(entry["interpreti"]):
                    persona = get_persona(interprete["nome"], interprete["ruolo"], interprete["strumento"])
                    get_partecipazione(persona, i)

                esistenti = list(concerto.brani.all())
                matched_pks = set()
                prossimo_ordine = max((b.ordine for b in esistenti), default=0) + 1

                for i, item in enumerate(entry["brani"], start=1):
                    diretta = norm(item["compositore"], item["titolo"])
                    trovato = next((b for b in esistenti if norm(b.compositore, b.titolo) == diretta), None)
                    if trovato:
                        matched_pks.add(trovato.pk)
                        stats["brano"][2] += 1
                        persona = get_persona(item["compositore"], "compositore", "")
                        get_partecipazione(persona, 100 + i)
                        continue

                    invertita = norm(item["titolo"], item["compositore"])
                    invertito = next((b for b in esistenti if norm(b.compositore, b.titolo) == invertita), None)
                    if invertito:
                        invertito.compositore = item["compositore"]
                        invertito.titolo = item["titolo"]
                        invertito.prima_esecuzione_tipo = item["prima"]
                        invertito.save()
                        matched_pks.add(invertito.pk)
                        stats["brano"][1] += 1
                        self.stdout.write(self.style.WARNING(
                            f"    Brano CORRETTO (era invertito): {item['compositore']} — {item['titolo']}"
                        ))
                        persona = get_persona(item["compositore"], "compositore", "")
                        get_partecipazione(persona, 100 + i)
                        continue

                    Brano.objects.create(
                        concerto=concerto, compositore=item["compositore"], titolo=item["titolo"],
                        prima_esecuzione_tipo=item["prima"], ordine=prossimo_ordine,
                    )
                    prossimo_ordine += 1
                    stats["brano"][0] += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"    Brano CREATO: {item['compositore']} — {item['titolo']}"
                    ))
                    persona = get_persona(item["compositore"], "compositore", "")
                    get_partecipazione(persona, 100 + i)

                for b in esistenti:
                    if b.pk not in matched_pks:
                        self.stdout.write(self.style.ERROR(
                            f"    Brano DA RIVEDERE A MANO (non riconosciuto): pk={b.pk} "
                            f"{b.compositore!r} / {b.titolo!r}"
                        ))

            if options["dry_run"]:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(
            f"\nConcerti: {stats['concerto'][0]} creati, {stats['concerto'][1]} già esistenti"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"Persone: {stats['persona'][0]} create, {stats['persona'][1]} già esistenti"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"Brani: {stats['brano'][0]} creati, {stats['brano'][1]} corretti (erano invertiti), "
            f"{stats['brano'][2]} già ok"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"Partecipazioni: {stats['partecipazione'][0]} create, {stats['partecipazione'][1]} già esistenti"
        ))
        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("\n--dry-run: nessuna modifica salvata (rollback)."))
