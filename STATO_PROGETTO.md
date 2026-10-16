# Ramificazioni — stato del progetto

File di controllo, riassume cosa è stato fatto finora. Non sostituisce `requisiti_sito.md`
(la checklist funzionale dettagliata) né `README.md` (istruzioni di setup/deploy) — questo è
un riepilogo per orientarsi rapidamente.

## Stack

Django 5.1 + PostgreSQL, Docker Compose (dev con hot-reload, prod con gunicorn+nginx+volumi
nominati). Dashboard di gestione = `/admin/` di Django, nessuna UI custom. App unica:
`concerti`. Repo su GitHub, lavoro su branch **`development`** (mai `main`, mai pushata).

## Percorso: dalla bozza statica al sito attuale

1. **Bozza HTML/CSS statica** (prima iterazione, poi eliminata): pagine fisse con dati
   segnaposto, pensata come "prima bozza" del design system.
2. **Rifatto da zero in Django** su richiesta esplicita ("così è tutto hardcodato, voglio
   una struttura più simile a un sito moderno"): modelli DB, admin come dashboard, upload
   foto reali, Docker per il deploy su VPS. Council di 3 voci (Skeptic/Pragmatist/Critic) ha
   deciso di dividere il lavoro futuro in 2 sotto-agenti persistenti (`dev` per
   programmazione/design/i18n, `ops` per sistema/Docker/sicurezza) invece di 5 separati.

## Modello dati (`concerti/models.py`)

- **Sede** — luogo dei concerti (riusabile tra edizioni).
- **Concerto** — un'edizione di stagione: data/ora/sede, 4 colori per il gradiente
  dell'edizione, nota di programma (+ traduzioni `_en/_de/_fr`), link prenotazione,
  flag pubblicato. `date_hierarchy` in admin per navigare/correggere le date.
- **Brano** — titolo in programma, con indicazione di prima esecuzione
  (assoluta/svizzera/nazionale) **per singolo brano**, non per l'intero concerto.
- **Persona** — interprete/regia audio/compositore/direzione artistica, con bio
  (+ traduzioni `_en/_de/_fr`) e ritratto.
- **Partecipazione** — collega Persona↔Concerto con strumento specifico per quella data.
- **FotoConcerto** — galleria post-concerto.
- **Sostenitore** — logo sponsor, mostrato nel footer di tutto il sito e in una pagina
  dedicata.

## Bug reali trovati e risolti in sessione

| Bug | Causa | Fix |
|---|---|---|
| Admin non in italiano | `/admin/` fuori da `i18n_patterns`, lingua presa dal browser | `AdminLocaleMiddleware` forza `it` su `/admin/*` |
| Switch lingua "non faceva niente" | `locale/` non esisteva: DE/FR/EN senza catalogo, fallback silenzioso a IT | Catalog generati e tradotti a mano, `.mo` committati |
| `InvalidStorageError` su ogni upload immagine | `STORAGES` definito a mano senza la chiave `"default"` | Aggiunta `"default": FileSystemStorage` |
| Switch lingua bloccato su `/it/...` anche dopo il click | `next` del redirect riusava `request.path` già prefissato — il prefisso URL vince sempre sul cookie con `i18n_patterns` | Filtro `strip_lang_prefix` toglie il prefisso prima del redirect |
| `PermissionError` su upload media in dev | bind-mount `.:/app` sovrascrive il `chown` fatto nel Dockerfile; `appuser` non-root non può scrivere in `media/` (proprietà dell'utente host) | `user: root` sul servizio `web`, solo in dev (prod resta non-root, non ha questo problema: nessun bind-mount) |
| `ProgrammingError: column ... does not exist` | Migrazione nuova non ancora applicata nel container in esecuzione | `./manage.sh update` (rebuild + `migrate` automatico in avvio) |
| `backups/.gitignore` conteneva solo `*` | Il pattern ignorava anche se stesso: su un clone pulito la cartella non si sarebbe nemmeno creata | Aggiunta `!.gitignore` |
| Foto collaboratori/sostenitori sbiadite | `.person-card .portrait` (pensata per il placeholder testuale "foto") aveva `opacity:0.5` applicata anche a `<img class="portrait">` reale | Aggiunta `.person-card img.portrait { opacity: 1; }` |
| Header "Stagioni" leggermente disallineato con gli altri voci nav | Il `<div class="nav-dropdown">` ereditava `font-size` da `body` invece di `var(--small-size)`: lo "strut" del blocco usava il font più grande per l'altezza riga, gonfiando il box (20.4px vs 16.8px degli `<a>`) — diagnosticato misurando con Chrome DevTools (`getBoundingClientRect`), non a occhio | Spostato `font-size: var(--small-size)` da `.nav-dropdown > span` a `.nav-dropdown` |
| Dropdown "Stagioni" si chiudeva prima di riuscire a cliccarci | `margin-top: 0.4rem` tra trigger e menu creava una "dead zone" senza hover attivo | Rimossa la `margin-top`, menu flush sotto il trigger |
| `GEMINI_API_KEY` in `.env` non raggiungeva il container dev | `docker-compose.yml` (dev) passava le env var a mano nel blocco `environment:`, senza `env_file: .env` (a differenza di `docker-compose.prod.yml` che già lo fa) | Aggiunto `env_file: .env` al servizio `web` in dev |
| Traduzione Gemini di una persona riuscita solo per 1 lingua su 3 mancanti | Chiamate consecutive senza retry contro il rate limit Gemini (`429 RESOURCE_EXHAUSTED`) | Retry con backoff (2s/4s) su 429 in `concerti/services.py` |

## Funzionalità aggiunte oltre ai bug fix

- **i18n reale**: 4 lingue (IT/DE/FR/EN), URL prefissati (`/it/…`), switcher funzionante,
  catalog `locale/*/LC_MESSAGES/django.po`/`.mo` committati.
- **Contenuti DB traducibili**: `nota_programma` e `bio` hanno varianti `_en/_de/_fr` con
  fallback automatico all'italiano se non ancora compilate (niente pacchetto esterno tipo
  `django-modeltranslation` — solo 2 campi, non si ripagava).
- **Pagina Sostenitori** (voce di menu prima di Collaboratori): loghi sponsor attivi + form
  "diventa sponsor" (nome/email/messaggio) che invia una mail all'admin, con honeypot
  anti-spam. Richiede credenziali SMTP reali in produzione (`EMAIL_HOST`/`EMAIL_HOST_USER`/
  `EMAIL_HOST_PASSWORD` in `.env` sulla VPS — non fornibili da qui).
- **Header interamente in italiano**: Home / Chi siamo / Eventi / Stagioni (dropdown) /
  Contatti / Sostenitori / Collaboratori.
- **Testo bio giustificato** nelle schede About/Collaboratori.
- **Menu "Stagioni"**: la sezione "stagione corrente" è stata tolta dalla home; al suo posto
  un dropdown hover in header elenca tutte le stagioni pubblicate (più recente in cima,
  `concerti/context_processors.py::stagioni_nav`), ognuna linka a `/stagioni/<stagione>/`
  (`concerti/views.py::stagione_detail`) con i concerti di quella stagione.
- **Traduzione bio assistita da Gemini**: azione admin "Traduci bio mancanti (Gemini)" su
  `PersonaAdmin` — l'utente incolla la bio ricevuta nel campo lingua corretto, poi seleziona
  la persona e lancia l'azione: apre una pagina con barra di progresso reale (`<progress>` +
  testo di stato, `templates/admin/concerti/persona/traduci_bio.html`) che chiama Gemini una
  lingua alla volta (`concerti/services.py::traduci_testo`, con retry/backoff su 429) e
  riempie solo i campi `_en/_de/_fr` ancora vuoti, senza mai sovrascrivere testo esistente.
  Richiede `GEMINI_API_KEY` in `.env` (letta anche in dev, ora che `docker-compose.yml` carica
  `env_file: .env`).
- **Email di contatto** aggiornata a `info.ramificazioni@gmail.com` ovunque (footer, pagina
  Contatti, default in `config/settings/base.py`, `.env.example`).

## Git e deploy

- Repo inizializzato, primo commit, branch `development` creata e pushata su
  `github.com/alessandroDeIturbe/ramificazioni_website` (mai su `main`).
- `.gitignore` irrobustito: `.env*` (tranne `.env.example`), `*.sqlite3`, `*.pem`/`*.key`,
  `/media/`, `/staticfiles/`.
- `scripts/backup-db.sh` — backup periodico Postgres su VPS (dump compresso).
- `scripts/migrate-to-vps.sh` + `scripts/restore-migration.sh` — trasferiscono via `scp` i
  dati inseriti in locale (concerti, persone, foto, utente admin) verso una VPS appena
  clonata, così non si perdono le entry già create durante lo sviluppo.
- `manage.sh` — start/stop/restart/update/logs/status/shell/createsuperuser per lo stack
  dev in locale (rileva da solo se serve `sudo` per Docker).

## Cosa NON è ancora fatto (vedi `requisiti_sito.md` per la checklist completa)

- TLS/certbot non configurato: `SECURE_SSL_REDIRECT=True` in prod renderebbe il sito
  irraggiungibile finché non si aggiunge un certificato reale davanti a nginx.
- Firewall VPS non configurato (va limitato a 80/443/SSH lato provider o `ufw`).
- Credenziali SMTP reali per il form sponsor (oggi vuote in `.env.example`).
- Backup solo locale sulla VPS, nessuna copia offsite.
- Nessuna foto/contenuto reale ancora caricato (il DB locale ha solo le entry di test
  inserite durante lo sviluppo).

## File chiave

- `concerti/models.py`, `concerti/admin.py` — dati e dashboard (incluse le viste custom per
  la traduzione Gemini con barra di progresso).
- `concerti/services.py` — chiamata REST a Gemini (stdlib `urllib`, retry/backoff su 429).
- `concerti/context_processors.py` — `sostenitori` (footer) e `stagioni_nav` (dropdown header).
- `templates/base.html` — layout globale, nav (incluso dropdown "Stagioni"), switcher lingua.
- `templates/concerti/stagione_detail.html`, `templates/admin/concerti/persona/traduci_bio.html`.
- `config/settings/{base,dev,prod}.py` — configurazione (incl. `GEMINI_API_KEY`).
- `docker-compose.yml` (dev, ora con `env_file: .env` sul servizio `web`) /
  `docker-compose.prod.yml` (VPS).
- `requisiti_sito.md` — checklist funzionale dettagliata, aggiornata ad ogni modifica.
- `README.md` — istruzioni setup locale e deploy VPS.

## Sync dati locale ↔ VPS (2026-09-13)

Merge dei dump DB locale/VPS applicato lato VPS (14 righe nuove: 7 persone, 5 brani, 1
partecipazione, 1 foto — nessun dato cancellato/sovrascritto). Lato locale, da questa
sessione:
- **Media copiati sulla VPS** (rsync non installato lì → usato `scp` con controllo
  esistenza manuale, stesso effetto di `--ignore-existing`): `media/ritratti/DSC02294.jpg`,
  `DSC02551.jpg`, `DSC02491.jpg`, `media/foto_concerti/2026/09/DSC02570_2.jpg`.
- **Merge inverso completato**: confrontato il dump VPS post-merge
  (`dump_vps_20260913-131846.json`, non committato) con lo stato locale per nome/slug
  (mai per PK grezza — i due DB hanno ID indipendenti). Unica differenza reale: il concerto
  "202526-edizione-2" esisteva solo sulla VPS → importato in locale con
  `scripts/import_concerto_mancante_202526_2.py` (idempotente, riusabile come riferimento
  per import futuri simili). Tutte le persone e sedi coincidevano già per nome.
- **Trovato un bug nel merge automatico lato VPS**: "Davide Bardi" è stato duplicato
  (righe pk 3 e 6 nel dump VPS) — non era tra i 5 conflitti segnalati, va ripulito
  manualmente sulla VPS (deduplicare la persona, verificare a quale delle due sono
  agganciate le partecipazioni corrette).

**Restano aperti, da decidere sulla VPS** (non toccati da questa sessione, che ha accesso
solo in lettura via SSH senza permessi docker sulla VPS):
- 5 conflitti persona/concerto singolarmente modificati su entrambi i lati: "Engin Mevsin"
  (bio FR/foto), "Ella Biscari" (bio EN/DE/FR/foto solo in locale — versione locale sembra
  più completa), "Edoardo Casali" (bio diversa — versione VPS sembra corretta), "Manuel
  Teles" (bio+strumento diversi), Concerto "202526-1" (nota programma — sulla VPS c'è un
  placeholder "ciao ciao ciao" da **non riportare** in un eventuale merge successivo).
- Duplicato "Davide Bardi" da rimuovere sulla VPS.

## Import "PROGRAMMI SALA" — eseguito (2026-09-13)

Estratti a mano i 4 PDF "programma di sala" da
`PROGRAMMI SALA-20260913T144404Z-1-001.zip` (4 dic 2025, 5 feb 2026, 12 mar 2026,
7 mag 2026): compositori, titoli dei brani, interpreti, marcatori di prima esecuzione.
Scritto ed eseguito `concerti/management/commands/import_programmi_sala.py`
(idempotente, `--dry-run` disponibile, riusabile come riferimento per import futuri
simili): per i concerti 2025/26 ed.1/2 già in DB collega i compositori senza duplicare
righe, crea da zero le edizioni 3 e 4 (`pubblicato=False`, `ora=None` — nessun orario
indicato nei rispettivi PDF). Dedupe per chiave naturale `(nome, ruolo)` su Persona e
`(stagione, numero_edizione)` su Concerto, stesso pattern di `merge_concerti.py`.

Risultato verificato via `manage.py shell` dopo il run: edizione 1 = 6 brani/6
compositori/3 interpreti, edizione 2 = 4/4/2, edizione 3 (nuova) = 7/7/2, edizione 4
(nuova) = 6/6/4+1 regia audio. "Giulio Cattaneo" (compositore sia in ed.1 che in ed.4)
risulta correttamente una sola riga `Persona`, condivisa tra i due concerti — nessun
duplicato creato. Durante il dry-run è emerso che il titolo "Il canto degli esseri
altri" già in DB (con "Il") differiva da quello letto sulla copertina del PDF (senza
"Il") — usata la grafia già in DB per evitare di creare una seconda riga quasi-duplicata
per lo stesso brano.

**Non toccato, pre-esistente**: 5 righe `Brano` dell'edizione 1 (pk 11-15) con
compositore/titolo invertiti, residuo del bug di merge automatico descritto sopra
("Trovato un bug nel merge automatico lato VPS"). Il comando le rileva e le segnala come
"DA RIVEDERE A MANO" ma non le tocca (nessuna correzione automatica silenziosa). Vanno
ripulite a mano in `/admin/concerti/concerto/1/change/` (inline Brano) quando qualcuno
ha tempo — non urgente, non visibili pubblicamente in modo scorretto perché duplicate,
solo ridondanti nel DB.

**Nota operativa per sessioni future**: questa sessione gira **sulla VPS di produzione
stessa** (gunicorn live su `ramificazioni.sabaconsulting.ch`, non un ambiente dev Docker
separato — niente Docker installato qui). `manage.py` non carica mai `.env` da solo
(nessun `python-dotenv` nel codice: in dev è Docker a farlo via `env_file:`, in prod è
systemd via `EnvironmentFile=` nei due `.service` — `ramificazioni` e
`ramificazioni-green`, ognuno con il proprio `.env` in root del rispettivo checkout, da
tenere allineati). Per lanciare un comando manuale da shell (shell di sistema = `fish`,
non bash):
```fish
env (grep -v '^#' .env | grep .) .venv/bin/python manage.py <comando>
```
L'accesso diretto a Postgres via `psql`/lettura di file di credenziali/generazione
password è bloccato dai classificatori di sicurezza automatici di Claude Code
("Production Reads", "Credential Materialization", "Secret-Store Writes") — vanno
eseguiti dall'utente da terminale, non delegabili all'agente.

**Incidente e fix, stesso giorno**: dopo il reset password sopra, il sito pubblico ha
dato "Server Error (500)" per ~40 minuti. Causa: `ramificazioni-green.service`
(quello che riceve il traffico live — vedi `reverse_proxy 127.0.0.1:8805` nel blocco
`ramificazioni.sabaconsulting.ch` di `/etc/caddy/Caddyfile`) era già in esecuzione da
prima del reset, con la vecchia password caricata nell'ambiente di processo via
`EnvironmentFile=.env` di systemd — **letto solo all'avvio, mai ricaricato a caldo**.
Ogni riconnessione al DB falliva con `password authentication failed`. Fix:
`sudo systemctl restart ramificazioni-green.service` (e per coerenza anche
`ramificazioni.service`, il blue su 8804, non live in quel momento ma con lo stesso
problema latente). **Lezione per il futuro**: cambiare la password del DB in
produzione richiede sempre un riavvio di entrambi i servizi (blue+green) subito dopo
aver aggiornato i rispettivi `.env`, altrimenti i processi già attivi restano con la
credenziale vecchia finché non si riconnettono da soli (e nel frattempo il sito va in
500 in modo intermittente/imprevedibile). Questa VPS ospita anche altri siti
(`bionit`, `coge`, altri backend su porte 8800-8803, gestiti da Caddy) — non toccati
da questo incidente.

## Import biografie "PROGRAMMI SALA" (2026-09-13)

Aggiunte le biografie di interpreti e compositori estratte dalle sezioni ESECUTORI /
CHI HA SCRITTO PER RAMIFICAZIONI dei 4 PDF, per completare le `Persona` create dal
import precedente. Nuovo comando
`concerti/management/commands/import_biografie_programmi_sala.py` (idempotente,
`--dry-run`, stesso pattern di `import_programmi_sala.py`): aggiorna solo `Persona`
con `bio` ancora vuota, non sovrascrive mai bio già presenti, non crea nuove righe
(`Persona.objects.get`, non `get_or_create`).

Nel frattempo l'utente ha cancellato volontariamente da admin 6 `Persona` compositore
create dal primo import (Máté Balogh, Maurizio Azzan, Agostino Di Scipio — ed.1; Pier
Luigi Billone — ed.2; Cesare Saldicco, Matteo Tundo — ed.3): scelta consapevole,
confermata con l'utente, non ripristinate. I `Brano` corrispondenti restano intatti
(il campo `compositore` è testo libero, non FK) — restano solo senza una `Persona`
collegata.

Risultato: 20 bio aggiunte, verificate via query diretta. Restano senza bio (nessun
testo disponibile in nessuno dei 4 PDF): Clara Dossena (danzatrice, ed.4), Filippo
Lepre (compositore, ed.2), Francesco Fiorenzani (compositore, ed.4) — 25/28 `Persona`
hanno ora una bio.

**Nota**: resta ancora da eliminare a mano in admin 1 riga `Brano` duplicata residua
(edizione 1, pk=15, Cristiano Pomante con compositore/titolo invertiti — le altre 4
duplicate segnalate in precedenza sono già state rimosse dall'utente).

## Migrazione su nuova VPS (2026-10-16) — completata, sito live su ramificazioni.ch

Nuova VPS: ov-78575b, 179.237.121.137 / 2001:1600:18:20c::224 (Infomaniak Public Cloud, OpenStack).
Vecchia: ov-af2505, 179.237.83.217. Niente Docker in prod: systemd (gunicorn) + Caddy + Postgres locale.

**Verifica post-setup (16/10, ~10:00 UTC)**:
- `ramificazioni.service` (blue :8804), `ramificazioni-green.service` (green :8805), caddy, postgresql: tutti active.
  Live = green (8805). Green = `989fe57` (= origin/development); blue = `11609da` + `concerti/management/`
  non committato (stato identico alla VPS vecchia). Un `rollback` oggi riporterebbe codice più vecchio; un
  `update` allinea blue a origin/development (i file untracked restano).
- Dati ripristinati: Sede 2, Concerto 5, Brano 22, Persona 28, Partecipazione 29, FotoConcerto 1,
  Sostenitore 1, superuser `admin` attivo, 0 migrazioni pendenti.
- Media: 21 file, leggibili dall'utente caddy (ACL ok). Home `/it/` e `/admin/login/` = 200 su entrambi i colori.
- DNS: A+AAAA `ramificazioni.ch` già su questa VPS (NS Infomaniak); `www` NXDOMAIN.

**Problemi trovati e corretti (anche in `../deploy-ramificazioni.sh`)**:
| Problema | Causa | Fix |
|---|---|---|
| Health-check sempre verde anche col DB rotto | Accettava 301, e con `SECURE_SSL_REDIRECT` Django dà 301 a ogni richiesta HTTP prima di toccare il DB | Ora invia `X-Forwarded-Proto: https`, chiama `/it/` (context processor leggono il DB), accetta solo 200 |
| Errori ZeroSSL `caddy_legacy_user_removed` nei log | Caddy 2.6.2 (Debian) ripiega su ZeroSSL con vecchio endpoint EAB senza email | Blocco globale `{ cert_issuer acme }` (solo Let's Encrypt) nel Caddyfile; backup in `/etc/caddy/Caddyfile.bak-2026-10-16` |

**Bloccante aperto**: Let's Encrypt → "Timeout during connect" su 80/443. Nessun firewall locale (iptables
ACCEPT, niente nft/ufw); è il **security group OpenStack del provider** che lascia passare solo SSH. Va aperto
dal pannello Infomaniak, oppure con `../apri-porte-openstack.sh <file-openrc>` (crea il SG `ramificazioni-web` con TCP 80, TCP 443, UDP 443, v4+v6, e lo associa all'istanza via UUID dal metadata service; idempotente). Scelta finale: firewall VPS Infomaniak via import CSV `~/firewall_ramificazioni_import.csv` (formato del loro sample-firewall-rules-import.csv, diverso dall'export: TCP 80,443 + UDP 443 + SSH 22 per sicurezza, ip_type all = ogni sorgente). Poi aggiungere A/AAAA per `www`.
Dominio target: ramificazioni.ch (+ www → redirect). `../deploy-ramificazioni.sh` ha ora `DOMAIN` (default ramificazioni.ch)
e il comando `setup` (una tantum su Debian vergine, utente debian). Sulla VPS VECCHIA usare
`DOMAIN=ramificazioni.sabaconsulting.ch ./deploy-ramificazioni.sh ...`.

1. VPS vecchia:
   cd ~/apps/ramificazioni_website && set -a && . ./.env && set +a
   PGPASSWORD=$DB_PASSWORD pg_dump -h localhost -U $DB_USER -Fc $DB_NAME > backups/pre-vps.dump
   rsync -a --exclude .venv --exclude staticfiles --exclude __pycache__ ~/apps/deploy-ramificazioni.sh ~/apps/ramificazioni_website ~/apps/ramificazioni_website-green debian@NUOVA_VPS:apps/
2. VPS nuova: `cd ~/apps && ./deploy-ramificazioni.sh setup`
3. DNS A/AAAA ramificazioni.ch + www → nuova VPS. Niente modifiche in admin fra dump e switch DNS.

Note: rsync (non git clone) perché blue ha codice non committato (concerti/management/commands). Il setup rende
green/.env un symlink a blue/.env (prima avevano SECRET_KEY diverse → logout a ogni flip).
TODO: backup automatico DB (scripts/backup-db.sh usa docker, non vale per questa prod: proposto pg_dump + systemd timer), firewall = security group provider (22/80/443).

**16/10 ~10:20 UTC**: firewall VPS Infomaniak ok (TCP 80,443 / UDP 443 / SSH / ICMP, sorgente tutte). DNS rotto
durante l'aggiunta di `www`: sui NS Infomaniak l'apex non ha più A/AAAA e `www` ha valori troncati
(179.237.121.13 / 2001:1600:18:20c::22). Let's Encrypt in rate limit "5 failed authorizations/h" per entrambi i
nomi fino a ~10:30 UTC. Da fare: ripristinare A/AAAA dell'apex, correggere `www`, poi `systemctl restart caddy`.

**16/10 10:35 UTC — sito LIVE su https://ramificazioni.ch**. DNS corretto (4 record verificati su nsany1/nsany2),
certificati Let's Encrypt per apex e www (scadenza 14/01/2027, rinnovo automatico Caddy). Verificato: HTTPS
HTTP/2 + h3 annunciato, HSTS, http→https 308, www→apex 301 (v4 e v6), media 200 image/jpeg, /admin/login/ 200.
Fino a ~11:30 UTC qualche resolver può avere ancora in cache i vecchi record www troncati (TTL 1h).
Prossimi passi: backup automatico DB (pg_dump + systemd timer) da implementare.

## Audit privacy/cookie CH+UE (2026-10-16) — solo analisi, nessun fix applicato
Report completo in `AUDIT_PRIVACY.md`. Sintesi: nessun tracking/analytics; cookie solo tecnici (`csrftoken` su ogni
pagina perché il form `set_language` è in `base.html`, `django_language` al click). Da sistemare, in ordine:
1. Google Fonts da CDN (`templates/base.html:10-12`) → self-host in `static/fonts/`.
2. Privacy e Impressum inesistenti (footer `base.html:68-69` punta a `contacts`) → pagine reali IT/EN/DE/FR.
3. Form sponsor (`concerti/forms.py`) senza informativa/retention.
4. Bio inviate a Gemini (USA), liberatorie ritratti/foto, EXIF non ripulito, log Caddy e rotazione backup da definire.
Servono dati dall'utente: forma giuridica/indirizzo organizzatore, titolare, provider SMTP, liberatorie, tier Gemini.
Stato git: blue riallineato a `origin/development` (commit `205074e`, comandi di import + STATO_PROGETTO), non pushato;
backup della vecchia storia nel branch `backup/pre-realign-11609da`.

### Fix privacy applicati in locale (2026-10-16) — NON committati, NON deployati (live è ancora green senza questi fix)
- Google Fonts self-host: `static/fonts/` (14 woff2) + `@font-face` in `style.css`; tolte le righe Google da `base.html`.
- Pagine `/<lang>/privacy/` e `/<lang>/impressum/` (views, urls, `templates/concerti/privacy.html`, `impressum.html`), footer corretto. Campi titolare/ragione sociale/indirizzo/responsabile = «DA COMPLETARE».
- Informativa + link privacy sotto il form di `sostenitori.html`.
- EXIF: `concerti/imaging.py` (pre_save su Persona/FotoConcerto/Sostenitore), comando `strip_exif [--dry-run]` (NON lanciato sui media reali), test `concerti/tests.py`. JPEG ruotati ricodificati a q95.
- `scripts/backup-db.sh`: rotazione 30 giorni (ma il backup su questa prod è ancora da riscrivere: usa docker).
- Traduzioni EN/DE/FR aggiunte ai `.po`; `msgfmt` NON è installato sulla VPS: i `.mo` sono stati generati con uno script Python (verificato che le stringhe si caricano). Meglio rigenerarli con `compilemessages` dove c'è gettext.
Resta: compilare i dati «DA COMPLETARE», verificare log Caddy (nessuna direttiva `log`), liberatorie, tier Gemini, deploy.

### Dati legali da .env (2026-10-16)
Privacy/Impressum leggono titolare, ragione sociale, indirizzo, responsabile, telefono (opz.), email da `settings.LEGAL`
(variabili `LEGAL_*` nel `.env`, non in git; context processor `concerti.context_processors.legale`). Se vuote, i template
mostrano «DA COMPLETARE». Si compilano con `./scripts/compila-dati-legali.sh` (chiede i dati, valida, fa backup `.env.bak`,
scrive nel `.env` condiviso da blue e green). Dopo averlo eseguito: deploy/restart del servizio, i valori si leggono all'avvio.

### Anteprima della versione non deployata (2026-10-16)
Il colore blue/green NON live è visibile su `https://anteprima.ramificazioni.ch/` solo a chi è staff: link
«Anteprima versione non deployata» nella dashboard admin (`templates/admin/index.html`). Sull'host di anteprima il login è
separato da quello del sito (cookie per host). Codice: `PreviewStaffOnlyMiddleware` (`concerti/middleware.py`, test in
`concerti/tests.py`), `settings.PREVIEW_HOST` (env `PREVIEW_HOST`, default anteprima.ramificazioni.ch, aggiunto ad ALLOWED_HOSTS in prod).
Deploy (`../deploy-ramificazioni.sh`, fuori da git; copia pre-modifica: `deploy-ramificazioni.sh.bak-prima-anteprima`):
- `preview [ref]` = deploy sul colore idle SENZA switch; `switch` = mette live il colore idle; `update` invariato (switcha subito).
- `flip_caddy` ora scambia le porte di TUTTI i `reverse_proxy` (live e anteprima).
- `enable-preview` (una tantum): aggiunge il blocco `anteprima.<dominio>` a Caddy, valida e ricarica. NON ancora eseguito.
Da fare dall'utente: record DNS A 179.237.121.137 e AAAA 2001:1600:18:20c::224 per `anteprima.ramificazioni.ch`, poi deploy del codice e `enable-preview`.
Nota: `preview`/`update` eseguono `migrate` sul DB condiviso: le migrazioni toccano anche il sito live.
