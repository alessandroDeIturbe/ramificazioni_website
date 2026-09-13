# RAMIFICAZIONI — Requisiti del sito

Checklist funzionale/contenuti basata su ricerca di siti comparabili: rassegne svizzere di musica contemporanea/da camera (Gare du Nord Basel, Lucerne Festival, sito eventi del Conservatorio della Svizzera Italiana), tedesche (Wittener Tage für neue Kammermusik) e italiane (MITO SettembreMusica). Ramificazioni è una piccola rassegna indipendente non-profit (4 concerti/stagione; la stagione 2025/26 è stata ospitata dal Conservatorio della Svizzera Italiana, senza altro legame organizzativo) — la lista è proporzionata a quella scala, non a un festival commerciale grande (niente carrello e-commerce, niente CRM complesso).

`[x]` = fatto nella bozza statica attuale · `[ ]` = da fare · nota tra parentesi = stato parziale/cosa manca ancora.

## Struttura / Navigazione

- [x] Header con menù: Home; About; Events; Contacts; Contributors
- [ ] Footer con: link social, contatti, link legali (privacy/cookie), logo sostenitori, newsletter
      (parziale: social+email presenti; link legali puntano a `#`, loghi sostenitori e form newsletter mancanti)
- [x] Switcher lingua sempre visibile in header (stub visivo — funzionalità reale in "Multilingua")
- [x] Pagina "Events" con calendario/lista della stagione corrente + archivio stagioni passate
      (lista stagione corrente e passata su `/events/`; tutte le stagioni ora anche elencate
      in un dropdown "Stagioni" in header, più recente in cima, ognuna con pagina dedicata
      `/stagioni/<stagione>/` — sostituisce la sezione "stagione corrente" prima in home)
- [x] Pagina singolo evento con URL propria (linkabile/condivisibile) — evento-a/b/c/d.html

## Homepage

- [x] Prossimo concerto in evidenza (data, ora, sede, compositore in cartellone) con CTA a pagina evento
      (dati segnaposto: sede/ora/compositore da confermare)
- [x] Vista d'insieme della stagione: card per ciascuno dei 4 concerti, ognuna con il proprio
      gradiente-edizione (vedi design system) come sfondo
- [x] Breve testo "cos'è Ramificazioni" (rassegna indipendente di musica da camera
      contemporanea/elettroacustica) con link a "About"
- [ ] Eventuale streaming/video del concerto più recente, se disponibile

## Pagina Evento/Concerto

- [x] Data, ora, sede (nome luogo + indirizzo) — valori segnaposto
- [ ] Programma musicale: compositore(i) in cartellone, titoli dei brani eseguiti
      (parziale: compositore segnaposto presente, titoli dei brani non ancora inclusi)
- [x] Interpreti/formazione (nomi + strumento/ruolo) — segnaposto
- [x] Ruolo "Regia Audio" (elettronica live) sempre indicato distintamente dagli altri interpreti
- [x] Nota di programma / testo introduttivo sul compositore o sul concerto — sezione presente, testo da scrivere
- [x] Indicazione se è prima esecuzione/prima svizzera/prima assoluta, quando applicabile — riga presente, da compilare
- [ ] Mappa/indicazioni per raggiungere la sede (solo testo segnaposto, nessuna mappa incorporata)
- [ ] Foto del concerto (dopo l'evento, galleria documentaria — vedi design system §7)
- [x] Link/bottone per prenotazione posto o biglietto
      (CTA presente ma non collegato a un sistema/link reale)
- [ ] Stato evento: futuro / passato (nasconde CTA prenotazione sugli eventi passati) — non implementato, le 4 pagine sono identiche in struttura

## Pagina About

- [x] Presentazione della rassegna: storia, missione, indipendenza organizzativa (Conservatorio
      della Svizzera Italiana = sede ospitante stagione 2025/26, non ente promotore)
- [x] Squadra/direzione artistica (nomi, ruoli, breve bio) — 1 scheda segnaposto
- [ ] Eventuale timeline delle stagioni passate (solo nota placeholder)

## Pagina Contributors

- [x] Elenco musicisti/compositori/regia audio coinvolti nella stagione, con breve bio
      (solo edizione I popolata, edizioni II–IV da completare)
- [x] Foto ritratto per ciascuno, se disponibile (foto reali caricate per parte dei
      collaboratori; fix opacità CSS che le rendeva sbiadite)
- [x] Collegamento dalla scheda contributor ai concerti in cui è coinvolto

## Multilingua

- [x] Traduzione reale in IT, DE, FR, EN (non più uno stub "automatico": stringhe dei
      template marcate `{% trans %}`/`{% blocktrans %}`, tradotte a mano in
      `locale/{de,fr,en}/LC_MESSAGES/django.po` e compilate in `.mo`, committati nel
      repo — non serve `makemessages`/`compilemessages` al deploy finché il testo non
      cambia). Contenuti DB traducibili (nota di programma, bio) via campi ombra per
      lingua (`_en`/`_de`/`_fr`) con fallback automatico all'italiano se non ancora
      compilati — niente pacchetto esterno, solo 2 campi coinvolti. Bio traducibili
      con assistenza Gemini da admin (azione "Traduci bio mancanti", richiede
      `GEMINI_API_KEY`). Nomi propri e
      titoli dei brani restano volutamente in una sola lingua (convenzione musicale
      standard, non un limite tecnico).
- [x] Switcher lingua persistente tra le pagine — form funzionante (`set_language`)
      in ogni pagina, cambia lingua mantenendo la pagina corrente
- [x] URL localizzati per lingua (`/it/...`, `/de/...`, `/fr/...`, `/en/...` via
      `i18n_patterns`) per SEO e condivisione
- [x] Dashboard admin in italiano indipendentemente dalla lingua del browser
      (`/admin/` forzato a `it` via middleware — l'admin di Django è già tradotto,
      non serve un catalogo nostro)

## Contatti e sede

- [ ] Pagina/sezione Contacts: email, eventuale telefono, form di contatto
      (parziale: solo email via mailto, niente telefono né form)
- [ ] Indirizzo/mappa della sede principale dei concerti (solo testo segnaposto, nessuna mappa)
- [x] Link ai canali social (Instagram @ramificazioni.festival)

## Newsletter e social

- [ ] Form di iscrizione newsletter (footer o pagina dedicata) per avvisi nuova stagione/concerto
      (solo nota testuale su pagina Contacts, nessun form funzionante)
- [ ] Link social in header/footer con icone coerenti col logo a tratto (§6 design system)
      (parziale: link testuali presenti, icone non ancora fatte)
- [ ] Meta tag Open Graph/Twitter Card per condivisione social delle pagine evento
      (parziale: solo `og:title`/`og:type` su evento-a.html; mancano su tutte le altre pagine, manca immagine preview e Twitter Card)

## Sostenitori/Partner

- [x] Sezione loghi sostenitori/partner — pagina dedicata "Sostenitori" in header (oltre
      alle miniature già presenti nel footer), con loghi dei sostenitori attivi
- [x] Form per proporsi come nuovo sponsor (nome/email/messaggio → email all'admin,
      honeypot anti-spam) — nella stessa pagina Sostenitori
- [ ] Eventuale nota di ringraziamento/crediti istituzionali

## SEO e performance

- [ ] Title/meta description per pagina, per lingua
      (parziale: presenti per ogni pagina, solo in italiano)
- [ ] Immagini poster/locandina ottimizzate (formati moderni, lazy-loading galleria eventi)
      (non ancora applicabile: nessuna galleria fotografica presente)
- [ ] Sitemap.xml e robots.txt
- [ ] Markup dati strutturati evento (schema.org `Event`) per ogni concerto

## Legale/Privacy

- [ ] Pagina Privacy Policy (trattamento dati form contatto/newsletter, GDPR/LPD svizzera)
- [ ] Cookie banner minimale se si usano cookie di tracciamento/analytics
- [ ] Pagina Impressum/note legali

## Accessibilità

- [ ] Contrasto testo/sfondo verificato su ogni gradiente-edizione (non ancora verificato con strumenti WCAG)
- [x] Alt text per tutte le immagini (logo ha `alt`; nessun'altra immagine reale presente ancora)
- [ ] Navigazione da tastiera e focus visibile su menu/form (comportamento di default del browser, non testato esplicitamente)
- [x] `prefers-reduced-motion` rispettata (media query presente in style.css)

## Amministrazione contenuti (CMS)

Il sito è ora un'app Django (Postgres + admin) — non più HTML statico. La dashboard
è `/admin/` di Django, senza UI custom da costruire.

- [x] Interfaccia per aggiungere un nuovo concerto/edizione senza intervento tecnico
      — una pagina admin per Concerto con inline per brani/programma, interpreti e
      regia audio, foto; `date_hierarchy` per navigare/correggere le date. Nuova
      stagione (es. 2026/27) = nuovo Concerto con `stagione="2026/27"`, nessuna
      migrazione o azione speciale richiesta.
- [x] Possibilità di caricare foto galleria post-concerto autonomamente (`FotoConcerto`
      con `ImageField`, inline nella pagina del concerto)
- [x] Gestione multilingua dei contenuti editoriali dal medesimo pannello — i campi
      `_en`/`_de`/`_fr` di nota di programma e bio sono editabili nella stessa scheda
      admin del contenuto italiano (vedi "Multilingua")
