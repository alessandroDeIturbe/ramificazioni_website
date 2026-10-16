from django.conf import settings

from .models import Sostenitore


def sostenitori(request):
    """Loghi sostenitori attivi, disponibili in ogni template (footer globale)."""
    return {"sostenitori_footer": Sostenitore.objects.filter(attivo=True)}


def legale(request):
    """Dati legali per Privacy/Impressum + host di anteprima per il link nell'admin."""
    return {"legale": settings.LEGAL, "preview_host": settings.PREVIEW_HOST}
