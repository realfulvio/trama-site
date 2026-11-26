# Sito di Trama

Pagina di presentazione di Trama, servita con GitHub Pages da questo ramo `main` sul dominio https://tramastat.org (file `CNAME`; DNS su Cloudflare, record solo DNS senza proxy).

- `index.html`: versione italiana; `en/index.html`: versione inglese.
- `site/`: foglio di stile, logo e font Bricolage Grotesque (licenza OFL in `site/fonts/`).
- `funzionalita/` e `en/features/`: mappa delle funzionalità.
- `novita/` e `en/whats-new/`: novità versione per versione, generate da `tools/novita.py` (vedi sotto).
- `media/`: catture reali del programma con dati sintetici.

HTML e CSS statici, poco JavaScript facoltativo (senza script le pagine restano complete), nessuna risorsa esterna.

Tutte le pagine hanno lo stesso menu: Home, Funzionalità, Novità.

## Novità a ogni versione

```
python tools/novita.py ../Trama
```

Legge `docs/release-*.md` del clone di Trama dalla 0.104 in poi e riscrive le due pagine Novità. Salta, segnalandole, le voci che nominano formati di prodotti di terzi.

## SEO

- Ogni pagina ha `title`, `description`, `canonical`, `hreflang` (it, en, x-default) assoluti, Open Graph, Twitter card e dati strutturati JSON-LD (`SoftwareApplication`, `WebSite`, `FAQPage` nelle home; `WebPage` e `BreadcrumbList` nelle pagine funzionalità).
- `sitemap.xml` elenca le sei pagine con le alternative di lingua. Aggiornare `lastmod` quando cambiano i contenuti.
- Con una nuova versione aggiornare anche `softwareVersion`, `downloadUrl` e `releaseNotes` nel JSON-LD delle due home (il testo visibile si aggiorna da `site/releases.js`, il JSON-LD no).
- Le immagini di anteprima social sono in `media/og/` (1200 × 630).
- `robots.txt` alla radice consente tutto e indica la sitemap. Con il dominio personalizzato i crawler lo leggono su https://tramastat.org/robots.txt.
