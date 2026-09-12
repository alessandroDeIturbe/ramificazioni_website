from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _


class SponsorInquiryForm(forms.Form):
    """Richiesta di sponsorizzazione dalla pagina Sostenitori. Nessuna persistenza in DB:
    per un sito no-profit piccolo un'email all'admin basta, non serve un modello dedicato."""

    nome = forms.CharField(max_length=200, label=_("Nome / organizzazione"))
    email = forms.EmailField(label=_("Email"))
    messaggio = forms.CharField(widget=forms.Textarea, label=_("Messaggio"))
    # Honeypot: campo nascosto via CSS, un utente reale non lo compila mai. Unico
    # deterrente anti-spam — proporzionato per un form senza altro traffico previsto.
    nome_azienda_hp = forms.CharField(required=False, widget=forms.HiddenInput)

    def invia_email(self):
        send_mail(
            subject=f"Nuova richiesta sponsorizzazione — {self.cleaned_data['nome']}",
            message=(
                f"Da: {self.cleaned_data['nome']} <{self.cleaned_data['email']}>\n\n"
                f"{self.cleaned_data['messaggio']}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.SPONSOR_INQUIRY_EMAIL],
        )
