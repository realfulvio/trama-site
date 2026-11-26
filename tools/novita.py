"""Genera le pagine Novità (novita/ e en/whats-new/) dalle note di rilascio di Trama.

Uso: python tools/novita.py PERCORSO_DEL_CLONE_DI_TRAMA
Legge docs/release-*.md dalla 0.104 in poi: la parte prima di "## English" è
l'italiano, quella dopo l'inglese. Solo libreria standard.

Regola del sito: niente nomi né estensioni di formati di prodotti di terzi.
Le voci che li contengono vengono saltate e il generatore le elenca a video.
"""
import html
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
FIRST = (0, 104, 0)
THIRD_PARTY = re.compile(r"\bPZ[A-Z]\b|Prism|GraphPad|\.pz", re.I)

TEXT = {
    "it": {
        "path": "novita/index.html", "url": "https://tramastat.org/novita/", "alt": "https://tramastat.org/en/whats-new/",
        "title": "Novità di Trama: che cosa cambia a ogni versione",
        "desc": "Le novità di Trama versione per versione, dalla più recente: analisi, fogli, grafici e correzioni.",
        "skip": "Vai al contenuto", "lang": "Lingua", "nav": "Pagine",
        "h1": "Novità", "lead": "Che cosa cambia a ogni versione di Trama, dalla più recente. Tutte le versioni 0.x sono beta.",
        "latest": "Ultima versione", "notes": "Note di rilascio e download", "all": "Tutte le versioni su GitHub",
        "older": "Le versioni precedenti alla 0.104 sono nell’archivio su GitHub.",
        "download": "Scarica",
    },
    "en": {
        "path": "en/whats-new/index.html", "url": "https://tramastat.org/en/whats-new/", "alt": "https://tramastat.org/novita/",
        "title": "What’s new in Trama: changes in every version",
        "desc": "What changes in each Trama version, newest first: analyses, worksheets, graphs and fixes.",
        "skip": "Skip to content", "lang": "Language", "nav": "Pages",
        "h1": "What’s new", "lead": "What changes in each Trama version, newest first. Every 0.x version is a beta.",
        "latest": "Latest version", "notes": "Release notes and download", "all": "All versions on GitHub",
        "older": "Versions before 0.104 are in the GitHub archive.",
        "download": "Download",
    },
}


def inline(md):
    out = html.escape(md, quote=False)
    out = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", out)          # i link interni ai docs non servono sul sito
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return out


def bullets(block):
    items, cur = [], None
    for line in block.splitlines():
        if line.startswith("- "):
            cur = [line[2:].strip()]
            items.append(cur)
        elif cur is not None and line.startswith("  ") and line.strip():
            cur.append(line.strip())
        else:
            cur = None
    if not items:  # alcune note inglesi sono un riassunto in prosa: ogni paragrafo diventa una voce
        paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", block)]
        return [p for p in paras if p and not p.startswith(("#", "Extract the ZIP", "Estrai lo ZIP")) and not p.lower().startswith("summary")]
    return [" ".join(i) for i in items]


def releases(trama):
    found = []
    for f in sorted((Path(trama) / "docs").glob("release-*.md")):
        text = f.read_text(encoding="utf-8")
        m = re.match(r"# Trama (\d+)\.(\d+)\.(\d+)", text)
        if not m:
            continue
        ver = tuple(int(x) for x in m.groups())
        if ver < FIRST:
            continue
        it, _, en = text.partition("\n## English")
        en = en.split("\n", 1)[1] if "\n" in en else ""
        lang = {"it": bullets(it), "en": bullets(en)}
        for code, items in lang.items():
            kept = [i for i in items if not THIRD_PARTY.search(i)]
            for i in items:
                if THIRD_PARTY.search(i):
                    print(f"saltata ({code} {'.'.join(map(str, ver))}): {i[:70]}…")
            lang[code] = kept
        found.append((ver, lang))
    found.sort(reverse=True)
    return found


def page(code, rels):
    t = TEXT[code]
    up = "../../" if code == "en" else "../"
    home = up + ("en/" if code == "en" else "")
    feats = up + ("en/features/" if code == "en" else "funzionalita/")
    other = up + ("novita/" if code == "en" else "en/whats-new/")
    names = {"it": ("Home", "Funzionalità", "Novità"), "en": ("Home", "Features", "What’s new")}[code]
    latest = ".".join(map(str, rels[0][0]))
    zip_url = f"https://github.com/realfulvio/Trama/releases/download/v{latest}/Trama-{latest}-Windows-x64.zip"
    arts = []
    for i, (ver, lang) in enumerate(rels):
        v = ".".join(map(str, ver))
        if not lang[code]:
            continue
        badge = f' <span class="tag">{t["latest"]}</span>' if i == 0 else ""
        lis = "".join(f"<li>{inline(x)}</li>" for x in lang[code])
        arts.append(
            f'<article class="rel{" latest" if i == 0 else ""}" id="v{v.replace(".", "-")}">'
            f'<h2>Trama {v} beta{badge}</h2><ul>{lis}</ul>'
            f'<a href="https://github.com/realfulvio/Trama/releases/tag/v{v}">{t["notes"]}</a></article>'
        )
    langs = (
        f'<span class="on" aria-current="true" lang="it" title="Italiano">IT</span><a href="{other}" hreflang="en" lang="en" title="English" aria-label="English">EN</a>'
        if code == "it" else
        f'<a href="{other}" hreflang="it" lang="it" title="Italiano" aria-label="Italiano">IT</a><span class="on" aria-current="true" lang="en" title="English">EN</span>'
    )
    it_url, en_url = TEXT["it"]["url"], TEXT["en"]["url"]
    return f"""<!doctype html>
<html lang="{code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t["title"]}</title>
<meta name="description" content="{t["desc"]}">
<link rel="canonical" href="{t["url"]}">
<link rel="alternate" hreflang="it" href="{it_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{en_url}">
<link rel="icon" type="image/svg+xml" href="{up}site/trama.svg">
<link rel="preload" href="{up}site/fonts/bricolage-grotesque-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{up}site/style.css">
<link rel="stylesheet" href="{up}site/pages.css">
<meta property="og:site_name" content="Trama">
<meta property="og:type" content="website">
<meta property="og:url" content="{t["url"]}">
<meta property="og:title" content="{t["title"]}">
<meta property="og:description" content="{t["desc"]}">
<meta property="og:image" content="https://tramastat.org/media/workflows-112/workspace-{code}.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#08232f">
</head>
<body>
<a class="skip" href="#contenuto">{t["skip"]}</a>
<header class="top"><div class="wrap">
<a class="brand" href="{home}"><img src="{up}site/trama.svg" alt="" width="34" height="34">Trama</a>
<nav aria-label="{t["nav"]}"><a href="{home}">{names[0]}</a><a href="{feats}">{names[1]}</a><a href="./" aria-current="page">{names[2]}</a></nav>
<div class="langs" role="group" aria-label="{t["lang"]}">{langs}</div>
<a class="btn" data-release-download href="{zip_url}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 11l5 5 5-5M5 20h14"/></svg>{t["download"]}</a></div></header>
<main id="contenuto">
<div class="phead"><div class="wrap"><h1>{t["h1"]}</h1><p>{t["lead"]}</p></div></div>
<div class="wrap page-body"><div class="tl">
{chr(10).join(arts)}
</div>
<p class="tl-end">{t["older"]} <a href="https://github.com/realfulvio/Trama/releases">{t["all"]}</a></p></div>
</main>
<footer><div class="wrap"><div class="brand"><img src="{up}site/trama.svg" alt="" width="34" height="34">Trama</div><nav aria-label="{t["nav"]}"><a href="{home}">{names[0]}</a><a href="{feats}">{names[1]}</a><a href="./">{names[2]}</a><a href="https://github.com/realfulvio/Trama">GitHub</a><a href="https://github.com/realfulvio/Trama/blob/main/LICENSE">{"Licenza MIT" if code == "it" else "MIT licence"}</a></nav></div></footer>
<script src="{up}site/releases.js" defer></script>
</body>
</html>
"""


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    rels = releases(sys.argv[1])
    for code in ("it", "en"):
        out = SITE / TEXT[code]["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(code, rels), encoding="utf-8")
        print("scritto", out.relative_to(SITE), len(rels), "versioni")


if __name__ == "__main__":
    main()
