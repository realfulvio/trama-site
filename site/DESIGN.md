# Sistema di design del sito di Trama

Documento di lavoro per chi modifica `index.html`, `en/index.html` e `site/style.css`. Stack: HTML e CSS statici, nessuna build, nessun JavaScript, nessuna risorsa esterna (il font dei titoli è nel repository).

## 1. Analisi

- **Tipologia:** pagina promozionale di un software desktop scientifico. Piattaforma: web, desktop e telefono.
- **Chi legge:** ricercatori, studenti e responsabili di laboratorio. Valutano uno strumento al posto di un altro, di solito alla scrivania, in una sessione di uno o tre minuti, e diffidano dei superlativi.
- **Ciclo principale:** capire il valore in dieci secondi → controllare che sia vero → scaricare. Ogni scelta grafica serve uno di questi tre passaggi.
- **Aspettative del genere:** densità alta, tono sobrio, prove al posto degli slogan, limiti dichiarati. Un sito che promette troppo qui perde credibilità.
- **Parti da game design:** non applicabili. Non ci sono progressione, punteggi o ricompense. Resta una sola idea affine, il feedback sulla verificabilità: ogni vantaggio ha un collegamento «Verifica» visibile.

## 2. Direzione visiva

Il marchio in grande. Testata blu profondo con i nastri verde acqua e corallo del logo, titolo in Bricolage Grotesque e una curva dose-risposta disegnata in SVG che si traccia al caricamento. La schermata reale del programma scavalca il bordo della testata, annotata con i punti A, B, C. Le sezioni chiare restano dense e sobrie; il confronto torna su fondo blu per dare ritmo alla pagina.

Elementi propri del soggetto: tacche d'asse per i numeri chiave, mini grafici disegnati per le sei famiglie di strumenti (barre con errori, sigmoide, cluster, Kaplan–Meier, foglio, layout), cornici inclinate verde acqua e corallo dietro le schermate.

## 3. Token

| Ruolo | Valore |
| --- | --- |
| Blu del marchio | `#08232f`, `#103642`, `#174654` |
| Verde acqua / menta / corallo / avorio | `#18b9ac` / `#a0e9d9` / `#f18a72` / `#f6f1e7` |
| Sezioni chiare: fondo, pannello, testo, secondario | `#f2f5f5`, `#ffffff`, `#0c2530`, `#47606a` |
| Sezioni nel tema scuro: fondo, pannello, testo, secondario | `#061a23`, `#0c2a36`, `#eef3f1`, `#a9c3c8` |
| Link su chiaro / su scuro | `#075f5b` / `#8ee5da` |

- **Tipografia:** titoli in Bricolage Grotesque variabile (file in `site/fonts/`, licenza OFL accanto), testo nello stack di sistema Segoe UI. Scala 14 / 16 / 18 / 22 px, titoli di sezione fluidi da 28 a 44 px, titolo principale da 40 a 76 px.
- **Spaziatura:** base 4 px (4, 8, 12, 16, 24, 32, 48, 72, 112).
- **Raggi:** pulsanti a pillola, 14 px sui pannelli, 10 px sulle finestre, 24–28 px sui riquadri grandi. Ombra solo sulle finestre del programma.
- **Contrasto:** avorio su blu 14:1, secondario su blu 8:1, blu su verde acqua (pulsanti) 6,4:1, testo secondario su fondo chiaro 6,3:1.

## 4. Schermate e flusso

Pagina unica, nell'ordine in cui il lettore decide:

1. **Testata:** titolo, due righe di spiegazione, pulsante di download, «Che cosa cambia», riga con versione beta, licenza, piattaforma e test. Sotto, la schermata annotata con la legenda A, B, C.
2. **Dove Trama lavora in modo diverso:** otto righe con la verifica a destra.
3. **Confronto per categoria** con il software commerciale tradizionale, senza nomi, con formule prudenti.
4. **Schermate reali** come pannelli A–D.
5. **Che cosa puoi fare** (sei famiglie di metodi).
6. **Quello che Trama non è (ancora):** limiti in chiaro.
7. **Provalo in tre passi** (qui l'ordine è reale) e requisiti.

Percorso critico: pulsante di download in testata, in barra, e a fine pagina; stessa etichetta ovunque.

## 5. Componenti e stati

| Componente | Stati |
| --- | --- |
| Pulsante (`.btn`, `.btn.line`) | normale, hover (menta, sale di 1 px), premuto, focus (anello 3 px), 48 px di altezza |
| Voce di navigazione | normale, hover (fondo), focus |
| Selettore di lingua (`.langs`) | IT e EN affiancati; lingua corrente piena (avorio), altra come collegamento con hover e focus; area di tocco 46 px |
| Vantaggio (`.gains li`) | icona SVG, titolo, testo, collegamento «Verifica» |
| Collegamento «Verifica» (`.check`) | normale, hover, focus, area 44 px |
| Tabella di confronto (`.cmp`) | colonna Trama con fondo e contorno verde acqua e spunta; sotto 960 px diventa a schede con l'etichetta della colonna |
| Scheda strumento (`.kit article`) | mini grafico SVG, titolo, testo |
| Schermata con cornice (`.frame`) | finestra con ombra su forma inclinata; alterna lato e colore |
| Finestra con schermata (`.window`) | solo contenitore; il collegamento apre l'immagine intera |
| Punto di annotazione (`.dot`) | decorativo (`aria-hidden`), la legenda sotto porta lo stesso testo |
| Riquadro limiti (`.limits`) | un solo stato, sempre visibile |

## 6. Accessibilità e prestazioni percepite

- Contrasti misurati (sopra), tema chiaro e scuro automatici.
- Bersagli ≥ 44 px per pulsanti, navigazione, collegamenti «Verifica» e collegamenti del piè di pagina.
- Focus visibile su ogni elemento, collegamento «Vai al contenuto», punti di riferimento (`header`, `nav`, `main`, `footer`), gerarchia dei titoli, testo alternativo descrittivo su ogni schermata.
- Il colore non è l'unico segnale: la colonna Trama ha intestazione e contorno; i limiti hanno titolo e testo.
- `prefers-reduced-motion` disattiva ogni animazione e lo scorrimento morbido.
- Nessun JavaScript né richiesta esterna: la pagina è completa al caricamento; le immagini sotto la prima schermata sono caricate in modo pigro con dimensioni dichiarate, quindi senza salti di layout.
- Nessuna emoji: icone e illustrazioni in SVG disegnato a mano nel codice.

## 7. Microinterazioni

- **La curva si disegna** nella testata: tratto in 1,6 s, poi i punti uno alla volta (110 ms di distanza) e la banda di confidenza. Una volta sola, al caricamento. Scopo: mostrare subito che cosa fa il programma, adattare una curva ai dati.
- **Pulsanti:** al passaggio schiariscono e salgono di 1 px in 150 ms.

Con riduzione del movimento la curva è già completa e i pulsanti non si muovono. Nessun'altra animazione, nessun effetto allo scorrimento.

## 8. Lista di coerenza

- [ ] Nessun nome di prodotto, marchio o estensione di file di altri programmi.
- [ ] Ogni affermazione su Trama ha un riferimento nel repository; ogni affermazione sugli altri è per categoria e con «di solito» o «spesso».
- [ ] Versione, conteggio dei test e rapporto di verifica aggiornati insieme (testata, strumenti, registro, piè di pagina) in italiano e inglese.
- [ ] Solo i colori del marchio: blu, verde acqua, menta, corallo, avorio. Il corallo segna beta, limiti e annotazioni.
- [ ] Ombra solo sulle finestre del programma; raggi dai token.
- [ ] Pulsanti e collegamenti interattivi ≥ 44 px; nessuno scorrimento orizzontale a 390 px.
- [ ] Le immagini sono catture reali con dati sintetici e provenienza in `media/homepage/PROVENANCE.md`.
