#!/bin/sh
# Backup Postgres su VPS (unica copia dei dati altrimenti). Uso:
#   ./scripts/backup-db.sh
# Pianificalo con crontab sulla VPS, es. ogni notte alle 3:
#   0 3 * * * cd /path/to/ramificazioni_website && ./scripts/backup-db.sh
set -eu
cd "$(dirname "$0")/.."

# DB_USER/DB_NAME servono qui sull'host per comporre il comando pg_dump
# dentro il container — non sono ereditati automaticamente da .env.
[ -f .env ] && . ./.env

mkdir -p backups
FILE="backups/ramificazioni-$(date +%F).sql.gz"

docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U "${DB_USER:-ramificazioni}" "${DB_NAME:-ramificazioni}" | gzip > "$FILE"

echo "Backup salvato in $FILE"
