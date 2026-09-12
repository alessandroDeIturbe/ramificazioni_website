#!/bin/sh
# Trasferisce i dati inseriti in locale (dashboard admin, stack dev) su una VPS
# via scp, prima che lo stack di produzione venga creato da zero lì.
# Uso: ./scripts/migrate-to-vps.sh   (chiede utente/host/percorso interattivamente)
set -eu
cd "$(dirname "$0")/.."

read -p "Utente SSH sulla VPS: " SSH_USER
read -p "Indirizzo o hostname della VPS: " SSH_HOST
read -p "Percorso assoluto del repo sulla VPS (destinazione): " DEST_PATH

mkdir -p backups
TS=$(date +%Y%m%d-%H%M%S)
SQL_FILE="backups/migrazione-${TS}.sql.gz"
MEDIA_FILE="backups/migrazione-media-${TS}.tar.gz"

echo "Esporto i dati dal database locale (stack dev)..."
# Solo dati, non schema: lo schema lo crea gia' `entrypoint.sh` (migrate) al primo
# avvio dello stack prod sulla VPS. Le tabelle escluse sono bookkeeping Django
# rigenerato automaticamente dal migrate del target, o dati privi di senso fuori
# dall'ambiente dev (sessioni, log). auth_user NON e' escluso: l'utente admin
# gia' creato in locale viaggia con i dati, non serve rifare createsuperuser.
docker compose -f docker-compose.yml exec -T db \
  pg_dump -U ramificazioni --data-only --no-owner --no-acl \
    --exclude-table=django_migrations \
    --exclude-table=django_session \
    --exclude-table=django_content_type \
    --exclude-table=django_admin_log \
    --exclude-table=auth_permission \
    --exclude-table=auth_group \
    --exclude-table=auth_group_permissions \
    --exclude-table=auth_user_groups \
    --exclude-table=auth_user_user_permissions \
    ramificazioni | gzip > "$SQL_FILE"

echo "Comprimo la cartella media/..."
tar -czf "$MEDIA_FILE" -C media .

echo "Copio i file sulla VPS..."
ssh "$SSH_USER@$SSH_HOST" "mkdir -p '$DEST_PATH/backups'"
scp "$SQL_FILE" "$MEDIA_FILE" "$SSH_USER@$SSH_HOST:$DEST_PATH/backups/"

echo ""
echo "Fatto. File caricati su $SSH_HOST:$DEST_PATH/backups/"
echo "Sulla VPS, DOPO 'docker compose -f docker-compose.prod.yml up -d --build'"
echo "e PRIMA di un eventuale 'createsuperuser', esegui:"
echo "  cd $DEST_PATH && ./scripts/restore-migration.sh"
echo "Il dump include gia' il tuo utente admin: se il restore va a buon fine,"
echo "NON eseguire createsuperuser — accedi con le credenziali che usavi in locale."
