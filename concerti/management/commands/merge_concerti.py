"""
Unisce nel DB corrente le righe presenti in un dump `manage.py dumpdata concerti`
prodotto da un altro ambiente (locale <-> VPS), senza mai sovrascrivere dati
esistenti: le righe mancanti vengono create, le righe con la stessa chiave
naturale ma campi diversi finiscono in un report di conflitti da risolvere a mano.

Uso:
    manage.py merge_concerti --theirs /percorso/al/dump_altro_ambiente.json

Va eseguito una volta per lato (una volta sulla VPS con il dump del locale, una
volta in locale con il dump della VPS) per ottenere l'unione su entrambi.
"""
import json
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from concerti.models import (
    Brano,
    Concerto,
    FotoConcerto,
    Partecipazione,
    Persona,
    Sede,
    Sostenitore,
)

# Un modello va processato dopo tutti quelli che referenzia via FK, cosi' la
# mappa "pk-loro -> nostra istanza" e' gia' pronta quando serve.
MODEL_ORDER = ["sede", "persona", "concerto", "brano", "partecipazione", "fotoconcerto", "sostenitore"]

MODEL_CLASSES = {
    "sede": Sede,
    "persona": Persona,
    "concerto": Concerto,
    "brano": Brano,
    "partecipazione": Partecipazione,
    "fotoconcerto": FotoConcerto,
    "sostenitore": Sostenitore,
}

# Quali campi sono FK e verso quale modello (per tradurre il pk nel dump
# altrui nell'istanza corrispondente nel nostro DB).
FK_FIELDS = {
    "concerto": {"sede": "sede"},
    "brano": {"concerto": "concerto"},
    "partecipazione": {"concerto": "concerto", "persona": "persona"},
    "fotoconcerto": {"concerto": "concerto"},
}

# Campi auto-generati, esclusi dal confronto conflitti e dalla creazione.
IGNORE_FIELDS = {"creato_il", "aggiornato_il"}


def natural_key_sede(fields):
    return (fields["nome"],)


def natural_key_persona(fields):
    return (fields["nome"], fields["ruolo"])


def natural_key_concerto(fields):
    return (fields["slug"],)


def natural_key_brano(fields):
    concerto = fields["concerto"]
    return (concerto.pk if concerto else None, fields["compositore"], fields["titolo"])


def natural_key_partecipazione(fields):
    concerto = fields["concerto"]
    persona = fields["persona"]
    return (concerto.pk if concerto else None, persona.pk if persona else None)


def natural_key_fotoconcerto(fields):
    concerto = fields["concerto"]
    return (concerto.pk if concerto else None, fields["immagine"])


def natural_key_sostenitore(fields):
    return (fields["nome"],)


NATURAL_KEY_FUNCS = {
    "sede": natural_key_sede,
    "persona": natural_key_persona,
    "concerto": natural_key_concerto,
    "brano": natural_key_brano,
    "partecipazione": natural_key_partecipazione,
    "fotoconcerto": natural_key_fotoconcerto,
    "sostenitore": natural_key_sostenitore,
}


def fields_from_instance(model_name, Model, obj):
    """Stessa forma dei fields di dumpdata, ma con le FK come istanza (non pk)."""
    result = {}
    for f in Model._meta.fields:
        if f.name == Model._meta.pk.name:
            continue
        result[f.name] = getattr(obj, f.name)
    return result


def resolve_fields(model_name, fields, maps):
    """Sostituisce i pk delle FK (validi nel dump altrui) con la nostra istanza."""
    resolved = dict(fields)
    for field_name, target_model in FK_FIELDS.get(model_name, {}).items():
        their_pk = fields.get(field_name)
        if their_pk is None:
            resolved[field_name] = None
            continue
        our_obj = maps[target_model].get(their_pk)
        if our_obj is None:
            return None  # dipendenza non risolta: la riga referenziata e' stata saltata
        resolved[field_name] = our_obj
    return resolved


def build_comparable(model_name, fields):
    """Normalizza i valori per il confronto (FK -> pk, date -> stringa ISO)."""
    out = {}
    for name, value in fields.items():
        if name in IGNORE_FIELDS:
            continue
        if name in FK_FIELDS.get(model_name, {}):
            out[name] = value.pk if value is not None else None
        elif hasattr(value, "isoformat"):
            out[name] = value.isoformat()
        else:
            out[name] = value
    return out


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "--theirs", required=True,
            help="File JSON prodotto da 'manage.py dumpdata concerti' sull'altro ambiente",
        )

    def handle(self, *args, **options):
        with open(options["theirs"]) as f:
            dump = json.load(f)

        by_model = defaultdict(list)
        for entry in dump:
            by_model[entry["model"].split(".")[-1]].append(entry)

        maps = {name: {} for name in MODEL_ORDER}  # their_pk -> nostra istanza
        created_count = 0
        conflicts = []

        with transaction.atomic():
            for model_name in MODEL_ORDER:
                Model = MODEL_CLASSES[model_name]
                nk_func = NATURAL_KEY_FUNCS[model_name]

                existing_index = {}
                for obj in Model.objects.all():
                    key = nk_func(fields_from_instance(model_name, Model, obj))
                    existing_index[key] = obj

                for entry in by_model.get(model_name, []):
                    resolved = resolve_fields(model_name, entry["fields"], maps)
                    if resolved is None:
                        self.stdout.write(self.style.WARNING(
                            f"  [{model_name}] pk={entry['pk']} saltato: dipendenza non trovata"
                        ))
                        continue

                    key = nk_func(resolved)
                    existing_obj = existing_index.get(key)

                    if existing_obj is not None:
                        maps[model_name][entry["pk"]] = existing_obj
                        ours_cmp = build_comparable(
                            model_name, fields_from_instance(model_name, Model, existing_obj)
                        )
                        theirs_cmp = build_comparable(model_name, resolved)
                        diff = {
                            name: (ours_cmp[name], theirs_cmp.get(name))
                            for name in ours_cmp
                            if ours_cmp[name] != theirs_cmp.get(name)
                        }
                        if diff:
                            conflicts.append((model_name, key, diff))
                        continue

                    create_kwargs = {k: v for k, v in resolved.items() if k not in IGNORE_FIELDS}
                    new_obj = Model.objects.create(**create_kwargs)
                    maps[model_name][entry["pk"]] = new_obj
                    existing_index[key] = new_obj
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f"\nCreate {created_count} righe nuove."))
        if conflicts:
            self.stdout.write(self.style.WARNING(f"{len(conflicts)} conflitti da risolvere a mano:\n"))
            for model_name, key, diff in conflicts:
                self.stdout.write(f"  [{model_name}] chiave={key}")
                for field_name, (ours, theirs) in diff.items():
                    self.stdout.write(f"      {field_name}: nostro={ours!r}  loro={theirs!r}")
        else:
            self.stdout.write(self.style.SUCCESS("Nessun conflitto."))
