from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from .forms import SponsorInquiryForm
from .models import Concerto, Persona, Sostenitore


def home(request):
    prossimo = Concerto.objects.futuri().select_related("sede").first()
    riferimento = prossimo or Concerto.objects.pubblicati().order_by("-data").first()
    stagione_corrente = riferimento.stagione if riferimento else None
    stagione = (
        Concerto.objects.pubblicati().filter(stagione=stagione_corrente)
        .select_related("sede").order_by("data")
        if stagione_corrente else Concerto.objects.none()
    )
    return render(
        request, "concerti/home.html",
        {"prossimo": prossimo, "stagione": stagione, "stagione_corrente": stagione_corrente},
    )


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
