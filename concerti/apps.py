from django.apps import AppConfig


class ConcertiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "concerti"
    verbose_name = "Concerti e stagione"

    def ready(self):
        # Personalizzazione branding dell'admin — va fatta a app-registry pronto,
        # non in settings.py (lì admin.site non è ancora inizializzato).
        from django.contrib import admin

        admin.site.site_header = "Ramificazioni — Amministrazione"
        admin.site.site_title = "Ramificazioni Admin"
        admin.site.index_title = "Gestione stagione e contenuti"
