# Sito promozionale di Trama

Sito statico (HTML e CSS, nessuna build, nessun JavaScript, nessuna richiesta esterna) pubblicato con GitHub Pages dalla cartella `/docs` del ramo `main`.

- `index.html` — pagina in italiano. `en/index.html` — versione inglese.
- `site/style.css` — stile "Scientifico compatto" (stessi colori e densità di `analisi/ui_theme.py`); `site/DESIGN.md` — sistema di design, componenti, accessibilità e lista di coerenza.
- Le immagini sono quelle di `media/homepage/`; il progetto di esempio è `examples/Laboratorio.alab`.
- `.nojekyll` in `/docs` evita che Pages elabori i file Markdown della documentazione.

Anteprima locale: `python -m http.server -d docs 8000` e apri http://localhost:8000/.

Quando cambia la versione, aggiornare nelle due pagine: numero di versione (hero, "Che cosa puoi fare"), conteggio dei test e link al rapporto di verifica. Le affermazioni sul software commerciale restano per categoria e senza nomi di prodotti o marchi.

Il font dei titoli è Bricolage Grotesque (SIL Open Font License 1.1), servito da `site/fonts/` con la licenza accanto.
