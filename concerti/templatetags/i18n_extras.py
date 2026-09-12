import re

from django import template

register = template.Library()

_LANG_PREFIX_RE = re.compile(r"^/[a-z]{2}(-[a-z]{2})?/")


@register.filter
def strip_lang_prefix(path):
    """
    Rimuove il prefisso di lingua da un path (/it/eventi/ -> /eventi/).

    Necessario per il form di cambio lingua in base.html: con i18n_patterns
    il prefisso nell'URL vince sempre sul cookie di lingua, quindi passare
    request.path (già prefissato) come "next" del redirect di set_language
    riporta sempre alla stessa lingua. Il path senza prefisso restituisce
    invece un 404 che LocaleMiddleware intercetta per reindirizzare al
    prefisso della lingua appena attivata — il meccanismo standard Django
    per questo esatto caso.
    """
    return _LANG_PREFIX_RE.sub("/", path) or "/"
