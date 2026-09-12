#!/bin/sh
# Ripristina sulla VPS i dati portati da migrate-to-vps.sh (dump SQL + foto).
# Eseguire UNA VOLTA, dopo 'docker compose -f docker-compose.prod.yml up -d --build'
# (schema gia' migrato dall'entrypoint) e PRIMA di un eventuale createsuperuser
# (il dump include gia' l'utente admin).
# Uso: ./scripts/restore-migration.sh [dump.sql.gz] [media.tar.gz]
set -eu
cd "$(dirname "$0")/.."

# shellcheck disable=SC1091
[ -f .env ] && . ./.env

SQL_FILE="${1:-$(ls -t backups/migrazione-*.sql.gz 2>/dev/null | head -n1)}"
MEDIA_FILE="${2:-$(ls -t backups/migrazione-media-*.tar.gz 2>/dev/null | head -n1)}"

[ -n "$SQL_FILE" ] && [ -f "$SQL_FILE" ] || { echo "Nessun dump SQL trovato in backups/"; exit 1; }
[ -n "$MEDIA_FILE" ] && [ -f "$MEDIA_FILE" ] || { echo "Nessun archivio media trovato in backups/"; exit 1; }

echo "Ripristino da: $SQL_FILE e $MEDIA_FILE"

gunzip -c "$SQL_FILE" | docker compose -f docker-compose.prod.yml exec -T db \
  psql -v ON_ERROR_STOP=1 -U "${DB_USER:-ramificazioni}" "${DB_NAME:-ramificazioni}"

# Estrazione dentro il container web gia' in esecuzione: /app/media e' li' il
# mount del volume media_volume, non serve indovinare il nome generato da Compose.
docker compose -f docker-compose.prod.yml exec -T web sh -c "cd /app/media && tar -xzf -" < "$MEDIA_FILE"

echo ""
echo "Ripristino completato."
echo "L'utente admin esistente e' stato ripristinato: NON eseguire createsuperuser."
echo "Accedi con le credenziali che usavi in locale (se dimenticate:"
echo "  docker compose -f docker-compose.prod.yml exec web python manage.py changepassword <username>)"
