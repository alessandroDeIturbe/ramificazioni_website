#!/bin/bash
# Compila i dati di Privacy e Impressum (titolare, indirizzo...) nel file .env.
# Uso:   ./scripts/compila-dati-legali.sh [percorso/.env]
# I valori restano nel .env del server (non in git). Blue e green condividono lo stesso .env.
# Poi basta il deploy: ./deploy-ramificazioni.sh update
set -euo pipefail

ENV_FILE="${1:-$(dirname "$0")/../.env}"
[ -f "$ENV_FILE" ] || { echo "File non trovato: $ENV_FILE"; exit 1; }

# chiave | domanda | obbligatoria (1/0)
CAMPI=(
  "LEGAL_TITOLARE|Titolare del trattamento dati (es. Associazione Ramificazioni)|1"
  "LEGAL_RAGIONE_SOCIALE|Ragione sociale / nome legale dell'organizzatore|1"
  "LEGAL_INDIRIZZO|Indirizzo postale con via (es. Via Roma 1, 6900 Lugano)|1"
  "LEGAL_RESPONSABILE|Persona responsabile (nome e cognome)|1"
  "LEGAL_TELEFONO|Telefono (opzionale, invio per saltare)|0"
  "LEGAL_EMAIL|Email di contatto per privacy/Impressum (invio = quella attuale o info.ramificazioni@gmail.com)|0"
)

valore_attuale() { grep -E "^$1=" "$ENV_FILE" | tail -n1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//' || true; }

declare -A NUOVI
for riga in "${CAMPI[@]}"; do
  IFS='|' read -r chiave domanda obbligatorio <<< "$riga"
  attuale="$(valore_attuale "$chiave")"
  while true; do
    if [ -n "$attuale" ]; then prompt="$domanda [$attuale]: "; else prompt="$domanda: "; fi
    read -r -p "$prompt" risposta
    risposta="${risposta:-$attuale}"
    # niente " \ $ ` : il .env viene letto sia da systemd sia da bash (source) e li interpreterebbero diversamente
    if [[ "$risposta" == *[\"\\\$\`]* ]]; then echo "  Caratteri non ammessi: \" \\ \$ \`"; continue; fi
    if [ -z "$risposta" ] && [ "$obbligatorio" = 1 ]; then echo "  Campo obbligatorio."; continue; fi
    if [ "$chiave" = LEGAL_EMAIL ] && [ -n "$risposta" ] && [[ "$risposta" != *@*.* ]]; then echo "  Email non valida."; continue; fi
    break
  done
  NUOVI[$chiave]="$risposta"
done

echo; echo "Riepilogo:"
for riga in "${CAMPI[@]}"; do chiave="${riga%%|*}"; printf '  %-22s %s\n' "$chiave" "${NUOVI[$chiave]:-(vuoto)}"; done
read -r -p "Scrivo in $ENV_FILE? [s/N] " ok
[[ "$ok" =~ ^[sS]$ ]] || { echo "Annullato, nulla modificato."; exit 0; }

cp -p "$ENV_FILE" "$ENV_FILE.bak"   # stesso permessi del .env (contiene segreti)
tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT
grep -v -E '^LEGAL_[A-Z_]+=' "$ENV_FILE" > "$tmp" || true
for riga in "${CAMPI[@]}"; do chiave="${riga%%|*}"; echo "$chiave=\"${NUOVI[$chiave]}\"" >> "$tmp"; done
cat "$tmp" > "$ENV_FILE"             # cat > mantiene inode e permessi (green ha un symlink a questo file)

echo "Fatto. Backup in $ENV_FILE.bak"
echo "Prossimo passo: deploy (./deploy-ramificazioni.sh update). I valori sono letti al riavvio del servizio."
