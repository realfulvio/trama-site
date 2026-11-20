"""Genera le pagine del Centro guide (/guida/ e /en/guide/) e aggiorna sitemap.xml.

Uso, dalla radice del sito:   python guide-src/build.py
Solo libreria standard. Legge:
  guide-src/indice.csv            l'indice dei capitoli, in italiano e in inglese, con la tranche di pubblicazione
  guide-src/capitoli/<lingua>/    il testo dei capitoli pronti (frammenti HTML con una testata JSON)
  guide-src/allegati.json         i file creati da esempi.py (percorsi, byte, misure delle immagini)

Nei frammenti: {{V}} versione, {{TAG}}, {{COMMIT}}, {{href:chiave}} indirizzo relativo di un allegato,
{{kb:chiave}} la sua dimensione, {{wh:chiave}} width e height di un'immagine, {{fonti}} numero di fonti.
Le sezioni con id e un h2 formano l'indice del capitolo; data-toc sull'h2 accorcia la voce.
"""
import csv
import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "guide-src"
SITE = "https://tramastat.org/"
VERSION = "0.95.0 beta"
TAG = "v0.95.0"
COMMIT = "4c07db6"
VERIFIED = "2026-11-20"
RELEASE_ZIP = f"https://github.com/realfulvio/Trama/releases/download/{TAG}/Trama-0.95.0-Windows-x64.zip"
RELEASE_PAGE = f"https://github.com/realfulvio/Trama/releases/tag/{TAG}"

SECTIONS = {
    "statistica": {"en": "statistics",
                   "it": ("Statistica", "Scegliere e interpretare il metodo, dai confronti fra gruppi alle analisi "
                                        "multivariabili e di sopravvivenza."),
                   "en_t": ("Statistics", "Choosing and interpreting the method, from group comparisons to "
                                          "multivariable and survival analyses.")},
    "curve": {"en": "curves",
              "it": ("Curve e calibrazione", "Dalla scelta dell’equazione alla diagnosi del fit e alla previsione "
                                             "con incertezza."),
              "en_t": ("Curves and calibration", "From choosing the equation to checking the fit and predicting "
                                                 "with uncertainty.")},
    "dati": {"en": "data",
             "it": ("Dati e formule", "Fogli, tipi di colonne, valori mancanti, trasformazioni e progetti che si "
                                      "riaprono uguali."),
             "en_t": ("Data and formulas", "Sheets, column types, missing values, transformations and projects "
                                           "that reopen unchanged.")},
    "grafici": {"en": "graphs",
                "it": ("Grafici e report", "Quali segni leggere, come comporre i pannelli, come esportare figure "
                                           "e tabelle."),
                "en_t": ("Graphs and reports", "Which marks to read, how to compose panels, how to export figures "
                                               "and tables.")},
}

# Parole in più per la ricerca: quello che un lettore di laboratorio scriverebbe davvero.
KEYWORDS = {
    "it": {"k-means": "cluster clustering raggruppamento gruppi partizione silhouette wss gomito elbow numero di gruppi",
           "anova": "varianza trattamenti controllo confronti multipli post hoc tukey welch più condizioni",
           "curva-standard": "calibrazione concentrazione ignoti interpolazione elisa standard retta di taratura",
           "colonne-calcolate": "formula colonna calcolata normalizzare rapporto foglio",
           "esportazione": "svg pdf vettoriale figura pubblicazione export rivista layout",
           "gerarchico": "dendrogramma cluster gerarchico", "sopravvivenza": "kaplan meier censura eventi",
           "cox": "hazard ratio rischio proporzionale", "correlazione": "pearson spearman associazione",
           "ranghi": "mann whitney wilcoxon kruskal non parametrico", "potenza": "numerosità campionaria sample size",
           "pca": "componenti principali loadings punteggi", "incertezza": "intervallo di predizione confidenza",
           "confronti": "test t appaiato welch", "mancanti": "esclusione celle vuote na"},
    "en": {"k-means": "cluster clustering groups partition silhouette wss elbow number of clusters",
           "anova": "variance treatments control multiple comparisons post hoc tukey welch several conditions",
           "curva-standard": "calibration concentration unknowns interpolation elisa standards",
           "colonne-calcolate": "formula calculated column normalise normalize ratio sheet",
           "esportazione": "svg pdf vector figure publication export journal layout",
           "gerarchico": "dendrogram hierarchical cluster", "sopravvivenza": "kaplan meier censoring events",
           "cox": "hazard ratio proportional hazards", "correlazione": "pearson spearman association",
           "ranghi": "mann whitney wilcoxon kruskal nonparametric", "potenza": "sample size",
           "pca": "principal components loadings scores", "incertezza": "prediction interval confidence",
           "confronti": "t test paired welch", "mancanti": "exclusion empty cells na"},
}

T = {
    "it": {
        "lang": "it", "locale": "it_IT", "other": "en", "skip": "Vai al contenuto", "home": "Home",
        "features": "Funzionalità", "guide": "Guida", "langs": "Lingua", "download": "Scarica",
        "site_nav": "Sito", "search": "Cerca nella guida", "search_go": "Cerca",
        "placeholder": "es. numero di gruppi, curva standard",
        "status": {1: ("ready", "Pronto · verificato 0.95.0"), 2: ("draft", "Prossima tranche"),
                   3: ("plan", "In programma · tranche 3"), 4: ("plan", "In programma · tranche 4")},
        "example": "Esempio", "chapters": "capitoli", "ready_n": "pronti", "all_guides": "Tutte le guide",
        "guide_index": "Indice della guida", "other_guides": "Altre guide", "in_chapter": "In questo capitolo",
        "proof": "Scheda di prova e file", "trama": "Trama", "commit": "Commit", "data": "Dati", "seed": "Seme",
        "sources": "fonti primarie", "back": "Indietro", "next": "Avanti", "index": "Indice",
        "to_index": "Torna all’indice della guida", "breadcrumb": "Percorso", "verified": "Verificato",
        "reading": "Lettura", "minutes": "minuti", "files": "File da scaricare",
        "footer": "Guida di Trama. Esempi con dati sintetici, numeri verificati nella versione indicata in ogni capitolo.",
        "links": "Collegamenti", "news": "Novità 0.95", "license": "Licenza MIT",
        "legal": "Trama è un progetto indipendente in fase beta. Non viene dichiarata una validazione clinica o una certificazione regolatoria.",
        "index_title": "Guida di Trama: statistica, curve, dati e grafici",
        "index_desc": "Capitoli pratici per chi lavora con misure sperimentali: scegliere l’analisi, eseguirla in Trama, leggere i numeri e scrivere i metodi, con dati sintetici e progetti che si riaprono.",
        "eyebrow": "Guida di Trama", "h1": "Dalla domanda al risultato che puoi riportare.",
        "lead": "Quattro guide per chi lavora con misure sperimentali: scegli l’analisi, eseguila in Trama, leggi i numeri e scrivi i metodi. Ogni esempio ha dati sintetici e un progetto che si riapre.",
        "try": "Prova:", "hints": ["numero di gruppi", "curva standard", "più condizioni", "svg"],
        "count": "{n} capitoli in quattro guide · {r} pronti · {d} nella prossima tranche",
        "empty": "Nessun capitolo per «<span data-echo></span>».</b> Prova con un metodo (ANOVA, Cox), con quello che vuoi fare (confrontare gruppi, esportare una figura) o con una parola più corta.",
        "show_all": "Mostra tutto l’indice", "anatomy": "Com’è fatto un capitolo",
        "anat": [("Domanda", "dal tuo lavoro"), ("Quando", "e quali assunzioni contano"),
                 ("Dati", "CSV e progetto .alab"), ("In Trama", "comandi veri"),
                 ("Risultato", "numeri e un caso limite"), ("Riporta", "frase, versione, fonti")],
        "ready_list": "Capitoli pronti", "tranches": "Come arrivano gli altri capitoli",
        "tranche_text": "I capitoli escono a tranche. Ognuno è pubblicato solo quando i numeri sono stati rifatti nella versione indicata, con dati sintetici, un progetto .alab che si riapre, schermate reali e fonti primarie.",
        "tranche_names": {1: "Tranche 1 · pubblicata", 2: "Tranche 2 · la prossima", 3: "Tranche 3", 4: "Tranche 4"},
        "proof_col": "Prova da allegare",
        "section_lead": "Capitoli della guida {name}.", "section_title": "{name} · Guida di Trama",
        "section_count": "{n} capitoli · {r} pronti", "edge": "Caso limite",
        "copy": "Copia la frase", "methods_example": "Esempio di frase per la sezione Metodi.",
    },
    "en": {
        "lang": "en", "locale": "en_US", "other": "it", "skip": "Skip to content", "home": "Home",
        "features": "Features", "guide": "Guide", "langs": "Language", "download": "Download",
        "site_nav": "Site", "search": "Search the guide", "search_go": "Search",
        "placeholder": "e.g. number of clusters, standard curve",
        "status": {1: ("ready", "Ready · checked on 0.95.0"), 2: ("draft", "Next batch"),
                   3: ("plan", "Planned · batch 3"), 4: ("plan", "Planned · batch 4")},
        "example": "Example", "chapters": "chapters", "ready_n": "ready", "all_guides": "All guides",
        "guide_index": "Guide contents", "other_guides": "Other guides", "in_chapter": "In this chapter",
        "proof": "Proof sheet and files", "trama": "Trama", "commit": "Commit", "data": "Data", "seed": "Seed",
        "sources": "primary sources", "back": "Previous", "next": "Next", "index": "Contents",
        "to_index": "Back to the guide contents", "breadcrumb": "Breadcrumb", "verified": "Checked on",
        "reading": "Reading", "minutes": "minutes", "files": "Files to download",
        "footer": "Trama guide. Examples use synthetic data; every chapter states the version its numbers were checked on.",
        "links": "Links", "news": "What’s new in 0.95", "license": "MIT licence",
        "legal": "Trama is an independent project in beta. No clinical validation or regulatory certification is claimed.",
        "index_title": "Trama guide: statistics, curves, data and graphs",
        "index_desc": "Practical chapters for people who work with experimental measurements: choose the analysis, run it in Trama, read the numbers and write the methods, with synthetic data and projects that reopen.",
        "eyebrow": "Trama guide", "h1": "From the question to a result you can report.",
        "lead": "Four guides for people who work with experimental measurements: choose the analysis, run it in Trama, read the numbers and write the methods. Every example has synthetic data and a project that reopens.",
        "try": "Try:", "hints": ["number of clusters", "standard curve", "several conditions", "svg"],
        "count": "{n} chapters in four guides · {r} ready · {d} in the next batch",
        "empty": "No chapter for “<span data-echo></span>”.</b> Try a method (ANOVA, Cox), what you want to do (compare groups, export a figure) or a shorter word.",
        "show_all": "Show the whole contents", "anatomy": "How a chapter is built",
        "anat": [("Question", "from your work"), ("When", "and which assumptions matter"),
                 ("Data", "CSV and .alab project"), ("In Trama", "the real commands"),
                 ("Result", "numbers and an edge case"), ("Report", "sentence, version, sources")],
        "ready_list": "Ready chapters", "tranches": "How the other chapters arrive",
        "tranche_text": "Chapters are published in batches. Each one goes out only after its numbers have been redone in the stated version, with synthetic data, an .alab project that reopens, real screenshots and primary sources.",
        "tranche_names": {1: "Batch 1 · published", 2: "Batch 2 · next", 3: "Batch 3", 4: "Batch 4"},
        "proof_col": "Proof to attach",
        "section_lead": "Chapters of the {name} guide.", "section_title": "{name} · Trama guide",
        "section_count": "{n} chapters · {r} ready", "edge": "Edge case",
        "copy": "Copy the sentence", "methods_example": "Example sentence for the Methods section.",
    },
}

ICONS = {
    "statistica": '<path d="M5 20v-8M12 20V6M19 20v-5"/><path d="M3 12h4M10 6h4M17 15h4"/><path d="M3 20h18"/>',
    "curve": '<path d="M3 19c5 0 6-12 10-12s4 6 8 6"/><circle cx="6" cy="17" r="1"/><circle cx="11" cy="9" r="1"/><circle cx="17" cy="11" r="1"/>',
    "dati": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M3 14h18M9 4v16M15 4v16"/>',
    "grafici": '<rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="18" height="8" rx="1.5"/>',
}
DL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
      'stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 11l5 5 5-5M5 20h14"/></svg>')
SEARCH = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
          'aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>')
E = html.escape


def icon(section):
    return (f'<svg class="gico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[section]}</svg>')


def fold(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.casefold()) if not unicodedata.combining(c))


def kb(n, lang):
    text = f"{n / 1024:.1f} kB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"
    return text.replace(".", ",") if lang == "it" else text


# ------------------------------------------------------------------------------------------------ indirizzi
def section_slug(section, lang):
    return section if lang == "it" else SECTIONS[section]["en"]


def section_name(section, lang):
    return SECTIONS[section]["it" if lang == "it" else "en_t"]


def url_index(lang):
    return "guida/" if lang == "it" else "en/guide/"


def url_section(section, lang):
    return f"{url_index(lang)}{section_slug(section, lang)}/"


def url_chapter(row, lang):
    return f"{url_section(row['sezione'], lang)}{row['slug'] if lang == 'it' else row['slug_en']}/"


def rel(page, target):
    """Indirizzo relativo da una pagina (cartella con index.html) a un percorso dalla radice del sito."""
    depth = page.count("/")
    return "../" * depth + target


# ------------------------------------------------------------------------------------------------ dati
def load_rows():
    rows = list(csv.DictReader((SRC / "indice.csv").open(encoding="utf-8")))
    for row in rows:
        row["tranche"] = int(row["tranche"])
    return rows


def load_chapter(row, lang, manifest):
    """Testata JSON e corpo di un capitolo pronto, con i segnaposto risolti."""
    path = SRC / "capitoli" / lang / f"{row['slug']}.html"
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\s*<!--\s*(\{.*?\})\s*-->\s*", text, re.S)
    meta, body = json.loads(match.group(1)), text[match.end():]
    files = manifest[row["slug"]][lang]
    page = url_chapter(row, lang)

    def sub(m):
        kind, _, key = m.group(1).partition(":")
        if kind == "V":
            return VERSION
        if kind == "TAG":
            return TAG
        if kind == "COMMIT":
            return COMMIT
        if kind == "fonti":
            return str(len(re.findall(r"<li\b", body.split('id="fonti"', 1)[-1].split("</ol>", 1)[0])))
        info = files[key]
        if kind == "href":
            return rel(page, info["path"])
        if kind == "kb":
            return kb(info["bytes"], lang)
        if kind == "wh":
            return f'width="{info["width"]}" height="{info["height"]}"'
        raise KeyError(m.group(0))

    body = re.sub(r"\{\{(V|TAG|COMMIT|fonti|(?:href|kb|wh):[\w-]+)\}\}", sub, body)
    meta = json.loads(re.sub(r"\{\{(V|TAG|COMMIT|fonti|(?:href|kb|wh):[\w-]+)\}\}", sub, json.dumps(meta, ensure_ascii=False)))
    toc = [(m.group(1), m.group(3) or re.sub(r"<[^>]+>", "", m.group(4)))
           for m in re.finditer(r'<section[^>]*\bid="([\w-]+)"[^>]*>\s*<h2([^>]*?data-toc="([^"]+)")?[^>]*>(.*?)</h2>',
                                body, re.S)]
    meta["toc"] = toc
    meta["files"] = files
    return meta, body


# ------------------------------------------------------------------------------------------------ pagina
def head(page, lang, title, desc, *, alternate, image, crumbs, kind="WebPage", wide=False, extra_ld=None):
    t = T[lang]
    url = SITE + page
    alt_url = SITE + alternate
    it_url, en_url = (url, alt_url) if lang == "it" else (alt_url, url)
    R = rel(page, "")
    ld_page = {"@type": kind, "@id": url + "#webpage", "url": url, "name": title, "description": desc,
               "inLanguage": lang, "isPartOf": {"@id": SITE + "#website"}, "about": {"@id": SITE + "#software"}}
    if kind == "TechArticle":
        ld_page.update({"headline": title.split(" · ")[0], "dateModified": VERIFIED})
    if image:
        ld_page["primaryImageOfPage"] = {"@type": "ImageObject", "url": SITE + image["path"],
                                         "width": image["width"], "height": image["height"]}
    if extra_ld:
        ld_page.update(extra_ld)
    ld = {"@context": "https://schema.org", "@graph": [ld_page, {
        "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE + target}
            for i, (name, target) in enumerate(crumbs)]}]}
    og = image or {"path": f"media/og/trama-{lang}.jpg", "width": 1200, "height": 630, "alt": t["index_title"]}
    og_type = "image/png" if og["path"].endswith(".png") else "image/jpeg"
    return f'''<!doctype html>
<html lang="{lang}"{' class="wide"' if wide else ""}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="{R}site/lang.js"></script>
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="it" href="{it_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{en_url}">
<link rel="icon" type="image/svg+xml" href="{R}site/trama.svg">
<link rel="preload" href="{R}site/fonts/bricolage-grotesque-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{R}site/style.css">
<link rel="stylesheet" href="{R}site/guide.css">
<meta property="og:site_name" content="Trama">
<meta property="og:type" content="{"article" if kind == "TechArticle" else "website"}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{t["locale"]}">
<meta property="og:locale:alternate" content="{T[t["other"]]["locale"]}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{SITE}{og["path"]}">
<meta property="og:image:type" content="{og_type}">
<meta property="og:image:width" content="{og["width"]}">
<meta property="og:image:height" content="{og["height"]}">
<meta property="og:image:alt" content="{E(og.get("alt", title))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{SITE}{og["path"]}">
<meta name="twitter:image:alt" content="{E(og.get("alt", title))}">
<meta name="theme-color" content="#08232f">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>
<script>document.documentElement.classList.add("js")</script>
<script defer src="{R}site/guide.js"></script>
</head>'''


def chrome(page, lang, alternate, body):
    t = T[lang]
    R = rel(page, "")
    home = rel(page, "" if lang == "it" else "en/")
    feats = rel(page, "funzionalita/" if lang == "it" else "en/features/")
    guide = rel(page, url_index(lang))
    other = rel(page, alternate)
    if lang == "it":
        langs = (f'<span class="on" aria-current="true" lang="it" title="Italiano">IT</span>'
                 f'<a href="{other}" hreflang="en" lang="en" title="English" aria-label="English">EN</a>')
    else:
        langs = (f'<a href="{other}" hreflang="it" lang="it" title="Italiano" aria-label="Italiano">IT</a>'
                 f'<span class="on" aria-current="true" lang="en" title="English">EN</span>')
    current = ' aria-current="page"' if page == url_index(lang) else ' aria-current="true"'
    return f'''<body>
<a class="skip" href="#contenuto">{t["skip"]}</a>
<header class="top"><div class="wrap">
<a class="brand" href="{home}"><img src="{R}site/trama.svg" alt="" width="34" height="34">Trama</a>
<nav aria-label="{t["site_nav"]}"><a href="{home}">{t["home"]}</a><a href="{feats}">{t["features"]}</a><a href="{guide}"{current}>{t["guide"]}</a></nav>
<div class="langs" role="group" aria-label="{t["langs"]}">{langs}</div>
<a class="btn" data-release-download href="{RELEASE_ZIP}">{DL}{t["download"]}</a></div></header>
{body}
<footer><div class="wrap"><div class="brand"><img src="{R}site/trama.svg" alt="" width="34" height="34">Trama</div><p>{t["footer"]}</p><nav aria-label="{t["links"]}"><a href="{guide}">{t["guide_index"]}</a><a href="{home}">{t["home"]}</a><a href="{feats}">{t["features"]}</a><a data-release-page href="{RELEASE_PAGE}">{t["news"]}</a><a href="https://github.com/realfulvio/Trama/blob/main/LICENSE">{t["license"]}</a></nav><p>{t["legal"]}</p></div></footer>
<script src="{R}site/releases.js" defer></script>
</body>
</html>
'''


def search_form(action, lang, big=False):
    t = T[lang]
    fid = "qb" if big else "q"
    return f'''<form class="search{" big" if big else ""}" role="search" action="{action}" method="get">
<label for="{fid}">{t["search"]}</label>
<div class="field">{SEARCH}<input id="{fid}" name="q" type="search" placeholder="{t["placeholder"]}" autocomplete="off"><button class="go" type="submit">{t["search_go"]}</button></div>
</form>'''


def chapter_items(rows, section, lang, page):
    t, out = T[lang], []
    for row in (r for r in rows if r["sezione"] == section):
        title = row["capitolo"] if lang == "it" else row["chapter"]
        example = row["esempio"] if lang == "it" else row["example"]
        cls, status = t["status"][row["tranche"]]
        text = f'{title} {example} {row["slug"]} {row["slug_en"]} {KEYWORDS[lang].get(row["slug"], "")} {section_name(section, lang)[0]}'
        head_ = (f'<a href="{rel(page, url_chapter(row, lang))}">{E(title)}</a>' if row["tranche"] == 1
                 else f'<span class="t">{E(title)}</span>')
        out.append(f'<li class="ch {cls}" data-q="{E(fold(text))}">{head_}<span class="st">{status}</span>'
                   f'<span class="ex">{t["example"]}: {E(example)}</span></li>')
    return "\n".join(out)


def guide_box(rows, section, lang, page, heading_link=True):
    t = T[lang]
    name, desc = section_name(section, lang)
    n = sum(1 for r in rows if r["sezione"] == section)
    r_ = sum(1 for r in rows if r["sezione"] == section and r["tranche"] == 1)
    title = f'<a href="{rel(page, url_section(section, lang))}">{name}</a>' if heading_link else name
    return f'''<section class="guide" id="{section_slug(section, lang)}" aria-labelledby="g-{section}" data-section="{section}">
<div class="ghead">{icon(section)}<div><h2 id="g-{section}">{title}</h2><p>{desc}</p><p class="gcount">{t["section_count"].format(n=n, r=r_).replace("1 pronti", "1 pronto")}</p></div></div>
<ul class="chs">
{chapter_items(rows, section, lang, page)}
</ul>
</section>'''


def tranche_table(rows, lang):
    t = T[lang]
    out = []
    for n in (1, 2, 3, 4):
        names = [(r["capitolo"] if lang == "it" else r["chapter"]) for r in rows if r["tranche"] == n]
        out.append(f'<tr><th scope="row">{t["tranche_names"][n]}</th><td>{len(names)}</td><td>{E(", ".join(names))}</td></tr>')
    head_ = ("<th scope=\"col\">Tranche</th><th scope=\"col\">Capitoli</th><th scope=\"col\">Titoli</th>" if lang == "it"
             else "<th scope=\"col\">Batch</th><th scope=\"col\">Chapters</th><th scope=\"col\">Titles</th>")
    return f'<div class="table-wrap"><table class="tranches"><thead><tr>{head_}</tr></thead><tbody>{"".join(out)}</tbody></table></div>'


def index_page(rows, lang, chapters):
    t = T[lang]
    page = url_index(lang)
    alt = url_index(t["other"])
    ready = [r for r in rows if r["tranche"] == 1]
    feature_row = next(r for r in rows if r["slug"] == "k-means")
    km_meta = chapters[("k-means", lang)][0]
    img = km_meta["files"]["groups_3"]
    feature = (f'<a class="feature" href="{rel(page, url_chapter(feature_row, lang))}"><img src="{rel(page, img["path"])}" '
               f'width="{img["width"]}" height="{img["height"]}" alt="" loading="lazy"><span><small>{km_meta["feature_tag"]}</small>'
               f'<b>{E(km_meta["title"])}</b><span>{E(km_meta["feature"])}</span></span></a>')
    anatomy = "".join(f"<li><b>{a}</b>{b}</li>" for a, b in t["anat"])
    hints = " ".join(f'<a href="?q={h.replace(" ", "+")}">{h}</a>' for h in t["hints"])
    count = t["count"].format(n=len(rows), r=len(ready), d=sum(1 for r in rows if r["tranche"] == 2))
    readies = "".join(f'<li><a href="{rel(page, url_chapter(r, lang))}">{E(r["capitolo"] if lang == "it" else r["chapter"])}</a>'
                      f' <span>· {section_name(r["sezione"], lang)[0]}</span></li>' for r in ready)
    body = f'''<main id="contenuto">
<div class="ihero"><div class="wrap">
<p class="eyebrow">{t["eyebrow"]}</p>
<h1>{t["h1"]}</h1>
<p class="lead">{t["lead"]}</p>
{search_form("./", lang, big=True)}
<p class="hints">{t["try"]} {hints}</p>
</div></div>
<div class="wrap ibody">
<div class="ilead">{feature}<div><h2 class="small">{t["anatomy"]}</h2><ol class="anat" aria-label="{t["anatomy"]}">{anatomy}</ol></div></div>
<div class="ilead readies"><div><h2 class="small">{t["ready_list"]}</h2><ul class="rlist">{readies}</ul></div></div>
<p class="count" id="esito" aria-live="polite">{count}</p>
<div class="empty" id="vuoto" hidden><p><b>{t["empty"]}</p><button type="button" class="btn line-l" data-clear>{t["show_all"]}</button></div>
<div class="guides">{"".join(guide_box(rows, s, lang, page) for s in SECTIONS)}</div>
<section class="tranche-box ilead" aria-labelledby="h-tranche"><div><h2 class="small" id="h-tranche">{t["tranches"]}</h2><p class="note-s">{t["tranche_text"]}</p>{tranche_table(rows, lang)}</div></section>
</div>
</main>'''
    crumbs = [("Trama", "" if lang == "it" else "en/"), (t["guide"], page)]
    return head(page, lang, t["index_title"], t["index_desc"], alternate=alt, image=None, crumbs=crumbs) + "\n" + chrome(page, lang, alt, body)


def section_page(rows, section, lang):
    t = T[lang]
    page = url_section(section, lang)
    alt = url_section(section, t["other"])
    name, desc = section_name(section, lang)
    others = "".join(f'<li><a href="{rel(page, url_section(s, lang))}">{icon(s)}{section_name(s, lang)[0]}</a></li>'
                     for s in SECTIONS if s != section)
    body = f'''<main id="contenuto">
<div class="ihero shero"><div class="wrap">
<p class="crumbs"><a href="../">{t["guide"]}</a><span aria-hidden="true">›</span><span aria-current="page">{name}</span></p>
<h1>{name}</h1>
<p class="lead">{desc}</p>
{search_form("../", lang, big=False)}
</div></div>
<div class="wrap ibody">
<div class="guides one">{guide_box(rows, section, lang, page, heading_link=False)}</div>
<nav class="others" aria-label="{t["other_guides"]}"><h2 class="small">{t["other_guides"]}</h2><ul>{others}</ul></nav>
</div>
</main>'''
    crumbs = [("Trama", "" if lang == "it" else "en/"), (t["guide"], url_index(lang)), (name, page)]
    title = t["section_title"].format(name=name)
    return head(page, lang, title, f"{t['section_lead'].format(name=name)} {desc}", alternate=alt, image=None,
                crumbs=crumbs) + "\n" + chrome(page, lang, alt, body)


def chapter_page(rows, row, lang, meta, body):
    t = T[lang]
    page = url_chapter(row, lang)
    alt = url_chapter(row, t["other"])
    section = row["sezione"]
    sname = section_name(section, lang)[0]
    tree = []
    for r in (r for r in rows if r["sezione"] == section):
        title = E(r["capitolo"] if lang == "it" else r["chapter"])
        if r is row:
            tree.append(f'<li><a href="./" aria-current="page">{title}</a></li>')
        elif r["tranche"] == 1:
            tree.append(f'<li><a href="{rel(page, url_chapter(r, lang))}">{title}</a></li>')
        else:
            tree.append(f'<li class="{"draft" if r["tranche"] == 2 else "plan"}"><span>{title}</span></li>')
    others = "".join(f'<li><a href="{rel(page, url_section(s, lang))}">{section_name(s, lang)[0]}</a></li>'
                     for s in SECTIONS if s != section)
    toc = "".join(f'<li><a href="#{i}">{E(label)}</a></li>' for i, label in meta["toc"])
    downloads = "".join(f'<li><a href="{rel(page, meta["files"][k]["path"])}" download>{DL}{E(label)}</a></li>'
                        for k, label in meta["downloads"])
    facts = "".join(f"<li><b>{E(k)}</b> {E(v)}</li>" for k, v in meta["facts"])
    proof = "".join(f"<div><dt>{E(k)}</dt><dd>{v}</dd></div>" for k, v in
                    [(t["trama"], VERSION), (t["commit"], f"<code>{COMMIT}</code>")] + meta["proof"])
    ready = [r for r in rows if r["tranche"] == 1]
    i = ready.index(row)
    prev_ = ready[i - 1] if i > 0 else None
    next_ = ready[i + 1] if i + 1 < len(ready) else None
    pager = '<nav class="pager" aria-label="' + ("Capitoli vicini" if lang == "it" else "Nearby chapters") + '">'
    pager += (f'<a href="{rel(page, url_chapter(prev_, lang))}"><small>{t["back"]}</small>{E(prev_["capitolo"] if lang == "it" else prev_["chapter"])}</a>'
              if prev_ else f'<a href="{rel(page, url_index(lang))}"><small>{t["index"]}</small>{t["to_index"]}</a>')
    pager += (f'<a href="{rel(page, url_chapter(next_, lang))}"><small>{t["next"]}</small>{E(next_["capitolo"] if lang == "it" else next_["chapter"])}</a>'
              if next_ else f'<a href="{rel(page, url_index(lang))}"><small>{t["index"]}</small>{t["to_index"]}</a>')
    pager += "</nav>"
    gi, si = rel(page, url_index(lang)), rel(page, url_section(section, lang))
    head_html = f'''<header class="chap-head" id="inizio">
<p class="crumbs" aria-label="{t["breadcrumb"]}"><a href="{gi}">{t["guide"]}</a><span aria-hidden="true">›</span><a href="{si}">{sname}</a><span aria-hidden="true">›</span><span aria-current="page">{E(meta["short"])}</span></p>
<h1>{E(meta["title"])}</h1>
<p class="ask">{meta["ask"]}</p>
<ul class="facts" aria-label="{t["proof"]}">{facts}</ul>
</header>'''
    nsrc = len(re.findall(r"<li\b", body.split('id="fonti"', 1)[-1].split("</ol>", 1)[0]))
    content = f'''<div class="wrap docs">
<aside class="side" aria-label="{t["guide_index"]}">
<details class="gnav" open><summary>{t["guide_index"]}</summary>
{search_form(gi, lang)}
<p class="gl"><a href="{gi}">{t["all_guides"]}</a></p>
<h2 class="gname"><a href="{si}">{icon(section)}{sname}</a></h2>
<ul class="gtree">{"".join(tree)}</ul>
<h2 class="gname sub">{t["other_guides"]}</h2>
<ul class="gtree">{others}</ul>
</details>
</aside>
<aside class="rail" aria-label="{t["in_chapter"]}">
<details class="toc" open><summary>{t["in_chapter"]}</summary><ol>{toc}</ol></details>
<details class="card proof" open><summary><h2>{t["proof"]}</h2></summary>
<dl>{proof}</dl>
<ul class="dl">{downloads}</ul>
<a class="tofonti" href="#fonti">{nsrc} {t["sources"]} ↓</a></details>
</aside>
<main id="contenuto" class="doc">
<article>{head_html}
{body.strip()}
{pager}</article>
</main>
</div>'''
    crumbs = [("Trama", "" if lang == "it" else "en/"), (t["guide"], url_index(lang)), (sname, url_section(section, lang)),
              (meta["short"], page)]
    image = dict(meta["files"][meta["image"]], alt=meta["image_alt"])
    title = f'{meta["title"]} · {"Guida di Trama" if lang == "it" else "Trama guide"}'
    return (head(page, lang, title, meta["description"], alternate=alt, image=image, crumbs=crumbs,
                 kind="TechArticle", wide=True) + "\n" + chrome(page, lang, alt, content))


def write(page, text):
    path = ROOT / page / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return page


def sitemap(pages):
    existing = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    keep = [u for u in re.findall(r"<url>.*?</url>", existing, re.S) if "/guida/" not in u and "/guide/" not in u]
    out = list(keep)
    for it, en in pages:
        for loc in (it, en):
            out.append(f'<url><loc>{SITE}{loc}</loc><lastmod>{VERIFIED}</lastmod>'
                       f'<xhtml:link rel="alternate" hreflang="it" href="{SITE}{it}"/>'
                       f'<xhtml:link rel="alternate" hreflang="en" href="{SITE}{en}"/>'
                       f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{en}"/></url>')
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(out) + "\n</urlset>\n", encoding="utf-8")


def main():
    rows = load_rows()
    manifest = json.loads((SRC / "allegati.json").read_text(encoding="utf-8"))
    chapters = {(r["slug"], lang): load_chapter(r, lang, manifest)
                for r in rows if r["tranche"] == 1 for lang in ("it", "en")}
    pairs = []
    for lang in ("it", "en"):
        write(url_index(lang), index_page(rows, lang, chapters))
        for section in SECTIONS:
            write(url_section(section, lang), section_page(rows, section, lang))
        for row in rows:
            if row["tranche"] == 1:
                write(url_chapter(row, lang), chapter_page(rows, row, lang, *chapters[(row["slug"], lang)]))
    pairs.append((url_index("it"), url_index("en")))
    pairs += [(url_section(s, "it"), url_section(s, "en")) for s in SECTIONS]
    pairs += [(url_chapter(r, "it"), url_chapter(r, "en")) for r in rows if r["tranche"] == 1]
    sitemap(pairs)
    print(f"ok: {len(pairs) * 2} pagine")


if __name__ == "__main__":
    main()
