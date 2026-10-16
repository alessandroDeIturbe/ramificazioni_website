from django.contrib.sitemaps import Sitemap
from django.db.models import Max
from django.urls import reverse

from .models import Concerto


class _Base(Sitemap):
    """Ogni URL in tutte le lingue di settings.LANGUAGES, con alternates hreflang.

    x_default di Django toglie il prefisso /it/ (pensato per prefix_default_language=False):
    qui darebbe un 302. L'x-default (/it/...) sta solo nell'HTML, vedi base.html.
    """

    i18n = True
    alternates = True
    protocol = "https"


class StaticSitemap(_Base):
    def items(self):
        return [
            "concerti:home", "concerti:events_list", "concerti:about", "concerti:archivio",
            "concerti:archivio_edizioni", "concerti:archivio_commissioni",
            "concerti:archivio_compositori", "concerti:archivio_interpreti",
            "concerti:archivio_gallery", "concerti:contacts", "concerti:sostenitori",
            "concerti:privacy", "concerti:impressum",
        ]

    def location(self, item):
        return reverse(item)


class ConcertoSitemap(_Base):
    def items(self):
        return Concerto.objects.pubblicati().order_by("data")

    def location(self, c):
        return reverse("concerti:event_detail", args=[c.slug])

    def lastmod(self, c):
        return c.aggiornato_il


class StagioneSitemap(_Base):
    def items(self):
        return list(
            Concerto.objects.pubblicati().values("stagione").annotate(lm=Max("aggiornato_il")).order_by("-lm")
        )

    def location(self, s):
        return reverse("concerti:stagione_detail", args=[s["stagione"]])

    def lastmod(self, s):
        return s["lm"]


SITEMAPS = {"pagine": StaticSitemap, "concerti": ConcertoSitemap, "stagioni": StagioneSitemap}
