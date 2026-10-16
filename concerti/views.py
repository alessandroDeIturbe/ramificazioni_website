from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from .forms import SponsorInquiryForm
from .models import Brano, Concerto, FotoConcerto, Persona, Sostenitore


def home(request):
    prossimo = Concerto.objects.futuri().select_related("sede").first()
    return render(request, "concerti/home.html", {"prossimo": prossimo})


def events_list(request):
    """Stagione corrente = quella dell'ultimo concerto pubblicato; le precedenti stanno in Archivio."""
    stagione = Concerto.objects.pubblicati().order_by("-data").values_list("stagione", flat=True).first()
    concerti = Concerto.objects.pubblicati().filter(stagione=stagione).select_related("sede").order_by("data")
    return render(request, "concerti/events_list.html", {"stagione": stagione, "concerti": concerti})


def event_detail(request, slug):
    concerto = get_object_or_404(
        Concerto.objects.pubblicati().select_related("sede").prefetch_related(
            "brani", "foto", "partecipazioni__persona"
        ),
        slug=slug,
    )
    return render(request, "concerti/event_detail.html", {"concerto": concerto})


def stagione_detail(request, stagione):
    concerti = Concerto.objects.pubblicati().filter(stagione=stagione).select_related("sede").order_by("data")
    if not concerti.exists():
        raise Http404
    return render(request, "concerti/stagione_detail.html", {"stagione": stagione, "concerti": concerti})


def about(request):
    direzione = Persona.objects.filter(ruolo="direzione")
    return render(request, "concerti/about.html", {"direzione": direzione})


def contributors(request):
    return redirect("concerti:archivio_interpreti", permanent=True)  # vecchio URL


def archivio(request):
    return render(request, "concerti/archivio.html")


def archivio_edizioni(request):
    concerti = Concerto.objects.pubblicati().select_related("sede").order_by("-data")
    return render(request, "concerti/archivio_edizioni.html", {"concerti": concerti})


def archivio_commissioni(request):
    brani = (
        Brano.objects.filter(commissione=True, concerto__pubblicato=True)
        .select_related("concerto")
        .order_by("-concerto__data", "ordine")
    )
    return render(request, "concerti/archivio_commissioni.html", {"brani": brani})


def archivio_compositori(request):
    persone = Persona.objects.filter(ruolo="compositore").prefetch_related("concerti")
    return render(request, "concerti/archivio_persone.html", {"titolo": _("Compositori"), "persone": persone})


def archivio_interpreti(request):
    persone = Persona.objects.filter(ruolo__in=["interprete", "regia_audio"]).prefetch_related("concerti")
    return render(request, "concerti/archivio_persone.html", {"titolo": _("Interpreti"), "persone": persone})


def archivio_gallery(request):
    concerti = (
        Concerto.objects.pubblicati().filter(foto__isnull=False).distinct().order_by("-data").prefetch_related("foto")
    )
    return render(request, "concerti/archivio_gallery.html", {"concerti": concerti})


def contacts(request):
    return render(request, "concerti/contacts.html")


def privacy(request):
    return render(request, "concerti/privacy.html")


def impressum(request):
    return render(request, "concerti/impressum.html")


def sostenitori(request):
    if request.method == "POST":
        form = SponsorInquiryForm(request.POST)
        if form.is_valid() and not form.cleaned_data["nome_azienda_hp"]:
            form.invia_email()
            messages.success(request, _("Grazie, ti risponderemo al più presto."))
            return redirect("concerti:sostenitori")
    else:
        form = SponsorInquiryForm()
    attivi = Sostenitore.objects.filter(attivo=True).order_by("ordine")
    return render(request, "concerti/sostenitori.html", {"sostenitori": attivi, "form": form})
