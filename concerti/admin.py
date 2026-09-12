from django.contrib import admin

from .models import (
    Brano,
    Concerto,
    FotoConcerto,
    Partecipazione,
    Persona,
    Sede,
    Sostenitore,
)


class BranoInline(admin.TabularInline):
    model = Brano
    extra = 1
    fields = ["ordine", "compositore", "titolo", "prima_esecuzione_tipo"]


class PartecipazioneInline(admin.TabularInline):
    model = Partecipazione
    extra = 1
    autocomplete_fields = ["persona"]


class FotoConcertoInline(admin.TabularInline):
    model = FotoConcerto
    extra = 1


@admin.register(Concerto)
class ConcertoAdmin(admin.ModelAdmin):
    """
    Un'unica pagina per inserire un concerto con tutti i dettagli: data/sede,
    colori dell'edizione, programma musicale, interpreti/regia audio e foto —
    questa è la "dashboard evento" richiesta, gratis grazie all'admin di Django.

    Per iniziare una nuova stagione (es. 2026/27) non serve nessuna azione
    speciale: si aggiunge un nuovo Concerto con stagione="2026/27" e
    numero_edizione=1 — la stagione precedente resta visibile e filtrabile
    (list_filter "stagione"), quelle con data passata finiscono comunque
    nell'archivio pubblico (Concerto.objects.passati()).
    """

    date_hierarchy = "data"  # navigazione per anno/mese, utile per "correggere le date"
    list_display = ["__str__", "stagione", "data", "sede", "pubblicato"]
    list_filter = ["stagione", "pubblicato"]
    ordering = ["-stagione", "-data"]
    search_fields = ["numero_edizione", "nota_programma"]
    prepopulated_fields = {"slug": ["stagione", "numero_edizione"]}
    inlines = [BranoInline, PartecipazioneInline, FotoConcertoInline]
    fieldsets = [
        (None, {"fields": ["numero_edizione", "stagione", "slug", "pubblicato"]}),
        ("Data e luogo", {"fields": ["data", "ora", "sede"]}),
        (
            "Colori edizione (gradiente-per-edizione, design system §2)",
            {"fields": [
                ("colore_sfondo_1", "colore_sfondo_2", "colore_sfondo_3"),
                "colore_accento",
            ]},
        ),
        ("Contenuti", {"fields": ["nota_programma", "link_prenotazione"]}),
    ]


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ["nome", "ruolo", "strumento"]
    list_filter = ["ruolo"]
    search_fields = ["nome"]


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ["nome", "indirizzo"]


@admin.register(Sostenitore)
class SostenitoreAdmin(admin.ModelAdmin):
    list_display = ["nome", "attivo", "ordine"]
    list_editable = ["attivo", "ordine"]
