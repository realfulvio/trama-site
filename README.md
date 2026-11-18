# Sito di Trama

Pagina di presentazione di Trama, servita con GitHub Pages da questo ramo `main`.

- `index.html`: versione italiana; `en/index.html`: versione inglese.
- `site/`: foglio di stile, logo e font Bricolage Grotesque (licenza OFL in `site/fonts/`).
- `media/homepage/`: catture reali del programma con dati sintetici.

HTML e CSS statici, nessun JavaScript, nessuna risorsa esterna.

## SEO

- Ogni pagina ha `title`, `description`, `canonical`, `hreflang` (it, en, x-default) assoluti, Open Graph, Twitter card e dati strutturati JSON-LD (`SoftwareApplication`, `WebSite`, `FAQPage` nelle home; `WebPage` e `BreadcrumbList` nelle pagine funzionalità).
- `sitemap.xml` elenca le quattro pagine con le alternative di lingua. Aggiornare `lastmod` quando cambiano i contenuti.
- Con una nuova versione aggiornare anche `softwareVersion`, `downloadUrl` e `releaseNotes` nel JSON-LD delle due home (il testo visibile si aggiorna da `site/releases.js`, il JSON-LD no).
- Le immagini di anteprima social sono in `media/og/` (1200 × 630).
- Un `robots.txt` in questa cartella non verrebbe letto: i crawler lo cercano solo alla radice del dominio `realfulvio.github.io`. Senza file tutto è consentito.
