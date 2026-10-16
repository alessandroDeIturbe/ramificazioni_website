"""
Aggiunge le biografie di interpreti e compositori estratte dai PDF "programma di
sala" (sezioni ESECUTORI / CHI HA SCRITTO PER RAMIFICAZIONI) in
"PROGRAMMI SALA-20260913T144404Z-1-001.zip", per le Persona già create da
import_programmi_sala.py.

Idempotente e non distruttivo: aggiorna solo Persona con bio ancora vuota, non
sovrascrive mai una bio già presente, non crea nuove Persona (se una riga attesa
non esiste più viene solo segnalata).

Uso:
    manage.py import_biografie_programmi_sala --dry-run
    manage.py import_biografie_programmi_sala
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from concerti.models import Persona

DATA = [
    # --- Edizione 1 (4 dicembre 2025) ---
    {
        "nome": "Cristiano Pomante", "ruolo": "compositore",
        "bio": (
            "Cristiano Pomante è un compositore e performer. Si diploma giovanissimo con "
            "lode in strumenti a percussione, sotto la guida di Clara Perra al Conservatorio "
            "di Pescara. Ha poi perfezionato la tecnica sul vibrafono jazz e l'improvvisazione "
            "con Andrea Dulbecco, al Conservatorio di Milano. La sua ricerca continua "
            "esplorando l'interazione tra musica improvvisata e scritta, culminando nel "
            "diploma in composizione con Giovanni Verrando alla Scuola Civica Abbado di "
            "Milano.\n\n"
            "Ha seguito masterclass con figure di spicco come Marco Momi, Ramberto "
            "Ciammarughi, Simon Steen-Andersen, Stefan Prins, Tristan Murail, Mike Mainieri e "
            "David Friedman. Iniziata la carriera come orchestrale, si è poi distinto come "
            "vibrafonista jazz, guidando proprie formazioni e collaborando con importanti "
            "musicisti del panorama italiano. Da diversi anni si dedica in particolare alla "
            "composizione per musica mista, svolgendo la sua attività professionale con "
            "grande versatilità.\n\n"
            "Il suo lavoro compositivo è incentrato sul legame tra gesto strumentale e "
            "processi di elaborazione sonora, con l'obiettivo di unire strumenti acustici, "
            "tecnologie digitali e linguaggi multimediali in un'esperienza performativa "
            "unitaria. Le sue composizioni sono state eseguite da Syntax Ensemble, "
            "Divertimento Ensemble e da solisti quali Myriam García Fidalgo ed Elio "
            "Marchesini. Il suo ultimo lavoro “Distortion Future”, brano per Grancassa "
            "video ed elettronica, è edito dalla SZ - Sugar di Milano."
        ),
    },
    {
        "nome": "Alessandro De Iturbe", "ruolo": "compositore",
        "bio": (
            "Nato a Tortona nel 2005, si avvicina alla musica all'età di otto anni iniziando "
            "lo studio del violoncello, strumento che lo accompagnerà per molti anni e con "
            "cui svilupperà una profonda sensibilità verso il suono. In seguito a difficoltà "
            "fisiche decide di interrompere il percorso strumentale e trasferirsi a Lugano, "
            "dove scopre nella composizione un nuovo spazio espressivo e di ricerca. "
            "Attualmente frequenta il Bachelor of Arts – Major in Theory and Composition "
            "presso il Conservatorio della Svizzera Italiana.\n\n"
            "L'interesse per la composizione nasce in un periodo personale complesso, "
            "inizialmente come forma di distrazione e poi come linguaggio necessario. La sua "
            "musica, ancora in evoluzione, si muove tra ordine e caos, alla ricerca di una "
            "voce autentica."
        ),
    },
    # --- Edizione 2 (5 febbraio 2026) ---
    {
        "nome": "Floriana Provenzano", "ruolo": "compositore",
        "bio": (
            "Floriana Provenzano (1998) è una compositrice italiana. La sua musica nasce "
            "spesso da immagini sonore e sensazioni visive e fisiche, sviluppandosi in "
            "esplorazioni di texture, luminosità e timbro. Utilizza frequentemente "
            "preparazioni strumentali, oggetti metallici e materiali non convenzionali, con "
            "l'obiettivo di ampliare il potenziale espressivo del suono.\n\n"
            "Le sue composizioni sono state eseguite da ensemble e solisti come zone "
            "expérimentale, Blaurenz Duo, Ensemble Sillages, Duo Dubois, mdi ensemble e "
            "Giulia Zaniboni, e presentate in festival internazionali tra cui impuls (AT), "
            "IntAct (TH), Mixtur (ES), Bludenzer Tage zeitgemäßer Musik (AT), Trame Sonore "
            "(Mantova, IT), Sound of Wander (Milano, IT), Musikàmera (Venezia, IT) e altri. È "
            "attualmente iscritta al Master in composizione presso il Conservatorio di "
            "Mantova, sotto la guida di Zeno Baldi e Maurizio Azzan."
        ),
    },
    {
        "nome": "Francesco Fausto Magaletti", "ruolo": "compositore",
        "bio": (
            "Francesco Fausto Magaletti (Bari, 2000) è chitarrista e compositore. Inizia la "
            "sua formazione musicale a 14 anni, affiancando fin da subito lo studio della "
            "chitarra a quello della composizione. Si laurea con lode in chitarra nel 2023 e "
            "avvia un'intensa attività concertistica nell'ambito della musica da camera. Dal "
            "2019 è attivo come camerista e cofondatore del Fairy Guitar Quartet, che nel "
            "2024 pubblica il suo primo album. Studia composizione dal 2015 con Gianvincenzo "
            "Cresta. A 17 anni ottiene la sua prima esecuzione pubblica con Lupus, "
            "selezionata da Zenit 2000 e vincitrice del premio del pubblico. Nel 2018 riceve "
            "la sua prima commissione dal festival Contemporaneamente Fisarmonica del "
            "Conservatorio di Santa Cecilia di Roma. Ha collaborato con musicisti ed "
            "ensemble di rilievo internazionale e la sua musica è eseguita in festival in "
            "Italia e all'estero. La sua musica, di forte impronta poetica, esplora "
            "recentemente il suono nello spazio e le illusioni prospettiche. Attualmente sta "
            "scrivendo la sua prima opera, Der Dichter Spricht, in debutto nel 2026. Studia "
            "composizione al Conservatorio di Milano con Gabriele Manca. Le sue opere sono "
            "pubblicate da Stradivarius Edizioni e SZ Sugar."
        ),
    },
    # --- Edizione 3 (12 marzo 2026) ---
    {
        "nome": "Massimo Restifo Pecorella", "ruolo": "interprete",
        "bio": (
            "Massimo Restifo Pecorella (Venezia 2000) consegue nel 2019 il Diploma "
            "Accademico di I livello in Clarinetto presso il Conservatorio di Musica "
            "“Benedetto Marcello” di Venezia, nel 2022 il Diploma Accademico di II livello "
            "in Clarinetto presso il Conservatorio di Musica “Giuseppe Verdi” di Milano e "
            "nel 2024 il Diploma Accademico di II livello in Musica d'Insieme presso il "
            "medesimo Conservatorio. Ha arricchito il suo percorso formativo con masterclass "
            "tenute da clarinettisti e musicisti di fama internazionale come Fabrizio "
            "Meloni, Fabio Di Casola, Lorenzo Coppola, Calogero Palermo, Andrea Massimo "
            "Grassi, Indrė Baikštytė, Rafael Albert Soler, Gitte Marcusson. Si è esibito come "
            "solista, orchestrale e camerista in Italia ed all'estero. Ha collaborato con la "
            "LNOBT Symphony, Orchestra Filarmonica “Mihail Jora” di Bacau Orchestra, Movies "
            "Classic Orchestra, Orchestra del Teatro Italia di Venezia, Orchestra Nazionale "
            "di Fiati dei Conservatori, Orchestra dei Solisti di Radio Veneto 1, Orchestra "
            "giovanile Filarmonici Friulani, Orchestra Sinfonica del Conservatorio di "
            "Venezia, Agimus Venezia, Youth Orchestra del Conservatorio di Milano, "
            "International Chamber Orchestra Academy, European Contemporary Music "
            "Ensemble, Kammarmusikens Vänner, Rencontres musicales de Méditerranée, La "
            "Biennale di Venezia. Nel 2024 pubblica per Möbius Duo l'album “Vilnian "
            "Textures” composto da improvvisazioni libere per l'etichetta Doppio Movimento. "
            "Dal 2021 al 2023 segue il corso libero di Elementi di Direzione d'Orchestra del "
            "M° Dario Bisso Sabàdin presso il Conservatorio di Venezia. Ha studiato direzione "
            "con Ennio Nicotra, Fabrizio Dorsi e Roberto Perata e dal 2024 studia sotto la "
            "guida del M° Donato Renzetti. Il suo repertorio direttoriale include "
            "compositori classici, romantici e moderni. Nel 2023 dirige a Molfetta "
            "l'Ouverture “Coriolano” Op.62 di L. van Beethoven eseguita dall'Orchestra "
            "Filarmonica Pugliese."
        ),
    },
    {
        "nome": "Elide Sulsenti", "ruolo": "interprete",
        "bio": (
            "Elide Sulsenti è una violoncellista e ricercatrice appassionata di "
            "sperimentazione e innovazione. La sua formazione classica, che include un "
            "diploma presso il Conservatorio di Cagliari nella classe di Oscar Piastrelloni "
            "e studi presso il Conservatorio della Svizzera Italiana nella classe di Enrico "
            "Dindo e la Hochschule di Lucerna, oltre a esperienze in accademie come la "
            "Ferenc Liszt Academy di Budapest, l'ha portata a dedicarsi alla musica "
            "contemporanea e all'esplorazione di nuovi potenziali sonori. Con un approccio "
            "interdisciplinare, Elide integra tecnologie, strumenti aumentati e pratiche "
            "performative in contesti non convenzionali. Le sue esibizioni, che spaziano "
            "dalla musica classica alla contemporanea, le hanno valso riconoscimenti come il "
            "Fritz Gerber Award (2023) e il Premio Valentino Bucchi (2024). Unisce la "
            "ricerca artistica alla sperimentazione, con un'attenzione particolare "
            "all'interazione tra spazio, suono e pubblico, che è attualmente il focus del "
            "suo progetto di dottorato presso il Conservatorio di Ferrara.\n\n"
            "Oltre alla sua attività accademica, Elide partecipa attivamente come solista o "
            "in ensemble a festival internazionali come il Lucerne Festival (Svizzera), il "
            "Connect Festival (Svezia) e l'EstOvest Festival (Italia). Collabora con "
            "compositori di diverse provenienze e tiene workshop e masterclass annuali "
            "presso istituzioni come la Lund University e il KUG di Graz. Attualmente, Elide "
            "è artista in residenza presso l'Inter Arts Center (IAC) a Malmö."
        ),
    },
    {
        "nome": "Federico Pezzatini", "ruolo": "compositore",
        "bio": (
            "Federico Pezzatini è un compositore attivo nella musica contemporanea, "
            "elettronica e multimediale. Diplomato in chitarra presso la University of East "
            "London, poi in Musica Applicata alle Immagini con il massimo dei voti presso la "
            "Civica Scuola di Musica “C. Abbado” e consegue il Master in Composizione e "
            "Teoria presso il Conservatorio della Svizzera Italiana nel 2026. Nel 2025 segue "
            "il corso di Live Electronics presso l'Accademia Chigiana di Siena, ottenendo il "
            "diploma di merito. L'anno successivo diviene parte del Chigiana Live "
            "Electroncis Ensemble. Ha partecipato alle masterclass di Mauro Lanza, Francesca "
            "Verunelli, Ivan Fedele, Luis Naón, Marco di Bari, Eric Maestri e Miliça "
            "Djordjevic. Federico è uno dei tre direttori artistici di Ramificazioni, "
            "festival di musica contemporanea dedicato a giovani compositori ed esecutori. "
            "La sua musica è stata eseguita in Italia, Svizzera, Inghilterra e Lituania."
        ),
    },
    {
        "nome": "Maria Vittoria Agresti", "ruolo": "compositore",
        "bio": (
            "Maria Vittoria Agresti ('96 Caserta, Italia) è una compositrice italiana la cui "
            "principale attenzione è rivolta all'esplorazione e allo studio del timbro come "
            "veicolo per la percezione del suono. Iniziati gli studi di pianoforte in "
            "giovanissima età, si è diplomata al Conservatorio di Avellino con il massimo "
            "dei voti in composizione (Maria Pia Sepe) e pianoforte (Sergio Di Gennaro). Nel "
            "2021 ha frequentato il corso di perfezionamento in musica da camera presso la "
            "Scuola di Musica di Fiesole, sotto la guida di Alain Meunier e Simone "
            "Bernardini. Successivamente ha conseguito il corso di alto perfezionamento con "
            "il massimo dei voti in composizione presso l'Accademia Nazionale di Santa "
            "Cecilia sotto la guida di Ivan Fedele, frequentando contemporaneamente anche il "
            "corso di musica elettronica con Michelangelo Lupone. I suoi lavori hanno "
            "ricevuto numerosi premi e riconoscimenti, collaborando con importanti "
            "compositori e artisti come U.Chin, F. Filidei, C. Czernowin, F. Verunelli, M. "
            "Stroppa, M. Momi, N. Vassena, L. Ronchetti, J.M. Sánchez-Verdú, G. Cresta, A. "
            "Solbiati, G. Battistelli e altri.\n\n"
            "I suoi brani sono stati eseguiti in Italia, Austria, Svizzera, Germania, Serbia "
            "e Portogallo da rinomati ensemble e orchestre quali Kalngforum Wien, Names "
            "Ensemble, RePercussion Trio, Concrete [Lab] Ensemble, Syntax Ensemble, NEMA "
            "Ensemble, AchRome Ensemble, Orchestra d'archi G.G. Arrigoni, Ensemble "
            "Dissonanzen, Orchestra Sinfonica D'Este e da importanti artisti quali Gregor "
            "Mayrhofer, Jack Sheen, F. D'Orazio, A. D'Errico, M. Boselli, E. Marchesini e "
            "altri. Nel 2025 è stata selezionata per la residenza compositiva all' Académie "
            "du Festival d'Aix-en-Provence sotto la guida di Unusk Chin. Attualmente "
            "frequenta l'Accademia di Belle Arti di Napoli per un dottorato di ricerca in "
            "“Innovation, Technologies and New Materials for Art”."
        ),
    },
    {
        "nome": "Gaia Aloisi", "ruolo": "compositore",
        "bio": (
            "La musica di Gaia Aloisi (Cagliari, 1995) esplora la relazione tra suono, corpo "
            "e gesto, con particolare attenzione alla voce come corpo sonoro e materia "
            "plastica. I suoi lavori, regolarmente commissionati ed eseguiti in contesti "
            "internazionali, sono stati presentati in festival come Tête à Tête (Londra), "
            "Impuls Festival (Graz), Mixtur e Barcelona Modern (Spagna), RED NOTE (USA), "
            "Nuova Consonanza (Roma), LuganoMusica e Accademia Nazionale di Santa Cecilia, e "
            "affidati a ensemble e orchestre di rilievo quali Klangforum Wien, Ensemble Dal "
            "Niente, Les Métaboles, Mdi Ensemble, Syntax Ensemble e Divertimento Ensemble, "
            "tra molti altri. Le sue opere sono state trasmesse da emittenti radiofoniche "
            "internazionali. La sua ricerca si nutre di un dialogo tra tradizione orale, "
            "tecniche improvvisative e prassi contemporanee, interrogando i confini tra "
            "gesto, parola e materia sonora e coinvolgendo il performer in una dimensione "
            "percettiva e fisica. Si è formata tra Svizzera, Italia e Austria e affianca "
            "alla composizione progetti di ricerca artistica in collaborazione con "
            "istituzioni accademiche, tra cui la Haute École de Musique di Ginevra."
        ),
    },
    {
        "nome": "Davide Broggini", "ruolo": "compositore",
        "bio": (
            "Davide Broggini (1996) è un compositore italiano la cui pratica si sviluppa tra "
            "scrittura strumentale, musica elettronica e multimedialità. La sua ricerca "
            "artistica indaga i processi percettivi e l'interpretazione di elementi "
            "comportamentali, con particolare attenzione alle trasformazioni delle forme e "
            "ai loro mutamenti nel tempo. Diplomato con il massimo dei voti e la lode in "
            "Percussioni (Conservatorio G. Cantelli, Novara - 2019) e in Musica Applicata "
            "(Civica Scuola di Musica C. Abbado, Milano - 2023), attualmente sta completando "
            "il Master of Arts in Composition and Theory presso il Conservatorio della "
            "Svizzera Italiana, studiando con i Maestri Nadir Vassena, Giovanni Verrando e "
            "Alberto Barberis. Inoltre nel 2025 si specializza presso l'Accademia Chigiana "
            "di Siena con Alvise Vidolin e Nicola Bernardini ricevendo il diploma di merito "
            "in Live Electronics, Sound and Music Computing.\n\n"
            "Parallelamente all'attività compositiva, svolge regolarmente il ruolo di "
            "esecutore elettronico, sound designer e assistente alla regia audio in "
            "produzioni contemporanee. E' membro del CLEE (Chigiana Live Electronics "
            "Ensemble); Ha collaborato con realtà come RSI (Radiotelevisione Svizzera), "
            "Piano City Milano, Palacinema Locarno, NFM Wrocław, TFF (Torino Film Festival)."
        ),
    },
    {
        "nome": "Giovanni Falascone", "ruolo": "compositore",
        "bio": (
            "Giovanni Falascone (1999). Compositore e improvvisatore italiano, la sua "
            "ricerca indaga l'interazione tra performance e composizione, ponendo il gesto "
            "strumentale come matrice formale e sonora. Attraverso dispositivi "
            "elettroacustici e digitali, talvolta amplia le possibilità timbriche e "
            "gestuali degli strumenti tradizionali, sviluppando una fusione tra suono "
            "acustico ed elettronico. Dal 2021 collabora con artisti visivi e danzatori in "
            "progetti multimediali che integrano suono, corpo e video dal vivo. "
            "Nell'ultimo anno, i suoi lavori, sono stati eseguiti da musicisti come NAMES, "
            "Divertimento Ensemble, Ensemble Suono Giallo, Alberto Anhaus e Falascone stesso "
            "in festival e istituzioni internazionali quali Limina Festival (Mozarteum "
            "Univeristät, Salisburgo, AT), Darmstädter Ferienkurse, Ars Electronica (Linz, "
            "AT), PianoCity Milano, Mantova Musica del XXI Secolo, Rondò e WeekIDEA "
            "(Milano). Come performer, collabora con ensemble, collettivi e associazioni "
            "provenienti da varie parti d'Italia e d'Europa che praticano e promuovono la "
            "musica d'improvvisazione, come il quartetto Ü, Collettivo Conserere, movement "
            "shaped like a heart e TAI No-Orchestra. Nel 2023 ha ricevuto il diploma di "
            "merito dall'Accademia Musicale Chigiana (Siena, IT) e nel 2024 un suo lavoro è "
            "stato citato tra i migliori dischi di musica improvvisata dell'anno da Ettore "
            "Grazia di percorsimusicali.net. Negli ultimi mesi si è esibito in Italia, "
            "Danimarca, Austria e Repubblica Ceca.\n\n"
            "Le sue partiture sono pubblicate da SZ Sugar – Sugarmusic Spa."
        ),
    },
    # --- Edizione 4 (7 maggio 2026) ---
    {
        "nome": "Antonia De Pasquale", "ruolo": "interprete",
        "bio": (
            "Antonia De Pasquale è una pianista italiana che unisce una solida formazione "
            "accademica a un'intensa carriera concertistica internazionale. Sotto la guida "
            "del M° Roberto Plano, ha conseguito con lode nel 2025 il Master of Advanced "
            "Studies presso il Conservatorio della Svizzera Italiana di Lugano, con una tesi "
            "dedicata all'identità musicale americana attraverso le opere di Beach, Rzewski "
            "e Liebermann. Attualmente prosegue gli studi presso la medesima istituzione per "
            "il Master of Arts in Music Performance e frequenta i corsi di Alto "
            "Perfezionamento dell'Accademia di Musica di Pinerolo con il M° Mariangela "
            "Vacatello.\n\n"
            "Diplomatasi con lode a soli 18 anni presso il Conservatorio “Nino Rota” di "
            "Monopoli, ha completato il biennio specialistico con lode e menzione speciale. "
            "Vincitrice di oltre 40 concorsi internazionali, si è distinta con il Secondo "
            "Premio al 2° International Contemporary Music Competition “Giulio "
            "Rospigliosi” 2026 e il Primo Premio al Lavaux Classic 2024 in Svizzera, dove ha "
            "ricevuto anche il Premio speciale per la migliore esecuzione del brano "
            "contemporaneo di Ezko Kikoutchi. Tra gli altri riconoscimenti figurano il Primo "
            "Premio all'Enotria Piano Competition — con conseguente debutto solistico con la "
            "Pazardzhik Symphony Orchestra — e il Premio “Harmonia in Music Chapel” al "
            "Concorso Esperia.\n\n"
            "La sua attività solistica l'ha vista protagonista in sedi prestigiose come la "
            "St. James's Church Piccadilly di Londra, la Mozarthaus di Vienna e la Reggia di "
            "Venaria Reale. Ha partecipato a festival di rilievo tra cui Piano City Milano, "
            "PianoPic in Francia, Orbetello Piano Festival e le rassegne dell'Accademia di "
            "Pinerolo dedicate a Rachmaninov e Ravel. Come solista con orchestra ha "
            "affrontato i grandi concerti di Beethoven, Mozart e Chopin, collaborando "
            "inoltre con l'Ensemble 900presente per opere di Ivan Fedele.\n\n"
            "Parallelamente, Antonia affianca all'attività artistica una profonda ricerca "
            "culturale: laureata in Lingue, è autrice del volume bilingue “Il suono del "
            "muro” (Schena Editore), dedicato al ruolo della musica nelle due Germanie."
        ),
    },
    {
        "nome": "Mariacostanza D'Agostino", "ruolo": "interprete",
        "bio": (
            "Mariacostanza D'Agostino comincia a studiare musica da quando aveva 5 anni con "
            "il pianoforte. È diplomata e laureata in Pianoforte e Musica da camera con il "
            "massimo dei voti e la lode al Conservatorio “G. Paisiello” di Taranto in "
            "Italia, sua città natìa. Si è perfezionata all'Accademia “Incontri col "
            "Maestro” di Imola. Dal 2021 studia direzione d'orchestra. Già nel 2022 debutta "
            "al Ravenna Festival con “Frammenti infernali”, spettacolo di teatro musicale "
            "ispirato a Dante Alighieri e a Pier Paolo Pasolini. Nello stesso anno viene "
            "ammessa al Master in Ensemble Conducting nella classe di Marc Kissoczy al "
            "Conservatorio della Svizzera italiana di Lugano, Svizzera. Nel 2024 conclude il "
            "master con il massimo dei voti e la lode. Ha partecipato in qualità di allieva "
            "effettiva a numerose masterclasses internazionali, come al Royal Northern "
            "College of Music di Manchester, UK e ha ricoperto la carica di Assistant "
            "Conductor durante il BerlinOpernFest 2023. Ha debuttato con le Orchestre "
            "sinfoniche di Karlovy Vary (2023) e Hradec Králové (2024). Tra gli altri, si è "
            "perfezionata con Marco Angius e Carlo Boccadoro. Nell'ambito della musica "
            "contemporanea ha diretto Divertimento Ensemble e AltreVoci Ensemble. Nel 2025 "
            "ha diretto “Histoire du Soldat” di Igor Stravinsky nella versione scenica "
            "italiana (curando anche la regia) con l'Orchestra Giovanile Fontane di Roma e "
            "Stefano Poeta nel ruolo del soldato. É stata vincitrice nel 2023 e nel 2025 "
            "della borsa di studio a sostegno delle giovani donne concessa dal Soroptimist "
            "Club di Lugano. Attualmente è direttrice dell'Ensemble dell'Internationale "
            "Ensemble Modern Akademie (IEMA) 2025/2026 di Frankfurt am Main, Germania, prima "
            "italiana ad aver raggiunto tale posizione. Nei suoi progetti cerca una visione "
            "musicale ampia, coniugando i diversi aspetti della sua formazione."
        ),
    },
    {
        "nome": "Francesca Seggioli", "ruolo": "regia_audio",
        "bio": (
            "Francesca Seggioli, diplomata con lode in Tecnico del Suono presso il "
            "Conservatorio “G. Verdi” di Milano, ha studiato con Massimo Marchi, Davide "
            "Gagliardi, Andrea Vigani e Fabio Venturi, specializzandosi successivamente con "
            "Alvise Vidolin e ottenendo il Diploma di Merito alla Chigiana Summer Academy in "
            "Live Electronics – Sound and Music Computing. La sua attività si concentra "
            "sulla realizzazione di live electronics, regia del suono e installazioni "
            "multimediali. Ha collaborato con istituzioni e festival come l'Accademia "
            "Nazionale di Santa Cecilia, il Chigiana International Festival, Milano Musica "
            "e la Filarmonica della Scala.\n\n"
            "È membro di Sistema Ensemble, Chigiana Live Electronics Ensemble e Yokai "
            "Ensemble. Ha inoltre partecipato a MLOrk (2021–2024) come laptop performer. "
            "Attualmente è PhD researcher presso i conservatori di Pescara, Ferrara, Trieste "
            "e Udine."
        ),
    },
    {
        "nome": "Emma Longo", "ruolo": "interprete",
        "bio": (
            "Emma Longo, classe 2001, si diploma con il massimo dei voti, la lode e la "
            "menzione al Conservatorio Vecchi-Tonelli di Modena. Ha conseguito con il "
            "massimo dei voti e la lode il diploma in Master of Arts in Music Performance al "
            "Conservatorio della Svizzera italiana nella classe di Andrea Oliva. Nel 2025 "
            "vince l'audizione e si esibisce come primo flauto nella Norrköping Symphony "
            "Orchestra (SON) sotto la direzione del maestro Karlheinz Steffens. Nel 2021 è "
            "stata primo flauto dell'Orchestra Giovanile Italiana (OGI) grazie alla quale ha "
            "collaborato con direttori come Alexander Lonquich, Andrea Lucchesini, Daniele "
            "Giorgi, Julian Rachlin. Dal 2022 è primo flauto dell'Orchestra del Teatro "
            "Olimpico di Vicenza (OTO). Svolge un'intensa attività orchestrale collaborando "
            "regolarmente con l'Orchestra Leonore, I solisti di Pavia, l'Orchestra Haydn di "
            "Bolzano, l'Orchestra Filarmonica di Modena. È vincitrice della Grafenegg "
            "Academy 2024, idonea presso l'Orchestra Regionale Toscana (ORT). Dal 2024 viene "
            "invitata come primo flauto nell'Orchestra Ceresio Estate (CH). Con le orchestre "
            "sopracitate, ha suonato in prestigiose sale da concerto nazionali ed "
            "internazionali: Emirates Palace (Abu Dhabi Festival), Elbphilharmonie di "
            "Amburgo, Konzerthaus di Berlino (Young Euro Festival), Wolkentrum Grafenegg, "
            "Teatro del Maggio Musicale Fiorentino, Teatro Olimpico di Vicenza, Auditorium "
            "della Radiotelevisione Svizzera italiana, Auditorium Louis De Geer di "
            "Norrköping, Teatro Alighieri di Ravenna, Teatro Pavarotti-Freni di Modena, "
            "Scalinata di San Bernardino all'Aquila, Teatro Sociale di Mantova, Teatro Verdi "
            "di Firenze. Ha ottenuto il terzo premio al Concorso Internazionale “Severino "
            "Gazzelloni” e il terzo premio nella borsa di studio “Betti”, ottenendo la "
            "possibilità di esibirsi come Falaut Artist al Campus Falaut e di incidere per "
            "il CD “Giovani Promesse”. Ha ottenuto il primo premio ai concorsi “Premio "
            "Crescendo” e “Riviera della Versilia”. Ha conseguito inoltre il primo premio "
            "assoluto al Concorso Alberghini di Bologna ed è inoltre vincitrice del concorso "
            "“Attraverso i Suoni”. Dal 2012 si esibisce da solista e in formazioni di "
            "musica da camera in Italia e in Svizzera in numerose stagioni concertistiche. "
            "Dal 2019 forma un duo stabile con l'arpista Valentina Vatteroni, con la quale "
            "ha inciso per l'etichetta discografica Da Vinci Classics l'album “Flute and "
            "Harp Fantasies in the 19th century”, recensito con 5 stelle dalla rivista "
            "“Amadeus”. Nel 2020 fonda il “Quintetto Fedro”, quintetto fiati in residence "
            "del Ticino Musica 2022 e 2023. È inoltre molto attiva nell'ambito della musica "
            "contemporanea: ha infatti curato un progetto di ricerca all'interno del "
            "Conservatorio della Svizzera Italiana che mira ad avvicinare il pubblico e la "
            "società alla musica degli anni 2000 e collabora come strumentista con la classe "
            "di composizione dei Maestri Nicola Bernardini e Alvise Visolin in Accademia "
            "Chigiana."
        ),
    },
    {
        "nome": "Chiara Ferraresi", "ruolo": "compositore",
        "bio": (
            "Chiara Ferraresi, nata nel 2005, si avvicina alla musica all'età di sei anni, "
            "cantando nel coro di voci bianche della FAES Academy di Milano. Parallelamente "
            "intraprende lo studio del pianoforte, che prosegue presso il Liceo Musicale "
            "“A. Manzoni” di Varese. Durante questi anni approfondisce lo studio del "
            "pianoforte, si dedica per alcuni anni al violoncello e scopre la passione per "
            "la composizione, che sceglie di coltivare come percorso principale. Ha "
            "mantenuto un costante legame con l'attività corale fin dall'infanzia e, dal "
            "2020, è direttrice del coro di voci bianche di San Vittore in Casbeno. "
            "Attualmente frequenta il Bachelor of Arts – Major in Theory and Composition "
            "presso il Conservatorio della Svizzera Italiana di Lugano."
        ),
    },
    {
        "nome": "Giulio Cattaneo", "ruolo": "compositore",
        "bio": (
            "Giulio Cattaneo, laureato con lode in Musica Elettronica al Conservatorio di "
            "Milano, dove ha studiato con Javier Torres Maldonado, Cesare Saldicco e "
            "Massimo Marchi, studia attualmente composizione al Conservatorio della "
            "Svizzera Italiana nella classe di Nadir Vassena. Dal 2024 frequenta il Corso di "
            "Specializzazione Superiore in Musica Elettronica all'Accademia Nazionale di "
            "Santa Cecilia con Michelangelo Lupone, e nel 2025 ha conseguito un Diploma di "
            "Merito all'Accademia Chigiana con Alvise Vidolin. Le sue opere sono state "
            "eseguite a livello internazionale in sedi e festival tra cui la Biennale di "
            "Venezia (concerto inaugurale del Padiglione Austriaco), la Sibelius Academy, il "
            "Parco della Musica, la Triennale di Milano, il Teatro LAC, AGON, il "
            "Conservatorio di Lione, la LMTA Academy di Vilnius e l'HSLU di Lucerna, "
            "l'Aerum contemporary music center di Daegu (Corea del Sud). È stato compositore "
            "in residenza per SZ Sugar (2025) e Tempo Reale (2024), e nel 2025 ha vinto il "
            "secondo premio al Concorso Internazionale di Composizione per Timpani di Lione."
        ),
    },
    {
        "nome": "Davide Rizza", "ruolo": "compositore",
        "bio": (
            "Davide Rizza (1996) è un compositore italiano con base a Dresda, in Germania. "
            "Il suo lavoro si concentra sull'esplorazione di come timbri complessi possano "
            "modellare il tempo e influenzarne la percezione.\n\n"
            "La sua musica è stata eseguita da ensemble e solisti come il Quartetto "
            "Maurice, l'Ensemble Fractales, l'Ensemble Lizard, Mariagrazia Bellocchio, Elio "
            "Marchesini e Alberto Cavallaro, ed è stata presentata in festival e rassegne "
            "tra cui Mixtur Festival (ES), Limina Festival (AT), Suena Festival (AT), Rondò "
            "– Divertimento Ensemble (IT) e Accademia Chigiana Festival (IT). Ha studiato "
            "composizione al Conservatorio di Torino con Giorgio Colombo Taccani e al "
            "Conservatorio di Mantova con Maurizio Azzan, partecipando inoltre a masterclass "
            "con Franck Bedrossian, Francesco Filidei, Mauro Lanza, Clara Iannotta, Dmitri "
            "Kourliandski, Pierluigi Billone e Alberto Posadas. Attualmente è iscritto al "
            "Meisterklasse-Komposition presso la Hochschule für Musik di Dresda con docenti "
            "Mark Andre e Stefan Prins, e al dottorato di ricerca in composizione presso il "
            "Conservatorio di Padova, dove indaga come le nuove tecnologie possano essere "
            "utilizzate per sostenere approcci compositivi fondati su una prospettiva "
            "fenomenologica."
        ),
    },
    {
        "nome": "Antonio Coiana", "ruolo": "compositore",
        "bio": (
            "Antonio Coiana nasce a Napoli nel 1996. Iniziati gli studi pianistici presso il "
            "Conservatorio D. Cimarosa di Avellino, consegue il diploma accademico di I "
            "livello in pianoforte, di II livello in maestro sostituto e Korrepetitor e II "
            "livello in composizione.\n\n"
            "Parallelamente al percorso accademico partecipa a seminari e masterclass con "
            "docenti del calibro di Salvatore Sciarrino, Ivan Fedele, Alessandro Solbiati, "
            "Giorgio Battistelli, Maria Grazia Bellocchio, Marco Momi e Milica Djordjevich.\n\n"
            "Le sue composizioni sono state eseguite da musicisti di chiara fama quali "
            "Francesco D'Orazio, Maria Grazia Bellocchio, Andrea Cavalazzi e Maria Eleonora "
            "Caminada. È attualmente iscritto al Master of Arts in Music Composition & "
            "Theory presso il Conservatorio della Svizzera italiana, dove studia con Nadir "
            "Vassena e Giovanni Verrando e contemporaneamente al corso di alto "
            "perfezionamento dell'Accademia di Santa Cecilia in Roma tenuto dal M° "
            "Alessandro Solbiati."
        ),
    },
    {
        "nome": "Matteo Cenerini", "ruolo": "compositore",
        "bio": (
            "Matteo Cenerini ha studiato Composizione alla Civica Scuola di Musica Claudio "
            "Abbado di Milano con Giovanni Verrando, Musicologia all'Università di Pavia, e "
            "Chitarra Jazz ai Conservatori di Livorno e Rovigo. Ha studiato con Nicola "
            "Evangelisti e Daniel D'Adamo, e ha partecipato a masterclass con numerosi "
            "compositori tra cui Simon Steen-Andersen, Pierre Jodlowski, Stefano Gervasoni, "
            "Marco Momi e James Dillon.\n\n"
            "Le sue composizioni sono state eseguite da ensemble e solisti quali il Moscow "
            "Contemporary Music Ensemble (MCME), Mdi Ensemble, FontanaMix, Syntax Ensemble, "
            "Icarus/Muzak Ensemble, Moto Contrario Ensemble, Sofia Gubaidulina Center "
            "Orchestra, Anna D'Errico, Marina Boselli e Giulia Zaniboni. I suoi lavori sono "
            "stati presentati in festival e istituzioni tra cui Mixtur (Barcellona), "
            "Filarmonica di Mosca, Accademia Chigiana e Divertimento Ensemble.\n\n"
            "Come chitarrista, è attivo nell'improvvisazione libera come solista e come "
            "membro dei collettivi Conserere (Milano) e Crisis Ensemble (Rovigo-Rotterdam)."
        ),
    },
]


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Esegue tutto ma non scrive (rollback a fine transazione).",
        )

    def handle(self, *args, **options):
        aggiunte = non_trovate = gia_presenti = 0

        with transaction.atomic():
            for item in DATA:
                try:
                    persona = Persona.objects.get(nome=item["nome"], ruolo=item["ruolo"])
                except Persona.DoesNotExist:
                    non_trovate += 1
                    self.stdout.write(self.style.ERROR(
                        f"NON TROVATA: {item['nome']} ({item['ruolo']})"
                    ))
                    continue

                if persona.bio:
                    gia_presenti += 1
                    self.stdout.write(f"  già presente, skip: {item['nome']}")
                    continue

                persona.bio = item["bio"]
                persona.save()
                aggiunte += 1
                self.stdout.write(self.style.SUCCESS(f"  bio aggiunta: {item['nome']}"))

            if options["dry_run"]:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(
            f"\nBio aggiunte: {aggiunte} | già presenti: {gia_presenti} | "
            f"non trovate: {non_trovate}"
        ))
        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("\n--dry-run: nessuna modifica salvata (rollback)."))
