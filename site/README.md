# Sito promozionale di Trama

Sito statico (HTML e CSS, nessuna build, nessun JavaScript, nessuna richiesta esterna) pubblicato con GitHub Pages dalla cartella `/docs` del ramo `main`.

- `index.html` — pagina in italiano. `en/index.html` — versione inglese.
- `site/style.css` — stile "Scientifico compatto" (stessi colori e densità di `analisi/ui_theme.py`); `site/DESIGN.md` — sistema di design, componenti, accessibilità e lista di coerenza.
- Le immagini sono quelle di `media/workflows-112/`; il progetto di esempio è `examples/Laboratorio.alab`.
- `.nojekyll` in `/docs` evita che Pages elabori i file Markdown della documentazione.

Anteprima locale: `python -m http.server -d docs 8000` e apri http://localhost:8000/.

Quando cambia la versione, aggiornare nelle due pagine: numero di versione (hero, "Che cosa puoi fare"), conteggio dei test e link al rapporto di verifica. Le affermazioni sul software commerciale restano per categoria e senza nomi di prodotti o marchi.

Il font dei titoli è Bricolage Grotesque (SIL Open Font License 1.1), servito da `site/fonts/` con la licenza accanto.

## Pagina «Funzionalità» (funzionalita/ e en/features/)

Mappa interattiva dei formati e delle funzionalità, con i lavori in programma. HTML statico con gli elenchi completi (leggibili anche senza JavaScript); `site/features.js` costruisce la griglia di quadrati e lo schema dei formati dagli elenchi. Stile in `site/features.css`, che usa i token di `style.css`. Unica pagina con JavaScript oltre a `releases.js`. I contenuti derivano dal codice di Trama (`analisi/workbench.py`, `docs/compatibility.md`, `docs/coverage.md`): aggiornarli a ogni versione, in italiano e inglese, senza nomi né estensioni di prodotti di terzi.
