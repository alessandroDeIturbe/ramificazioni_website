from django.conf import settings
from django.db.models import Max

from .models import Concerto, Sostenitore


def sostenitori(request):
    """Loghi sostenitori attivi, disponibili in ogni template (footer globale)."""
    return {"sostenitori_footer": Sostenitore.objects.filter(attivo=True)}


def stagioni_nav(request):
    """Stagioni esistenti, più recente in cima — per il menu a tendina nell'header."""
    stagioni = (
        Concerto.objects.pubblicati()
        .values("stagione")
        .annotate(ultima_data=Max("data"))
        .order_by("-ultima_data")
    )
    return {"stagioni_nav": stagioni}


def legale(request):
    """Dati legali per Privacy/Impressum + host di anteprima per il link nell'admin."""
    return {"legale": settings.LEGAL, "preview_host": settings.PREVIEW_HOST}
