# RAMIFICAZIONI — Design System

Reference sources: 4 locandine ufficiali A3 (stagione 2025/26: 4 dic 2025, 5 feb 2026, 12 mar 2026, 7 mag 2026), il logo/icona profilo Instagram (@ramificazioni.festival), e una foto di scena reale dell'evento del 4 dic 2025. Ogni token qui sotto è osservato direttamente da questi materiali — non inventato. Gli hex sono stime a occhio dai PDF/immagini (nessun file sorgente InDesign/Illustrator disponibile): trattali come punto di partenza solido per la prima bozza del sito, da rifinire campionando i pixel se serve precisione assoluta.

Ramificazioni è una rassegna indipendente di musica da camera contemporanea/elettroacustica (Lugano) — quattro concerti a stagione, ognuno con un proprio compositore in cartellone e un ruolo "Regia Audio" dedicato all'elettronica live. La stagione 2025/26 è stata ospitata dal Conservatorio della Svizzera Italiana (sede, non affiliazione organizzativa) — non è una rassegna del Conservatorio. Non confondere con altri progetti omonimi trovati online (un festival di danza in Calabria, un ciclo Verdi a Parma, un progetto artistico nel Mediterraneo) — nessuno di quelli è questo.

## 1. Philosophy

- **Un'unica idea visiva, ripetuta e variata**: una fotografia-simbolo di un ramo spoglio, fotografato una volta e poi virato di colore a ogni edizione. Non è decorazione — è la traduzione letterale del nome "Ramificazioni" (biforcazioni, linee che si diramano, come le voci musicali di un ensemble). Ogni superficie nuova (sito, locandina, programma di sala) dovrebbe portare questo stesso ramo, mai un albero diverso o un'illustrazione generica di natura.
- **Nessun colore di brand fisso — un sistema stagionale.** A differenza di un brand con palette fissa (vedi ASSUML), Ramificazioni cambia gradiente pastello a ogni concerto/edizione. La costante non è "questo colore" ma "questo *tipo* di gradiente" (acquarellato, pastello, a due o tre toni ravvicinati) più un accento di contrasto scelto apposta per quell'edizione. Il sito dovrebbe replicare questa logica: ogni pagina-evento ha la sua variante cromatica, non un'unica palette piatta su tutto il sito.
- **Serif elegante + sans morbido, mai altro.** Solo due famiglie tipografiche: una serif ad alto contrasto per il wordmark e i numeri di edizione (voce "istituzionale", quasi da conservatorio/etichetta discografica classica), e un sans geometrico dai terminali morbidi per tutto il resto (date, crediti, corpo testo). Non introdurre una terza famiglia.
- **Molto spazio negativo, poca decorazione.** Le locandine sono per il 55-60% campo vuoto (gradiente + wordmark + info), la foto occupa solo la fascia inferiore. Non riempire: la calma dello spazio bianco/pastello è parte dello stile quanto il ramo stesso.
- **Fotografia reale, mai stock patinato.** Le foto di scena/backstage sono documentarie: luce calda pratica (lampade da leggio, schermi) contro ambiente scuro, poca posa, grana filmica.  Questo vale per qualunque galleria fotografica del sito — non sostituire con foto da banca immagini "pulite".
- **Il tratto del logo è unico e non negoziabile.** Un solo peso di linea, nessun riempimento pieno, nessuna ombra. Se il logo non si legge bene su uno sfondo, cambia lo sfondo (una card bianca/chiara dietro), non il logo.

## 2. Color

### La logica: gradiente-per-edizione + accento di contrasto

Non esiste un `--primary` fisso. Ogni "edizione" (concerto, o sul sito: ogni evento/pagina) è definita da **due token**: uno sfondo gradiente pastello acquarellato, e un colore di accento scelto per contrastare bene con quello sfondo specifico (usato solo per il numero/testo d'evidenza, es. "2025/26"). Ecco le quattro varianti osservate, da usare come palette di partenza e come modello per generarne di nuove:

```css
:root {
  --ink: #171512;              /* quasi-nero, testo/wordmark/hairline su ogni edizione */
  --paper-line: rgba(23,21,18,0.16); /* hairline dei blocchi info/crediti */

  /* Edizione A — 4 dicembre: oro/ambra caldo */
  --ed-a-bg: linear-gradient(160deg, #f6dfa0 0%, #f0c96a 45%, #eecf8f 100%);
  --ed-a-accent: #ffffff;

  /* Edizione B — 5 febbraio: sabbia/kaki chiaro */
  --ed-b-bg: linear-gradient(160deg, #ece2c2 0%, #ddd0a3 50%, #cfc9ad 100%);
  --ed-b-accent: #6b7a8f; /* grigio-blu ardesia */

  /* Edizione C — 12 marzo: verde salvia/menta */
  --ed-c-bg: linear-gradient(160deg, #d9e8d6 0%, #c7ddc9 50%, #dce6da 100%);
  --ed-c-accent: #e8875a; /* corallo-arancio */

  /* Edizione D — 7 maggio: azzurro polvere */
  --ed-d-bg: linear-gradient(160deg, #cfe1ee 0%, #b9d3e6 45%, #d6e6ef 100%);
  --ed-d-accent: #eda6a0; /* rosa salmone */
}
```

**Regola per crearne di nuove:** scegli sempre un gradiente *pastello, ravvicinato di tono* (mai saturo, mai più di ~20-25% di variazione di luminosità tra gli stop) e un accento che stia sull'altro lato della ruota cromatica rispetto al gradiente — se lo sfondo è caldo (oro, sabbia) l'accento tende freddo/neutro (bianco, grigio-blu); se lo sfondo è freddo (menta, azzurro) l'accento tende caldo (corallo, salmone). Non riusare mai lo stesso accento su due edizioni consecutive.

**Texture, non gradiente piatto.** Nei PDF originali il gradiente non è un `linear-gradient` pulito a due stop: è più simile a un acquerello — nuvoloso, leggermente marmorizzato, con variazioni di tono morbide e irregolari. Un `linear-gradient` a 3 stop come sopra è una approssimazione accettabile per CSS puro; se serve più fedeltà, sovrapponi un `background-blend-mode: overlay` con un file di texture (grana/carta) leggerissimo, oppure usa 2-3 `radial-gradient` sfocati sovrapposti invece di uno solo lineare:

```css
.edition-bg {
  background:
    radial-gradient(ellipse at 20% 15%, rgba(255,255,255,0.35), transparent 60%),
    radial-gradient(ellipse at 80% 90%, rgba(0,0,0,0.06), transparent 55%),
    var(--ed-a-bg);
}
```

### Inchiostro e opacità del testo

Un solo `--ink` quasi-nero (`#171512`, non nero puro) usato su ogni edizione senza eccezioni — è ciò che tiene insieme visivamente le quattro varianti di sfondo. Testo secondario per opacità, non per grigio a parte (stessa convenzione di ASSUML):

| Opacità | Uso |
|---|---|
| `1` | Wordmark, numero edizione, etichette crediti (bold) |
| `0.82` | Nomi negli slot crediti, corpo testo |
| `0.55` | Meta/didascalie, orario secondario |

Non introdurre mai bianco/nero puro come superficie: lo sfondo è sempre uno dei gradienti-edizione, mai `#fff` piatto (eccetto eventuali card UI tecniche come form, dove il bianco puro è accettabile proprio perché *distinto* dal linguaggio delle locandine).

## 3. Typography

```css
:root {
  --font-display: 'Playfair Display', 'Times New Roman', serif; /* wordmark, numeri edizione */
  --font-body:    'Poppins', sans-serif;                        /* tutto il resto */
}
```
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;800&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
```
`Playfair Display` è la scelta Google Fonts più vicina alla serif ad alto contrasto vista nelle locandine (tagli sottili, ampiezza generosa delle maiuscole); se in futuro si recupera il font originale del grafico, sostituire qui senza toccare il resto del sistema — tutto il resto referenzia solo la custom property.

**Wordmark.** Sempre tutto maiuscolo, tracking ampio, nessun peso oltre 700/800:
```css
.wordmark {
  font-family: var(--font-display); font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.01em; color: var(--ink); line-height: 0.95;
  font-size: clamp(2.2rem, 7vw, 5.5rem);
}
```

**Numero edizione** ("2025/26" e varianti future): stessa serif, peso più leggero del wordmark, colore = accento dell'edizione corrente, dimensione paragonabile al wordmark ma posizionato sotto-destra con leggera sovrapposizione:
```css
.edition-number {
  font-family: var(--font-display); font-weight: 500; color: var(--ed-accent, var(--ink));
  font-size: clamp(2rem, 6.5vw, 5rem); line-height: 0.9;
}
.edition-number .slash { opacity: 0.85; } /* la "/" tra 2025 e 26 è più leggera nel peso visivo */
```

**Blocco info (data/ora/luogo) ed etichette crediti**: sans bold, terminali morbidi, nero pieno (non attenuato — è informazione pratica, deve leggersi a colpo d'occhio anche su un gradiente chiaro):
```css
.info-line { font-family: var(--font-body); font-weight: 600; color: var(--ink); line-height: 1.4; }
.credit-label { font-family: var(--font-body); font-weight: 700; font-size: var(--small-size); }
.credit-name  { font-family: var(--font-body); font-weight: 400; opacity: 0.82; }
```

Scala fluida (stesso principio ASSUML — `clamp()`, non breakpoint fissi):
```css
:root {
  --title-size: clamp(2.2rem, 7vw, 5.5rem);
  --h2-size:    clamp(1.5rem, 4vw, 2.6rem);
  --body-size:  clamp(0.85rem, 1.3vw, 1rem);
  --small-size: clamp(0.7rem, 1vw, 0.85rem);
}
```

## 4. Layout — lo schema-locandina

Le quattro locandine condividono esattamente questa struttura verticale; è il pattern da riusare per l'header di ogni pagina-evento del sito (hero di una singola data, o intestazione di sezione "prossimo concerto"):

1. **Logo + wordmark**, allineati a sinistra, in alto.
2. **Numero edizione**, subito sotto, leggermente sovrapposto al wordmark, allineato verso destra del wordmark stesso (non centrato, non a sinistra).
3. **Blocco data/ora/luogo**, 3 righe (data — ora — sede), allineato a sinistra, sans bold.
4. **Riga hairline** a tutta larghezza, sottile, `var(--paper-line)`.
5. **Griglia crediti**, 3 o 4 colonne a seconda del numero di ruoli in cartellone (strumentisti + "Regia Audio" + "Musiche di" con lista compositori multi-riga), ogni colonna centrata al suo interno, colonne separate da gap generoso.
6. **Foto del ramo**, full-bleed (bordo a bordo, anche oltre i margini laterali della pagina), ancorata in fondo, ~35-40% dell'altezza totale, colorata/virata per intonarsi al gradiente dell'edizione corrente.

```css
.poster-header { padding: clamp(1.5rem, 5vw, 4rem); display: flex; flex-direction: column; gap: clamp(0.5rem, 2vw, 1.5rem); }
.poster-credits { display: grid; grid-template-columns: repeat(var(--credit-cols, 4), 1fr); gap: clamp(1rem, 3vw, 2rem); border-top: 1px solid var(--paper-line); padding-top: clamp(1rem, 3vw, 2rem); text-align: center; }
.poster-photo { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; margin-top: auto; }
@media (max-width: 640px) { .poster-credits { grid-template-columns: repeat(2, 1fr); } }
```

Su schermi stretti la griglia crediti passa da 3-4 a 2 colonne (mai a colonna singola: i crediti sono brevi, una sola colonna sprecherebbe verticalità senza motivo).

**Spaziatura generale** (stesso principio `clamp()` di ASSUML §4):
```css
:root {
  --page-padding: clamp(1.25rem, 5vw, 4rem);
  --section-gap:  clamp(2rem, 6vw, 5rem);
}
```

## 5. Motion

Il materiale sorgente (locandine statiche PDF) non definisce motion — per il sito, applicare solo principi leggeri e non invasivi, coerenti con la calma del sistema:

- **Reveal-on-scroll discreto**: fade + piccolo rise (stesso pattern `.reveal`/`IntersectionObserver` di ASSUML §5), usato per far comparire wordmark → numero edizione → info → crediti in sequenza quando l'header di una pagina-evento entra in vista. Nessun overshoot vistoso: transizioni morbide (`ease`, 0.5-0.6s), non elastiche — il tono è editoriale/da conservatorio, non da deck energico.  
- **Transizione di colore tra edizioni**: se il sito passa da una pagina-evento all'altra (o da una card evento all'altra in una lista), il cambio di gradiente-sfondo può animarsi via `transition: background 0.4s ease` — mai un taglio netto, il passaggio di palette dovrebbe sentirsi fluido come lo è visivamente tra le quattro locandine.
- **Rispetta sempre `prefers-reduced-motion`** (stessa regola ASSUML §5):
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.2s !important; }
}
```
- Non serve nulla di più elaborato (niente FLIP, niente scroll-scrubbing): è materiale da concerto di musica da camera, non una presentazione da proiettare — l'energia va nella tipografia e nel colore, non nel movimento.

## 6. Iconografia — il logo

Il logo è un emblema circolare: un anello sottile racchiude un albero stilizzato a tratto unico (chioma arrotondata composta da rami sottili biforcati, tronco visibile alla base). Un solo peso di linea, nessun riempimento pieno, nessun colore fuori da `var(--ink)`.

```html
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="icon-ramificazioni-tree" viewBox="0 0 64 64">
    <!-- ridisegnare a tratto singolo (stroke, no fill) dal file logo originale;
         stroke="currentColor" cosi' eredita var(--ink) o l'accento dell'edizione -->
  </symbol>
</svg>
<svg width="40" height="40" style="color:var(--ink)"><use href="#icon-ramificazioni-tree"></use></svg>
```
Usare `stroke="currentColor"` (non un colore fisso nel simbolo) così il logo può ereditare `var(--ink)` ovunque, o eccezionalmente l'accento dell'edizione se serve un logo "in tinta" su un elemento decorativo. Non ricolorare mai il logo con un riempimento pieno o un gradiente — perde immediatamente la lettura da sigillo/timbro che ha nell'originale.

## 7. Component Patterns

### Colonna-credito
```css
.credit-col { display: flex; flex-direction: column; align-items: center; gap: 0.3rem; }
.credit-col .credit-label { text-align: center; }
.credit-col .credit-name  { text-align: center; }
```
Per "Musiche di" con più compositori, ogni nome è una riga propria dentro la stessa colonna — non separare i compositori in colonne aggiuntive, restano impilati verticalmente in un'unica colonna "Musiche di".

### Numero-edizione come elemento isolato
Riusabile fuori dal contesto locandina — es. per intestare una lista di concerti passati/futuri — come "numero grande in tinta accento" isolato:
```css
.edition-badge {
  font-family: var(--font-display); font-weight: 500; font-size: clamp(1.4rem, 3vw, 2rem);
  color: var(--ed-accent); line-height: 1;
}
```

### Foto-ramo tonalizzata per sezione
Variante del pattern `.photo-organic` di ASSUML: invece di tilt/rotazione, l'organicità viene da un **overlay colore per edizione** sopra la stessa foto sorgente in bianco e nero/desaturata — così la stessa immagine può comparire in ogni pagina-evento già "vestita" del colore giusto senza dover rifare l'export per ogni palette:
```css
.branch-photo { position: relative; overflow: hidden; }
.branch-photo img { display: block; width: 100%; height: 100%; object-fit: cover; filter: grayscale(1) contrast(1.05); }
.branch-photo::after {
  content: ""; position: absolute; inset: 0; mix-blend-mode: multiply; opacity: 0.9;
  background: var(--ed-a-bg); /* sostituire con il gradiente dell'edizione corrente */
}
```
Usa `mix-blend-mode: multiply` (non `overlay`) — è quello che dà l'effetto "foto virata color seppia/blu" visto nelle locandine reali, mantenendo i rami scuri leggibili sopra qualunque tinta.

### Galleria foto-evento (documentaria)
Per foto reali di backstage/concerto (non il ramo-simbolo): niente filtro/tinta uniforme, si lasciano i toni caldi/freddi naturali dello scatto. Layout a griglia semplice, non organico/tiltato (quello è riservato al ramo-simbolo, che è l'unico elemento "artistico" del sistema — le foto documentarie restano oneste, senza trattamento grafico sopra):
```css
.event-gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: clamp(0.5rem, 1.5vw, 1rem); }
.event-gallery img { width: 100%; aspect-ratio: 3/2; object-fit: cover; }
```

## 8. Applicazione al sito

1. **Homepage / lista concerti**: ogni concerto della stagione è una card o sezione con il proprio gradiente-edizione (§2) come sfondo — non un'unica palette per tutto il sito. Se la stagione ha più di 4 concerti, genera nuovi gradienti seguendo la regola pastello+accento-contrastante di §2, non riusare esattamente i 4 già assegnati a concerti passati.
2. **Pagina di un singolo concerto**: riusa lo schema-locandina intero (§4) come hero della pagina — wordmark, numero edizione, data/ora/luogo, crediti, foto-ramo tonalizzata in fondo. È essenzialmente la locandina resa responsive.
3. **Header/footer globali del sito** (non legati a un concerto specifico): usa `var(--ink)` su sfondo chiaro neutro, logo in `currentColor`, senza gradiente-edizione — il gradiente è un linguaggio *per evento*, non per il chrome di navigazione persistente.
4. **Galleria fotografica**: foto documentarie oneste (§7) per il recap di un concerto passato; riserva la foto-ramo tonalizzata per elementi editoriali/hero, mai per la galleria stessa.
5. **Nuove edizioni future**: quando si aggiunge un quinto concerto e oltre, non improvvisare un colore qualsiasi — segui sempre la coppia gradiente-pastello-ravvicinato + accento-di-contrasto di §2, e verifica che l'accento scelto non sia già usato dall'edizione immediatamente precedente.
