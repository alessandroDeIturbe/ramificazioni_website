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
