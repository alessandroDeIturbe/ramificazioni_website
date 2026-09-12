from django.shortcuts import get_object_or_404, render

from .models import Concerto, Persona


def home(request):
    prossimo = Concerto.objects.futuri().select_related("sede").first()
    stagione = Concerto.objects.pubblicati().select_related("sede").order_by("data")
    return render(request, "concerti/home.html", {"prossimo": prossimo, "stagione": stagione})


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
