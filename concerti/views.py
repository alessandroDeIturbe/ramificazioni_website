from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from .forms import SponsorInquiryForm
from .models import Concerto, Persona, Sostenitore


def home(request):
    prossimo = Concerto.objects.futuri().select_related("sede").first()
    return render(request, "concerti/home.html", {"prossimo": prossimo})


def events_list(request):
    futuri = Concerto.objects.futuri().select_related("sede")
    passati = Concerto.objects.passati().select_related("sede")
    return render(request, "concerti/events_list.html", {"futuri": futuri, "passati": passati})


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
    persone = Persona.objects.exclude(ruolo="direzione").prefetch_related("concerti")
    return render(request, "concerti/contributors.html", {"persone": persone})


def contacts(request):
    return render(request, "concerti/contacts.html")


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
