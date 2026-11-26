"""Genera le pagine Novità (novita/ e en/whats-new/) dalle note di rilascio di Trama.

Uso: python tools/novita.py PERCORSO_DEL_CLONE_DI_TRAMA
Legge docs/release-*.md dalla 0.104 in poi: la parte prima di "## English" è
l'italiano, quella dopo l'inglese. Solo libreria standard.

Regola del sito: niente nomi né estensioni di formati di prodotti di terzi.
Le voci che li contengono vengono saltate e il generatore le elenca a video.
"""
from datetime import date
import html
import re
import sys
from pathlib import Path

CURVES = '<svg class="hero-bg" viewBox="0 0 1440 640" preserveAspectRatio="none" aria-hidden="true"><path pathLength="1" d="M-20 560C420 560 520 150 1460 110"/><path pathLength="1" d="M-20 600C560 600 700 260 1460 220"/><path pathLength="1" d="M-20 500C300 500 420 60 1460 40"/></svg>'
DOWNLOAD_MARK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 11l5 5 5-5M5 20h14"/></svg>'
GITHUB_MARK = '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>'
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
        "dl_long": "Scarica la {v}", "jump": "Vai a una versione", "close_h": "Provala sui tuoi dati", "close_p": "Gratuita, portabile, in italiano e in inglese. Estrai lo ZIP e apri Trama.exe.", "dl_win": "Scarica per Windows x64", "code": "Codice su GitHub",
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
        "dl_long": "Download {v}", "jump": "Jump to a version", "close_h": "Try it on your own data", "close_p": "Free, portable, in Italian and English. Extract the ZIP and open Trama.exe.", "dl_win": "Download for Windows x64", "code": "Code on GitHub",
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
    gh_label = "Codice sorgente su GitHub" if code == "it" else "Source code on GitHub"
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
            f'<article class="rel rv{" latest" if i == 0 else ""}" id="v{v.replace(".", "-")}">'
            f'<h2>Trama {v} beta{badge}</h2><ul>{lis}</ul>'
            f'<a href="https://github.com/realfulvio/Trama/releases/tag/v{v}">{t["notes"]}</a></article>'
        )
    vers = "".join(f'<li><a href="#v{".".join(map(str, ver)).replace(".", "-")}">{".".join(map(str, ver))}</a></li>' for ver, lang in rels if lang[code])
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
<a class="gh" href="https://github.com/realfulvio/Trama" aria-label="{gh_label}" title="{gh_label}">{GITHUB_MARK}<span>GitHub</span></a>
<a class="btn" data-release-download href="{zip_url}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 11l5 5 5-5M5 20h14"/></svg>{t["download"]}</a></div></header>
<main id="contenuto">
<div class="phead">{CURVES}<div class="wrap page-in"><h1>{t["h1"]}</h1><p>{t["lead"]}</p>
<div class="cta"><a class="btn" data-release-download href="{zip_url}">{DOWNLOAD_MARK}{t["dl_long"].format(v=latest)}</a><a class="btn line" href="https://github.com/realfulvio/Trama">{GITHUB_MARK}{t["code"]}</a></div>
<ul class="vers" aria-label="{t["jump"]}">{vers}</ul></div></div>
<div class="wrap page-body"><div class="tl">
{chr(10).join(arts)}
</div>
<p class="tl-end">{t["older"]} <a href="https://github.com/realfulvio/Trama/releases">{t["all"]}</a></p>
<div class="close rv"><div><h2>{t["close_h"]}</h2><p>{t["close_p"]}</p></div><div class="cta"><a class="btn" data-release-download href="{zip_url}">{DOWNLOAD_MARK}{t["dl_win"]}</a><a class="btn line" href="https://github.com/realfulvio/Trama">{GITHUB_MARK}{t["code"]}</a></div></div></div>
</main>
<footer><div class="wrap"><div class="brand"><img src="{up}site/trama.svg" alt="" width="34" height="34">Trama</div><nav aria-label="{t["nav"]}"><a href="{home}">{names[0]}</a><a href="{feats}">{names[1]}</a><a href="./">{names[2]}</a><a class="gh-foot" href="https://github.com/realfulvio/Trama">{GITHUB_MARK}GitHub</a><a href="https://github.com/realfulvio/Trama/blob/main/LICENSE">{"Licenza MIT" if code == "it" else "MIT licence"}</a></nav></div></footer>
<script src="{up}site/motion.js" defer></script>
<script src="{up}site/releases.js" defer></script>
</body>
</html>
"""


VERSION = r"\d+\.\d+\.\d+"
RELEASE_ROOT = "https://github.com/realfulvio/Trama/releases"


def refresh_release_fields(version):
    """Update static downloads and the catalogue release labels, including without JavaScript."""
    for name in ("index.html", "en/index.html", "funzionalita/index.html", "en/features/index.html"):
        path = SITE / name
        text = path.read_text(encoding="utf-8")
        text = re.sub(rf"{RELEASE_ROOT}/download/v{VERSION}/Trama-{VERSION}-Windows-x64\.zip",
                      f"{RELEASE_ROOT}/download/v{version}/Trama-{version}-Windows-x64.zip", text)
        text = re.sub(rf"{RELEASE_ROOT}/tag/v{VERSION}", f"{RELEASE_ROOT}/tag/v{version}", text)
        if name in ("index.html", "en/index.html"):
            text = re.sub(rf'("softwareVersion":"){VERSION}(")', rf'\g<1>{version}\2', text)
            text = re.sub(rf'(data-release-version>Beta ){VERSION}', rf'\g<1>{version}', text)
            text = re.sub(rf'Trama-{VERSION}-Windows-x64\.zip', f'Trama-{version}-Windows-x64.zip', text)
        else:
            text = re.sub(rf'{VERSION} beta', f'{version} beta', text)
            for status in ("ok", "plan"):
                count = text.count(f'data-s="{status}"')
                text = re.sub(rf'(data-feature-count="{status}">)\d+', rf'\g<1>{count}', text)
        path.write_text(text, encoding="utf-8")


def refresh_sitemap():
    path = SITE / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<lastmod>\d{4}-\d{2}-\d{2}</lastmod>", f"<lastmod>{date.today()}</lastmod>", text)
    path.write_text(text, encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    rels = releases(sys.argv[1])
    for code in ("it", "en"):
        out = SITE / TEXT[code]["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(code, rels), encoding="utf-8")
        print("scritto", out.relative_to(SITE), len(rels), "versioni")
    refresh_release_fields(".".join(map(str, rels[0][0])))
    refresh_sitemap()


if __name__ == "__main__":
    main()
