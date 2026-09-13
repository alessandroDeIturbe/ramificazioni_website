"""Chiamate a servizi esterni. Solo stdlib (urllib) — nessuna dipendenza aggiuntiva
per un singolo endpoint REST usato da un'azione admin manuale."""
import json
import time
import urllib.error
import urllib.request

from django.conf import settings

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)

NOMI_LINGUA = {"it": "italiano", "en": "inglese", "de": "tedesco", "fr": "francese"}

MAX_TENTATIVI = 3  # su 429 (rate limit Gemini): retry con backoff 2s, 4s prima di rinunciare


def traduci_testo(testo, lingua_origine, lingua_destinazione):
    """Traduce `testo` da lingua_origine a lingua_destinazione tramite l'API Gemini."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY non impostata nell'ambiente.")

    prompt = (
        f"Traduci il seguente testo dal {NOMI_LINGUA[lingua_origine]} al "
        f"{NOMI_LINGUA[lingua_destinazione]}. Rispondi solo con il testo tradotto, "
        f"senza commenti aggiuntivi:\n\n{testo}"
    )
    payload = json.dumps(
        {"contents": [{"parts": [{"text": prompt}]}]}
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{GEMINI_URL}?key={settings.GEMINI_API_KEY}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    dati = None
    for tentativo in range(MAX_TENTATIVI):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                dati = json.load(response)
            break
        except urllib.error.HTTPError as errore:
            if errore.code == 429 and tentativo < MAX_TENTATIVI - 1:
                time.sleep(2 ** (tentativo + 1))
                continue
            raise RuntimeError(f"Chiamata a Gemini fallita: {errore}") from errore
        except urllib.error.URLError as errore:
            raise RuntimeError(f"Chiamata a Gemini fallita: {errore}") from errore

    try:
        return dati["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as errore:
        raise RuntimeError(f"Risposta Gemini inattesa: {dati}") from errore
