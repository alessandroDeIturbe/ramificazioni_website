from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.utils import translation


class AdminLocaleMiddleware:
    """
    Forza l'admin in italiano indipendentemente da Accept-Language/cookie del
    browser. /admin/ resta fuori da i18n_patterns (config/urls.py) quindi
    LocaleMiddleware sceglie la lingua dal browser — sbagliato per una
    dashboard con un solo admin italofono. Le stringhe di django.contrib.admin
    sono già tradotte in italiano da Django stesso, non serve un catalogo
    nostro: basta forzare la lingua attiva.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            translation.activate("it")
            request.LANGUAGE_CODE = "it"
        return self.get_response(request)


class PreviewStaffOnlyMiddleware:
    """
    Sull'host di anteprima (settings.PREVIEW_HOST, servito da Caddy col colore blue/green
    non live) solo lo staff vede il sito: gli altri vanno al login dell'admin.
    Va dopo AuthenticationMiddleware. Sugli altri host non fa nulla.
    """

    LIBERI = ("/admin/", "/static/")  # login admin e asset

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.get_host().split(":")[0] == settings.PREVIEW_HOST
            and not request.user.is_staff
            and not request.path.startswith(self.LIBERI)
        ):
            return redirect_to_login(request.get_full_path(), "/admin/login/")
        return self.get_response(request)
