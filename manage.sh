#!/bin/sh
# Avvia/ferma/aggiorna il sito Ramificazioni in locale (docker-compose.yml, dev).
# Uso: ./manage.sh {start|stop|restart|update|logs|status|shell|createsuperuser}

set -e
cd "$(dirname "$0")"

# Se l'utente non è nel gruppo docker, i comandi vanno lanciati con sudo:
# rileva automaticamente cosa serve, invece di farlo scegliere ogni volta.
if docker info >/dev/null 2>&1; then
  DC="docker compose"
else
  DC="sudo docker compose"
fi

if ! $DC version >/dev/null 2>&1; then
  echo "Errore: il demone Docker non è in esecuzione." >&2
  case "$(uname -s)" in
    Linux)
      echo "Avvialo con: sudo systemctl start docker" >&2
      ;;
    Darwin)
      echo "Avvialo con: open -a Docker" >&2
      ;;
    *)
      echo "Avvia Docker Desktop e riprova." >&2
      ;;
  esac
  exit 1
fi

usage() {
  echo "Uso: $0 {start|stop|restart|update|logs|status|shell|createsuperuser}"
  echo "  start           Avvia i container (senza rebuild)"
  echo "  stop            Ferma i container"
  echo "  restart         stop + start"
  echo "  update          Rebuild immagine (dopo modifiche a codice/requirements) e riavvia"
  echo "  logs            Segue i log del servizio web"
  echo "  status          Stato dei container"
  echo "  shell           Shell Django (manage.py shell) dentro il container"
  echo "  createsuperuser Crea un utente admin"
  exit 1
}

case "$1" in
  start)
    $DC up -d
    ;;
  stop)
    $DC down
    ;;
  restart)
    $DC down
    $DC up -d
    ;;
  update)
    $DC up -d --build
    ;;
  logs)
    $DC logs -f web
    ;;
  status)
    $DC ps
    ;;
  shell)
    $DC exec web python manage.py shell
    ;;
  createsuperuser)
    $DC exec web python manage.py createsuperuser
    ;;
  *)
    usage
    ;;
esac
