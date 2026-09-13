"""
Importa in locale il concerto "202526-edizione-2" presente solo sulla VPS
(merge inverso, 2026-09-13). Idempotente: se lo slug esiste già, non fa nulla.
Uso: docker compose exec -T web python manage.py shell < scripts/import_concerto_mancante_202526_2.py
"""
from concerti.models import Brano, Concerto, Partecipazione, Sede, Persona

SLUG = "202526-edizione-2"

if Concerto.objects.filter(slug=SLUG).exists():
    print(f"Concerto {SLUG} già presente, nessuna azione.")
else:
    sede = Sede.objects.get(nome="Conservatorio della Svizzera Italiana")

    concerto = Concerto.objects.create(
        numero_edizione=2,
        stagione="2025/26",
        slug=SLUG,
        data="2026-02-05",
        ora="19:00:00",
        sede=sede,
        colore_sfondo_1="#f6dfa0",
        colore_sfondo_2="#f0c96a",
        colore_sfondo_3="#eecf8f",
        colore_accento="#ffffff",
        nota_programma=(
            "Edoardo Casali - Fagotto\n\n"
            "Pier Luigi Billone (1960)\n"
            "Legno. Edre.: I. ME.\n"
            "Tratto da \"Legno Edre I - V\" (2003-2004)\n"
            "per Fagotto solo è un lavoro di ampio respiro (78') dove interesse tecnico, "
            "pensiero compositivo, concezioni astratte e una sorgiva emozione verso il "
            "suono si incontrano nel punto dove diventa possibile una particolare "
            "“libertà”: quella che nasce quando una totale familiarità con lo "
            "strumento viene orientata dalla attenzione e dalla capacità di ascolto.\n"
            "Il suono tradizionale qui non è più il centro. Il fagotto si apre "
            "completamente offrendo tutta l'inesplorata disomogeneità delle proprie "
            "caratteristiche fisiche e acustiche. All'interprete è affidato il difficile "
            "compito di inoltrarsi in questo spazio aperto.\n\n"
            "Filippo Lepre (1995)\n"
            "Binario di Azione Binaria (2022-2023)\n"
            "per fagotto amplificato è il secondo lavoro del compositore per strumento "
            "amplificato. Questa composizione è stata commissionata da DYCE 2022-2023 – "
            "progetto in collaborazione con Divertimento Ensemble. Il fagotto viene "
            "visualizzato in una geografia strumentale in cui il ragionamento sulla "
            "meccanica di questo strumento ha portato a tracciare binari di gesti ed "
            "azioni paralleli, dipendenti ed indipendenti.\n\n"
            "Manuel Teles - Saxofono alto, saxofono soprano\n\n"
            "Francesco Fausto Magaletti (2000)\n"
            "Attraverso gli Attimi (2026) *\n"
            "nasce dal desiderio di raccontare quei momenti interiori in cui il tempo "
            "sembra fermarsi. È la sensazione di trovarsi in bilico, tra ciò che è stato "
            "e ciò che sta per accadere, quando un cambiamento è vicino ma non ancora "
            "visibile. La musica attraversa stati di tensione, fragilità e silenzio, "
            "lasciando emergere lentamente una nuova forma di equilibrio.\n\n"
            "Floriana Provenzano (1998)\n"
            "Calce, luce, squarci (2026) *\n"
            "in inglese \"Lime, light, rifts\" esplora una materia sonora acida, ruvida e "
            "luminosa. In questo lavoro, la ricerca timbrica consiste nell'elaborazione e "
            "nella costruzione di nuovi materiali attraverso proprietà sonore quali "
            "instabilità, saturazione e granulazione, richiamando le sonorità acide della "
            "musica tradizionale del Sud Italia e le \"pietre sonore\" di Pinuccio Sciola.\n\n"
            "* : prima esecuzione assoluta\n\n"
            "CHI HA SCRITTO PER RAMIFICAZIONI\n\n"
            "Floriana Provenzano (1998) è una compositrice italiana. La sua musica nasce "
            "spesso da immagini sonore e sensazioni visive e fisiche, sviluppandosi in "
            "esplorazioni di texture, luminosità e timbro. È attualmente iscritta al "
            "Master in composizione presso il Conservatorio di Mantova, sotto la guida di "
            "Zeno Baldi e Maurizio Azzan.\n\n"
            "Francesco Fausto Magaletti (Bari, 2000) è chitarrista e compositore. Si "
            "laurea con lode in chitarra nel 2023 e avvia un'intensa attività "
            "concertistica nell'ambito della musica da camera. Studia composizione al "
            "Conservatorio di Milano con Gabriele Manca. Le sue opere sono pubblicate da "
            "Stradivarius Edizioni e SZ Sugar."
        ),
        link_prenotazione="",
        pubblicato=True,
    )

    Brano.objects.bulk_create([
        Brano(concerto=concerto, ordine=0, compositore="Pier Luigi Billone",
              titolo="Legno. Edre.: I. ME.", prima_esecuzione_tipo=""),
        Brano(concerto=concerto, ordine=1, compositore="Filippo Lepre",
              titolo="Binario di Azione Binaria", prima_esecuzione_tipo=""),
        Brano(concerto=concerto, ordine=2, compositore="Francesco Fausto Magaletti",
              titolo="Attraverso gli Attimi", prima_esecuzione_tipo="assoluta"),
        Brano(concerto=concerto, ordine=3, compositore="Floriana Provenzano",
              titolo="Calce, luce, squarci", prima_esecuzione_tipo="assoluta"),
    ])

    Partecipazione.objects.bulk_create([
        Partecipazione(concerto=concerto, ordine=0, strumento_in_concerto="",
                        persona=Persona.objects.get(nome="Edoardo Casali")),
        Partecipazione(concerto=concerto, ordine=1, strumento_in_concerto="",
                        persona=Persona.objects.get(nome="Manuel Teles")),
    ])

    print(f"Creato concerto {SLUG} con 4 brani e 2 partecipazioni.")
