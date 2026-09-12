"""
Settings condivisi tra dev e prod. Legge tutto da variabili d'ambiente
(.env in dev via python-dotenv, variabili reali del sistema in prod) —
nessun segreto hardcoded nel codice.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-secret-key-change-me")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "concerti",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "concerti.middleware.AdminLocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "concerti.context_processors.sostenitori",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "ramificazioni"),
        "USER": os.environ.get("DB_USER", "ramificazioni"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "ramificazioni"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# i18n reale (sostituisce lo stub "traduzione automatica" della bozza statica):
# 4 lingue con URL prefissati (/it/, /de/, /fr/, /en/), stringhe dei template
# marcate {% trans %} e traducibili con gli strumenti standard Django
# (makemessages/compilemessages — richiedono gettext installato).
LANGUAGE_CODE = "it"
LANGUAGES = [
    ("it", "Italiano"),
    ("de", "Deutsch"),
    ("fr", "Français"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
# I file .mo compilati sono committati in locale/ (non rigenerati al deploy):
# per un sito con poche stringhe statiche non serve una pipeline di build
# dedicata — se il testo cambia, si rilancia `compilemessages` a mano e si
# committa il nuovo .mo insieme al resto.
TIME_ZONE = "Europe/Zurich"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "info@ramificazioni.ch")
SPONSOR_INQUIRY_EMAIL = os.environ.get("SPONSOR_INQUIRY_EMAIL", DEFAULT_FROM_EMAIL)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
