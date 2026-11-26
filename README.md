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

Usa un clone di Trama fermo al tag appena pubblicato su GitHub. Prima di eseguire il comando,
aggiorna le voci della mappa in `funzionalita/index.html` e `en/features/index.html` con i cambiamenti
della release. Lo script legge le date di pubblicazione da GitHub e mostra nell’indice e nella pagina
Novità le ultime dieci release in entrambe le lingue, con un link allo storico completo. Per i testi usa
`docs/release-*.md` del clone e, se manca un file, le note pubblicate su GitHub.
Lo script aggiorna i download statici, la versione delle home e del catalogo, i dati strutturati,
i contatori della mappa e le date nella sitemap. Salta, segnalandole, le voci che nominano prodotti
di terzi.

Verifica le sei pagine sul dominio pubblico e prova il link diretto al portabile. Se i cambiamenti
riguardano un percorso illustrato, usa schermate reali e aggiorna la relativa provenienza.

## SEO

- Ogni pagina ha `title`, `description`, `canonical`, `hreflang` (it, en, x-default) assoluti, Open Graph, Twitter card e dati strutturati JSON-LD (`SoftwareApplication`, `WebSite`, `FAQPage` nelle home; `WebPage` e `BreadcrumbList` nelle pagine funzionalità).
- `sitemap.xml` elenca le sei pagine con le alternative di lingua. Aggiornare `lastmod` quando cambiano i contenuti.
- Le immagini di anteprima social sono in `media/og/` (1200 × 630).
- `robots.txt` alla radice consente tutto e indica la sitemap. Con il dominio personalizzato i crawler lo leggono su https://tramastat.org/robots.txt.
