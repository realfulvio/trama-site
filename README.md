# Sito di Trama

Pagina di presentazione di Trama, servita con GitHub Pages da questo ramo `main` sul dominio https://tramastat.org (file `CNAME`; DNS su Cloudflare, record solo DNS senza proxy).

- `index.html`: versione italiana; `en/index.html`: versione inglese.
- `site/`: foglio di stile, logo e font Bricolage Grotesque (licenza OFL in `site/fonts/`).
- `media/homepage/`: catture reali del programma con dati sintetici.

HTML e CSS statici, nessun JavaScript, nessuna risorsa esterna.

## SEO

- Ogni pagina ha `title`, `description`, `canonical`, `hreflang` (it, en, x-default) assoluti, Open Graph, Twitter card e dati strutturati JSON-LD (`SoftwareApplication`, `WebSite`, `FAQPage` nelle home; `WebPage` e `BreadcrumbList` nelle pagine funzionalità).
- `sitemap.xml` elenca le quattro pagine con le alternative di lingua. Aggiornare `lastmod` quando cambiano i contenuti.
- Con una nuova versione aggiornare anche `softwareVersion`, `downloadUrl` e `releaseNotes` nel JSON-LD delle due home (il testo visibile si aggiorna da `site/releases.js`, il JSON-LD no).
- Le immagini di anteprima social sono in `media/og/` (1200 × 630).
- `robots.txt` alla radice consente tutto e indica la sitemap. Con il dominio personalizzato i crawler lo leggono su https://tramastat.org/robots.txt.

## Centro guide (guida/ e en/guide/)

Guida a capitoli in italiano e inglese: indice con ricerca, quattro sezioni (Statistica, Curve e calibrazione, Dati e formule, Grafici e report) e i capitoli pronti. Le pagine HTML sono **generate**: non modificarle a mano.

- `guide-src/indice.csv`: tutti i capitoli, con sezione, slug italiano e inglese, tranche (1 = pubblicato) ed esempio previsto.
- `guide-src/capitoli/{it,en}/<slug>.html`: testo dei capitoli pronti, con una testata JSON (titolo, domanda, scheda di prova, file da scaricare, immagine).
- `guide-src/esempi.py`: rifà dati sintetici, progetti `.alab`, figure, risultati `.json` e schermate dell'app in `guida/allegati/` ed `en/guide/files/`, e controlla che i numeri citati siano quelli che Trama calcola. Si lancia dal clone di Trama alla versione indicata:
  `cd <clone Trama> && PYTHONPATH=. python <sito>/guide-src/esempi.py [slug…] [--senza-app]`
- `guide-src/build.py` (solo libreria standard): `python3 guide-src/build.py` scrive indice, sezioni, capitoli e le voci della guida in `sitemap.xml`. Versione, tag, commit e data di verifica sono costanti in cima al file.
- Stile in `site/guide.css`, comportamento in `site/guide.js` (ricerca senza accenti, indice del capitolo, copia della frase). Senza JavaScript la guida resta completa.

Per pubblicare un capitolo nuovo: esempio in `esempi.py`, testo in `capitoli/it` e `capitoli/en`, tranche 1 in `indice.csv`, poi `build.py`.
