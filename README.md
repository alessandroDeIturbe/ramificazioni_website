# Ramificazioni — sito

Django + Postgres, dashboard admin nativa come CMS, Docker Compose per dev e per il deploy sulla VPS.

## Sviluppo locale

```
cp .env.example .env   # solo se vuoi personalizzare, il dev compose ha già dei default
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Sito: http://localhost:8000/it/ — Admin: http://localhost:8000/admin/

`docker compose down` per fermare, `docker compose up -d --build` di nuovo dopo aver cambiato `requirements.txt`.

## Deploy su VPS (produzione)

1. Clona il repo sulla VPS.
2. `cp .env.example .env` e compila per davvero: `DJANGO_SECRET_KEY` (genera una stringa lunga e casuale — l'app **rifiuta di avviarsi** in produzione se lasci il default), `DB_PASSWORD`, `ALLOWED_HOSTS` con il dominio reale.
3. **TLS obbligatorio prima di esporre il sito**: `config/settings/prod.py` ha `SECURE_SSL_REDIRECT = True`, quindi Django reindirizza ogni richiesta a `https://`. Il config nginx incluso (`nginx/ramificazioni.conf`) ascolta solo sulla porta 80 — se lo usi così com'è, senza certificato, il sito diventa irraggiungibile (redirect verso un https che nessuno serve). Prima del primo avvio pubblico, aggiungi certbot/Let's Encrypt (non incluso in questo repo) o un altro terminatore TLS davanti a nginx.
4. `docker compose -f docker-compose.prod.yml up -d --build` — al primo avvio il container `web` esegue da solo `migrate` + `collectstatic` (vedi `entrypoint.sh`).
5. `docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser`

Se arrivi da un ambiente di sviluppo dove avevi già inserito dati veri via `/admin/` (concerti,
persone, foto), **salta il punto 5** e usa invece `./scripts/migrate-to-vps.sh` (dalla macchina
di sviluppo) seguito da `./scripts/restore-migration.sh` (sulla VPS, tra i punti 4 e 5): il dump
include già l'utente admin, quindi non serve ricrearlo.

### Hardening opzionale dell'admin

`/admin/` è già protetto dall'autenticazione Django. Se vuoi un livello in più su un sito pubblico, aggiungi in `nginx/ramificazioni.conf` un blocco `location /admin/ { ... }` con `auth_basic` (richiede una seconda password prima ancora di vedere il login Django) oppure un `allow`/`deny` per IP se l'admin lo usate sempre dagli stessi indirizzi. Non è incluso di default per non complicare l'accesso su un sito gestito da poche persone da luoghi diversi.

### Backup del database

Non c'è replica: il volume Postgres sulla VPS è l'unica copia di concerti/persone/foto. Usa lo script incluso:

```
./scripts/backup-db.sh
```

Salva un dump compresso in `backups/` (esclusa da git). Pianificalo con crontab sulla VPS:

```
0 3 * * * cd /percorso/ramificazioni_website && ./scripts/backup-db.sh
```

Per riportare i backup fuori dalla VPS (offsite), copiali periodicamente altrove (`scp`/`rsync`) — non incluso qui, aggiungilo se/quando serve davvero.

## Cose note e non ancora fatte

- Nessun certificato TLS/certbot configurato (vedi sopra).
- Nessun firewall configurato in questo repo — su una VPS nuova apri solo le porte 80/443 (e SSH) a livello di provider o `ufw`/`iptables`.
- Nessuna rotazione/offsite dei backup, solo il dump giornaliero locale.
