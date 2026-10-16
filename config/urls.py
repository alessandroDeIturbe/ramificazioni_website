from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path

from concerti.sitemaps import SITEMAPS


def robots_txt(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /admin/\nDisallow: /i18n/\n"
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}\n",
        content_type="text/plain",
    )


# /admin/ resta fuori da i18n_patterns: la dashboard di gestione non ha
# bisogno di URL localizzati, solo il sito pubblico li usa. Idem robots/sitemap.
urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="django.contrib.sitemaps.views.sitemap"),
]

urlpatterns += i18n_patterns(
    path("", include("concerti.urls")),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
