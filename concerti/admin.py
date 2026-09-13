import json

from django.contrib import admin
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse

from .models import (
    Brano,
    Concerto,
    FotoConcerto,
    Partecipazione,
    Persona,
    Sede,
    Sostenitore,
)
from .services import traduci_testo

LINGUA_CAMPO_BIO = {"it": "bio", "en": "bio_en", "de": "bio_de", "fr": "bio_fr"}
NOMI_LINGUA = {"it": "italiano", "en": "inglese", "de": "tedesco", "fr": "francese"}


def _lingua_sorgente(persona):
    return next(
        (
            (lingua, getattr(persona, campo))
            for lingua, campo in LINGUA_CAMPO_BIO.items()
            if getattr(persona, campo)
        ),
        None,
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
        ("Contenuti", {"fields": [
            "nota_programma", "nota_programma_en", "nota_programma_de", "nota_programma_fr",
            "link_prenotazione",
        ]}),
    ]


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ["nome", "ruolo", "strumento"]
    list_filter = ["ruolo"]
    search_fields = ["nome"]
    fieldsets = [
        (None, {"fields": ["nome", "ruolo", "strumento", "ritratto"]}),
        ("Bio", {"fields": ["bio", "bio_en", "bio_de", "bio_fr"]}),
    ]
    actions = ["traduci_bio_mancanti"]

    @admin.action(description="Traduci bio mancanti (Gemini)")
    def traduci_bio_mancanti(self, request, queryset):
        ids = ",".join(str(pk) for pk in queryset.values_list("pk", flat=True))
        return redirect(f"{reverse('admin:concerti_persona_traduci_bio')}?ids={ids}")

    def get_urls(self):
        return [
            path(
                "traduci-bio/",
                self.admin_site.admin_view(self.traduci_bio_piano_view),
                name="concerti_persona_traduci_bio",
            ),
            path(
                "traduci-bio/step/",
                self.admin_site.admin_view(self.traduci_bio_step_view),
                name="concerti_persona_traduci_bio_step",
            ),
        ] + super().get_urls()

    def traduci_bio_piano_view(self, request):
        ids = [int(pk) for pk in request.GET.get("ids", "").split(",") if pk]
        piano = []
        saltate = []
        for persona in Persona.objects.filter(pk__in=ids):
            sorgente = _lingua_sorgente(persona)
            if not sorgente:
                saltate.append(persona.nome)
                continue
            lingua_origine, _testo = sorgente
            for lingua in LINGUA_CAMPO_BIO:
                if lingua == lingua_origine or getattr(persona, LINGUA_CAMPO_BIO[lingua]):
                    continue
                piano.append({
                    "persona_id": persona.pk,
                    "persona_nome": persona.nome,
                    "lingua_origine": lingua_origine,
                    "lingua_destinazione": lingua,
                    "lingua_destinazione_nome": NOMI_LINGUA[lingua],
                })
        return render(
            request,
            "admin/concerti/persona/traduci_bio.html",
            {
                **self.admin_site.each_context(request),
                "piano_json": json.dumps(piano),
                "totale": len(piano),
                "saltate": saltate,
                "step_url": reverse("admin:concerti_persona_traduci_bio_step"),
                "changelist_url": reverse("admin:concerti_persona_changelist"),
            },
        )

    def traduci_bio_step_view(self, request):
        if request.method != "POST":
            raise Http404
        dati = json.loads(request.body)
        persona = Persona.objects.get(pk=dati["persona_id"])
        campo = LINGUA_CAMPO_BIO[dati["lingua_destinazione"]]
        sorgente = _lingua_sorgente(persona)
        if not sorgente:
            return JsonResponse({"ok": False, "errore": "Nessun testo sorgente trovato."})
        _lingua_origine, testo_origine = sorgente
        try:
            setattr(persona, campo, traduci_testo(testo_origine, dati["lingua_origine"], dati["lingua_destinazione"]))
            persona.save()
            return JsonResponse({"ok": True})
        except RuntimeError as errore:
            return JsonResponse({"ok": False, "errore": str(errore)})


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ["nome", "indirizzo"]


@admin.register(Sostenitore)
class SostenitoreAdmin(admin.ModelAdmin):
    list_display = ["nome", "attivo", "ordine"]
    list_editable = ["attivo", "ordine"]
