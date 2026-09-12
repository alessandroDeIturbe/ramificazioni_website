from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


class Sede(models.Model):
    """Luogo dei concerti — un unico posto può ospitare più edizioni."""

    nome = models.CharField(max_length=200)
    indirizzo = models.CharField(max_length=300, blank=True)
    mappa_url = models.URLField(
        "link mappa (Google Maps ecc.)", blank=True
    )

    class Meta:
        verbose_name = "sede"
        verbose_name_plural = "sedi"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class ConcertoQuerySet(models.QuerySet):
    def pubblicati(self):
        return self.filter(pubblicato=True)

    def futuri(self):
        return self.pubblicati().filter(data__gte=timezone.localdate()).order_by("data")

    def passati(self):
        return self.pubblicati().filter(data__lt=timezone.localdate()).order_by("-data")


class Concerto(models.Model):
    """
    Un concerto/edizione della stagione. I tre colori + l'accento seguono la
    logica gradiente-per-edizione del design system (§2): ogni nuovo concerto
    può ricevere una propria tinta pastello senza toccare il codice.
    """

    numero_edizione = models.PositiveIntegerField(
        "numero edizione", help_text="1, 2, 3... progressivo nella stagione"
    )
    stagione = models.CharField(max_length=20, default="2025/26")
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    data = models.DateField()
    ora = models.TimeField(null=True, blank=True)
    sede = models.ForeignKey(
        Sede, on_delete=models.PROTECT, related_name="concerti", null=True, blank=True
    )

    colore_sfondo_1 = models.CharField(max_length=7, default="#f6dfa0")
    colore_sfondo_2 = models.CharField(max_length=7, default="#f0c96a")
    colore_sfondo_3 = models.CharField(max_length=7, default="#eecf8f")
    colore_accento = models.CharField(max_length=7, default="#ffffff")

    nota_programma = models.TextField(
        "nota di programma", blank=True,
        help_text="Testo introduttivo sul concerto/compositore.",
    )
    link_prenotazione = models.URLField("link prenotazione/biglietteria", blank=True)
    pubblicato = models.BooleanField(
        default=False, help_text="Se disattivo, il concerto non è visibile sul sito pubblico."
    )

    persone = models.ManyToManyField(
        "Persona", through="Partecipazione", related_name="concerti"
    )

    creato_il = models.DateTimeField(auto_now_add=True)
    aggiornato_il = models.DateTimeField(auto_now=True)

    objects = ConcertoQuerySet.as_manager()

    class Meta:
        verbose_name = "concerto"
        verbose_name_plural = "concerti"
        ordering = ["data"]
        constraints = [
            models.UniqueConstraint(
                fields=["stagione", "numero_edizione"], name="unica_edizione_per_stagione"
            )
        ]

    def __str__(self):
        return f"Edizione {self.numero_edizione} — {self.data:%d/%m/%Y}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.stagione}-edizione-{self.numero_edizione}")
        super().save(*args, **kwargs)

    @property
    def gradiente_css(self):
        return (
            f"linear-gradient(160deg, {self.colore_sfondo_1} 0%, "
            f"{self.colore_sfondo_2} 45%, {self.colore_sfondo_3} 100%)"
        )

    @property
    def is_passato(self):
        return self.data < timezone.localdate()

    @property
    def regia_audio(self):
        return self.partecipazioni.filter(persona__ruolo="regia_audio")

    @property
    def interpreti(self):
        return self.partecipazioni.filter(persona__ruolo="interprete")

    @property
    def compositori(self):
        return self.partecipazioni.filter(persona__ruolo="compositore")


class Brano(models.Model):
    """Titolo eseguito all'interno di un concerto — parte del programma musicale."""

    PRIMA_ESECUZIONE_CHOICES = [
        ("", "Nessuna"),
        ("assoluta", "Prima esecuzione assoluta"),
        ("svizzera", "Prima esecuzione svizzera"),
        ("nazionale", "Prima esecuzione nazionale"),
    ]

    concerto = models.ForeignKey(Concerto, on_delete=models.CASCADE, related_name="brani")
    compositore = models.CharField(max_length=200)
    titolo = models.CharField(max_length=300)
    prima_esecuzione_tipo = models.CharField(
        "prima esecuzione", max_length=20, choices=PRIMA_ESECUZIONE_CHOICES, blank=True, default=""
    )
    ordine = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "brano in programma"
        verbose_name_plural = "brani in programma"
        ordering = ["ordine", "id"]

    def __str__(self):
        return f"{self.compositore} — {self.titolo}"


class Persona(models.Model):
    """Interprete, regia audio, compositore o direzione artistica — anagrafica unica."""

    RUOLO_CHOICES = [
        ("interprete", "Interprete"),
        ("regia_audio", "Regia Audio"),
        ("compositore", "Compositore"),
        ("direzione", "Direzione artistica"),
    ]

    nome = models.CharField(max_length=200)
    ruolo = models.CharField(max_length=20, choices=RUOLO_CHOICES)
    strumento = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    ritratto = models.ImageField(upload_to="ritratti/", blank=True, null=True)

    class Meta:
        verbose_name = "persona"
        verbose_name_plural = "persone"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.get_ruolo_display()})"


class Partecipazione(models.Model):
    """Collega una Persona a un Concerto, con l'eventuale strumento specifico per quella data."""

    concerto = models.ForeignKey(Concerto, on_delete=models.CASCADE, related_name="partecipazioni")
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="partecipazioni")
    strumento_in_concerto = models.CharField(
        "strumento/ruolo per questo concerto", max_length=120, blank=True,
        help_text="Se vuoto, usa lo strumento di default della persona.",
    )
    ordine = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "partecipazione"
        verbose_name_plural = "partecipazioni"
        ordering = ["ordine", "id"]
        constraints = [
            models.UniqueConstraint(fields=["concerto", "persona"], name="persona_unica_per_concerto")
        ]

    def __str__(self):
        return f"{self.persona.nome} @ {self.concerto}"

    @property
    def strumento(self):
        return self.strumento_in_concerto or self.persona.strumento


class FotoConcerto(models.Model):
    """Galleria fotografica documentaria post-concerto (design system §7)."""

    concerto = models.ForeignKey(Concerto, on_delete=models.CASCADE, related_name="foto")
    immagine = models.ImageField(upload_to="foto_concerti/%Y/%m/")
    didascalia = models.CharField(max_length=200, blank=True)
    ordine = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "foto concerto"
        verbose_name_plural = "foto concerti"
        ordering = ["ordine", "id"]

    def __str__(self):
        return f"Foto — {self.concerto}"


class Sostenitore(models.Model):
    """Logo sostenitore/partner mostrato in footer su tutto il sito."""

    nome = models.CharField(max_length=200)
    logo = models.ImageField(upload_to="sostenitori/")
    url = models.URLField(blank=True)
    attivo = models.BooleanField(default=True)
    ordine = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "sostenitore"
        verbose_name_plural = "sostenitori"
        ordering = ["ordine", "nome"]

    def __str__(self):
        return self.nome
