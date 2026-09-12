from .models import Sostenitore


def sostenitori(request):
    """Loghi sostenitori attivi, disponibili in ogni template (footer globale)."""
    return {"sostenitori_footer": Sostenitore.objects.filter(attivo=True)}
