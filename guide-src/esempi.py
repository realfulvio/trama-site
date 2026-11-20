"""Genera gli allegati dei capitoli della guida con Trama (dati sintetici) e verifica i numeri.

Uso, dalla radice del sito:
    PYTHONPATH=/percorso/Trama-0.95.0 python guide-src/esempi.py            # tutti i capitoli
    PYTHONPATH=/percorso/Trama-0.95.0 python guide-src/esempi.py anova      # uno solo
    ... --senza-app                                                          # niente schermate

Serve il sorgente di Trama alla versione indicata in VERSION (tag e commit in guide-src/build.py) con le sue
dipendenze, PySide6 compreso. Per ogni capitolo e lingua scrive dati (.csv), progetto (.alab), numeri di prova
(.json), figure esportate da Trama e schermate dell'app. Ogni numero citato nelle pagine è controllato qui con
un assert: se una versione nuova di Trama cambia un risultato, lo script si ferma.

In guide-src/allegati.json resta l'elenco dei file con dimensioni e misure delle immagini, che build.py usa.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "guide-src" / "allegati.json"
VERSION = "0.95.0"
BASE = {"it": ROOT / "guida" / "allegati", "en": ROOT / "en" / "guide" / "files"}
SUB = {"it": ("dati", "figure", "app"), "en": ("data", "figures", "app")}
SLUG = {"k-means": "k-means", "anova": "anova", "curva-standard": "standard-curve",
        "colonne-calcolate": "calculated-columns", "esportazione": "vector-export"}

if os.environ.get("PYTHONHASHSEED") != "0":  # sottoinsiemi di caratteri nel PDF uguali a ogni esecuzione
    os.environ["PYTHONHASHSEED"] = "0"
    os.execv(sys.executable, [sys.executable, *sys.argv])
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["TRAMA_NO_ANIMATIONS"] = "1"
# File riproducibili: data fissa nei metadati SVG/PDF e identificativi interni stabili.
os.environ["SOURCE_DATE_EPOCH"] = "1795132800"  # 2026-11-20
import matplotlib  # noqa: E402
matplotlib.rcParams["svg.hashsalt"] = "trama-guida"

from analisi import _version, kmeans_options, parallel  # noqa: E402
from analisi.data import Dataset, load_project, save_project  # noqa: E402
from analisi.figure_export import export_figure  # noqa: E402
from analisi.i18n import set_language  # noqa: E402
from analisi.presentation import Layout  # noqa: E402
from analisi.workbench import METHODS, analyse  # noqa: E402

parallel.configure(1)
assert _version.VERSION == VERSION, f"Serve Trama {VERSION}, trovata {_version.VERSION}"


def opts(method, **given):
    """Opzioni complete come le riempie la finestra: primo valore delle scelte, numeri e caselle predefiniti."""
    out = {}
    for key, value in METHODS[method].items():
        if isinstance(value, tuple):
            out[key] = value[0]
        elif isinstance(value, (bool, int, float)):
            out[key] = value
    out.update(given)
    return out


def run(method, frame, **given):
    return analyse(method, frame, opts(method, **given))


def close(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


class Chapter:
    """Cartelle e nomi dei file di un capitolo in una lingua; tiene l'elenco per il manifest."""

    def __init__(self, slug, lang):
        self.slug, self.lang = slug, lang
        self.root = BASE[lang] / (slug if lang == "it" else SLUG[slug])
        self.data, self.fig, self.app = (self.root / s for s in SUB[lang])
        for folder in (self.data, self.fig, self.app):
            folder.mkdir(parents=True, exist_ok=True)
        self.files = {}

    def rel(self, path):
        return path.relative_to(ROOT).as_posix()

    def add(self, key, path):
        info = {"path": self.rel(path), "bytes": path.stat().st_size}
        if path.suffix == ".png":
            from PIL import Image
            with Image.open(path) as image:
                info["width"], info["height"] = image.size
        self.files[key] = info
        return path

    def csv(self, key, name, frame):
        path = self.data / name
        frame.to_csv(path, index=False, lineterminator="\n")
        return self.add(key, path)

    def json(self, key, name, payload):
        path = self.data / name
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return self.add(key, path)

    def project(self, key, name, tables, layouts=()):
        path = self.data / name
        save_project(path, tables, layouts=layouts)
        return self.add(key, path)

    def figure(self, key, name, figure, *, svg=False, dpi=120):
        path = self.fig / f"{name}.png"
        export_figure(figure, path, {"format": "png", "dpi": dpi})
        self.add(key, path)
        if svg:
            self.add(key + "_svg", self._svg(figure, name))
        return path

    def _svg(self, figure, name):
        path = self.fig / f"{name}.svg"
        export_figure(figure, path, {"format": "svg", "svg_text": "text"})
        return path


# ---------------------------------------------------------------------------------------------------------
# K-means: 45 segnali sintetici (stesso generatore del brief, seme 19) e caso limite in µV.
# ---------------------------------------------------------------------------------------------------------
KM = {
    "it": {"sheet": "Segnali sintetici", "vars": ["Ampiezza (mV)", "Deriva (mV/min)"],
           "uV": "Ampiezza (µV)", "sheet_uV": "Segnali in µV",
           "csv": "segnali-sintetici.csv", "alab": "esempio-k-means.alab", "json": "risultati.json",
           "csv_uV": "segnali-sintetici-uV.csv", "alab_uV": "caso-limite-uV.alab", "json_uV": "caso-limite-uV.json",
           "groups": "gruppi-{k}", "raw": "caso-limite-uV-non-standardizzato", "std": "caso-limite-uV-standardizzato"},
    "en": {"sheet": "Synthetic signals", "vars": ["Amplitude (mV)", "Drift (mV/min)"],
           "uV": "Amplitude (µV)", "sheet_uV": "Signals in µV",
           "csv": "synthetic-signals.csv", "alab": "k-means-example.alab", "json": "results.json",
           "csv_uV": "synthetic-signals-uV.csv", "alab_uV": "edge-case-uV.alab", "json_uV": "edge-case-uV.json",
           "groups": "clusters-{k}", "raw": "edge-case-uV-not-standardized", "std": "edge-case-uV-standardized"},
}


def kmeans_points():
    rng = np.random.default_rng(19)
    centres = [(-1.45, .25), (.95, -1.1), (1.65, 1.53)]
    return np.vstack([rng.normal(c, [.23, .20], (15, 2)) for c in centres]).round(4)


def kmeans(lang):
    L, ch = KM[lang], Chapter("k-means", lang)
    frame = pd.DataFrame(kmeans_points(), columns=L["vars"])
    base = {"Variables": L["vars"], "Standardize": True, "Seed": 42}
    selection = {**base, "Criterion": "Silhouette", "Minimum k": 2, "Maximum k": 4}
    scan = analyse(kmeans_options.SELECTION, frame, opts(kmeans_options.SELECTION, **selection))
    metrics, suggested = scan.tables["Model metrics"], int(scan.tables["Selection"].loc["Suggested k", "Value"])
    expected = {2: (36.17482370521825, .6204974295100698), 3: (2.678388924024927, .8555585957524268),
                4: (2.0363623166135474, .7326367441605375)}
    for k, (wss, sil) in expected.items():
        assert close(metrics.loc[k, "WSS"], wss) and close(metrics.loc[k, "Silhouette"], sil), (k, metrics)
    assert suggested == 3
    one = analyse(kmeans_options.SELECTION, frame, opts(kmeans_options.SELECTION, **{**selection, "Minimum k": 1}))
    assert close(one.tables["Model metrics"].loc[1, "WSS"], 88.0)
    for seed in (1, 7, 123, 2026):
        again = run(kmeans_options.SELECTION, frame, **{**selection, "Seed": seed})
        assert int(again.tables["Selection"].loc["Suggested k", "Value"]) == 3
    sizes = run(kmeans_options.CLUSTERING, frame, **base, Clusters=3).tables
    ch.csv("csv", L["csv"], frame)
    ch.project("alab", L["alab"], {L["sheet"]: Dataset(frame, analyses=[
        (kmeans_options.CLUSTERING, opts(kmeans_options.CLUSTERING, **base, Clusters=3)),
        (kmeans_options.SELECTION, opts(kmeans_options.SELECTION, **selection, **{kmeans_options.WSS_PLOT: True})),
    ])})
    for k in (2, 3, 4):
        graph = run(kmeans_options.CLUSTERING, frame, **base, Clusters=k).figure
        ch.figure(f"groups_{k}", L["groups"].format(k=k), graph, svg=True)
    # Caso limite: ampiezza in µV, senza Standardizza.
    micro = frame.copy()
    micro[L["vars"][0]] = (micro[L["vars"][0]] * 1000).round(1)
    micro = micro.rename(columns={L["vars"][0]: L["uV"]})
    uvars = [L["uV"], L["vars"][1]]
    raw_sel = run(kmeans_options.SELECTION, micro, Variables=uvars, Standardize=False, Seed=42,
                  Criterion="Silhouette", **{"Minimum k": 2, "Maximum k": 4})
    raw_metrics = raw_sel.tables["Model metrics"]
    raw_k = int(raw_sel.tables["Selection"].loc["Suggested k", "Value"])
    assert raw_k == 2 and round(float(raw_metrics.loc[2, "Silhouette"]), 3) == .844
    assert round(float(raw_metrics.loc[3, "Silhouette"]), 3) == .787
    std_sel = run(kmeans_options.SELECTION, micro, Variables=uvars, Standardize=True, Seed=42,
                  Criterion="Silhouette", **{"Minimum k": 2, "Maximum k": 4})
    assert int(std_sel.tables["Selection"].loc["Suggested k", "Value"]) == 3
    raw3 = run(kmeans_options.CLUSTERING, micro, Variables=uvars, Standardize=False, Seed=42, Clusters=3)
    std3 = run(kmeans_options.CLUSTERING, micro, Variables=uvars, Standardize=True, Seed=42, Clusters=3)
    family = np.repeat([0, 1, 2], 15)
    misassigned = _misassigned(raw3, family)
    assert misassigned == 3 and _misassigned(std3, family) == 0
    ch.csv("csv_uV", L["csv_uV"], micro)
    ch.project("alab_uV", L["alab_uV"], {L["sheet_uV"]: Dataset(micro, analyses=[
        (kmeans_options.SELECTION, opts(kmeans_options.SELECTION, Variables=uvars, Standardize=False, Seed=42,
                                        Criterion="Silhouette", **{"Minimum k": 2, "Maximum k": 4})),
        (kmeans_options.CLUSTERING, opts(kmeans_options.CLUSTERING, Variables=uvars, Standardize=False, Seed=42,
                                         Clusters=3)),
    ])})
    ch.figure("edge_raw", L["raw"], raw3.figure)
    ch.figure("edge_std", L["std"], std3.figure)
    report = {"trama": VERSION, "data": "synthetic", "rows": len(frame), "seed": 42, "standardize": True,
              "starts": "10 k-means++ (Lloyd)",
              "metrics": {str(k): {"wss": float(metrics.loc[k, "WSS"]), "silhouette": float(metrics.loc[k, "Silhouette"])}
                          for k in (2, 3, 4)},
              "wss_k1": float(one.tables["Model metrics"].loc[1, "WSS"]), "suggested_k": suggested,
              "same_k_with_seeds": [1, 7, 123, 2026]}
    ch.json("json", L["json"], report)
    edge = {"trama": VERSION, "amplitude_unit": "µV", "standardize": False, "suggested_k": raw_k,
            "silhouette": {str(k): float(raw_metrics.loc[k, "Silhouette"]) for k in (2, 3, 4)},
            "misassigned_with_k3": misassigned,
            "suggested_k_standardized": int(std_sel.tables["Selection"].loc["Suggested k", "Value"])}
    ch.json("json_uV", L["json_uV"], edge)
    return ch, {"report": report, "edge": edge, "shots": {
        "alab": ch.data / L["alab"], "sheet": L["sheet"], "method": kmeans_options.SELECTION}}, None


def _misassigned(result, family):
    labels = result.tables["Assignments"].iloc[:, -1].to_numpy()
    wrong = 0
    for fam in range(3):
        _, counts = np.unique(labels[family == fam], return_counts=True)
        wrong += int(counts.sum() - counts.max())
    return wrong


# ---------------------------------------------------------------------------------------------------------
# ANOVA: controllo e due trattamenti, 6 unità per condizione; caso limite con repliche tecniche.
# ---------------------------------------------------------------------------------------------------------
AN = {
    "it": {"sheet": "Tre condizioni", "group": "Condizione", "resp": "Risposta (u.a.)",
           "levels": ["Controllo", "Trattamento A", "Trattamento B"], "unit": "Unità", "rep": "Replica",
           "sheet_tech": "Repliche tecniche", "csv": "tre-condizioni.csv", "alab": "esempio-anova.alab",
           "json": "risultati.json", "csv_tech": "repliche-tecniche.csv", "alab_tech": "caso-limite-repliche.alab",
           "json_tech": "caso-limite-repliche.json", "box": "condizioni-box"},
    "en": {"sheet": "Three conditions", "group": "Condition", "resp": "Response (a.u.)",
           "levels": ["Control", "Treatment A", "Treatment B"], "unit": "Unit", "rep": "Replicate",
           "sheet_tech": "Technical replicates", "csv": "three-conditions.csv", "alab": "anova-example.alab",
           "json": "results.json", "csv_tech": "technical-replicates.csv", "alab_tech": "edge-case-replicates.alab",
           "json_tech": "edge-case-replicates.json", "box": "conditions-box"},
}
OFFSETS = [(-.25, .05, .20), (.30, -.10, -.20), (-.15, -.05, .20), (.10, .20, -.30), (-.20, .25, -.05),
           (.15, -.30, .15)]


def anova_values():
    rng = np.random.default_rng(7)
    return [[round(float(v), 2) for v in rng.normal(mu, 1.0, 6)] for mu in (10.0, 12.4, 10.9)]


def anova(lang):
    L, ch = AN[lang], Chapter("anova", lang)
    values = anova_values()
    frame = pd.DataFrame([(lvl, v) for lvl, vs in zip(L["levels"], values) for v in vs],
                         columns=[L["group"], L["resp"]])
    choice = {"Response": L["resp"], "Group": L["group"], "Post-hoc": "Tukey"}
    result = run("One-way ANOVA", frame, **choice)
    table, pairs = result.tables["ANOVA"], result.tables["Multiple comparisons"]
    term = table.iloc[0]
    assert round(float(term["F"]), 2) == 31.53 and int(term["df"]) == 2 and int(table.iloc[1]["df"]) == 15
    assert float(term["p"]) < 1e-5
    c, a, b = L["levels"]
    diff = {f"{x} − {y}": pairs.loc[f"{x} − {y}"] for x, y in ((c, a), (c, b), (a, b))}
    ca, cb, ab = diff.values()
    assert round(float(ca["Difference"]), 3) == -2.973 and round(float(cb["Difference"]), 3) == -.958
    assert round(float(cb["Adjusted p"]), 4) == .0592 and round(float(ab["Adjusted p"]), 5) == .00026
    assert round(float(cb["CI 95% low"]), 3) == -1.951 and round(float(cb["CI 95% high"]), 3) == .034
    welch = run("One-way ANOVA", frame, **{**choice, "Method": "Welch", "Post-hoc": "Games–Howell"})
    welch_term = welch.tables["ANOVA"].iloc[0]
    sd = frame.groupby(L["group"], sort=False)[L["resp"]].std(ddof=1)
    assert sd.max() / sd.min() < 1.6
    graph = run("Box / violin plot", frame, Input="Single response", Response=L["resp"], Group=L["group"],
                **{"Show mean": True, "Overlay observations": True})
    box_options = opts("Box / violin plot", Input="Single response", Response=L["resp"], Group=L["group"],
                       **{"Show mean": True, "Overlay observations": True})
    # Caso limite: tre repliche tecniche per unità trattate come 54 osservazioni indipendenti.
    rows = []
    for lvl, vs in zip(L["levels"], values):
        for i, v in enumerate(vs):
            for j, d in enumerate(OFFSETS[i]):
                rows.append((lvl, f"{lvl.split()[-1][0]}{i + 1}",
                             j + 1, round(v + d, 2)))
    tech = pd.DataFrame(rows, columns=[L["group"], L["unit"], L["rep"], L["resp"]])
    pseudo = run("One-way ANOVA", tech, **choice)
    pt, pp = pseudo.tables["ANOVA"].iloc[0], pseudo.tables["Multiple comparisons"]
    assert round(float(pt["F"]), 1) == 97.0 and int(pseudo.tables["ANOVA"].iloc[1]["df"]) == 51
    assert float(pp.loc[f"{c} − {b}", "Adjusted p"]) < .001
    means = tech.groupby([L["group"], L["unit"]], sort=False)[L["resp"]].mean().round(2).to_numpy()
    assert np.allclose(means, np.concatenate(values)), "Le medie per unità devono ridare la tabella principale"
    ch.csv("csv", L["csv"], frame)
    ch.project("alab", L["alab"], {L["sheet"]: Dataset(frame, analyses=[
        ("One-way ANOVA", opts("One-way ANOVA", **choice)), ("Box / violin plot", box_options)])})
    ch.csv("csv_tech", L["csv_tech"], tech)
    ch.project("alab_tech", L["alab_tech"], {L["sheet_tech"]: Dataset(tech, analyses=[
        ("One-way ANOVA", opts("One-way ANOVA", **choice))])})
    ch.figure("box", L["box"], graph.figure, svg=True)
    report = {"trama": VERSION, "data": "synthetic", "rows": len(frame), "seed": 7,
              "group_mean": {k: float(v) for k, v in frame.groupby(L["group"], sort=False)[L["resp"]].mean().items()},
              "group_sd": {k: float(v) for k, v in sd.items()},
              "anova": {"F": float(term["F"]), "df1": int(term["df"]), "df2": int(table.iloc[1]["df"]),
                        "p": float(term["p"]), "ss_between": float(term["SS"]), "ms_residual": float(table.iloc[1]["MS"])},
              "tukey_kramer": {name: {"difference": float(r["Difference"]), "se": float(r["SE"]),
                                      "adjusted_p": float(r["Adjusted p"]), "ci95": [float(r["CI 95% low"]),
                                                                                     float(r["CI 95% high"])]}
                               for name, r in diff.items()},
              "welch": {"F": float(welch_term["F"]), "df1": float(welch_term["F df1"]),
                        "df2": float(welch_term["F df2"]), "p": float(welch_term["p"])}}
    ch.json("json", L["json"], report)
    edge = {"trama": VERSION, "rows": len(tech), "units": 18, "replicates_per_unit": 3,
            "anova": {"F": float(pt["F"]), "df1": int(pt["df"]), "df2": int(pseudo.tables["ANOVA"].iloc[1]["df"]),
                      "p": float(pt["p"])},
            "control_vs_B": {"difference": float(pp.loc[f"{c} − {b}", "Difference"]),
                             "se": float(pp.loc[f"{c} − {b}", "SE"]),
                             "adjusted_p": float(pp.loc[f"{c} − {b}", "Adjusted p"])},
            "unit_means_equal_main_table": True}
    ch.json("json_tech", L["json_tech"], edge)
    return ch, {"report": report, "edge": edge, "shots": {
        "alab": ch.data / L["alab"], "sheet": L["sheet"], "method": "One-way ANOVA"}}, None


# ---------------------------------------------------------------------------------------------------------
# Curva standard: 6 standard in doppio, 4 campioni ignoti (uno fuori campo).
# ---------------------------------------------------------------------------------------------------------
CS = {
    "it": {"sheet": "Curva standard", "x": "Concentrazione (µg/mL)", "y": "Assorbanza",
           "unk": "Campioni ignoti (assorbanza)", "csv": "curva-standard.csv", "alab": "esempio-curva-standard.alab",
           "json": "risultati.json", "fig": "curva-standard"},
    "en": {"sheet": "Standard curve", "x": "Concentration (µg/mL)", "y": "Absorbance",
           "unk": "Unknown samples (absorbance)", "csv": "standard-curve.csv", "alab": "standard-curve-example.alab",
           "json": "results.json", "fig": "standard-curve"},
}
CONC = [0, 0, 5, 5, 10, 10, 20, 20, 40, 40, 80, 80]
UNKNOWN = [.231, .478, .702, 1.120]


def curve_frame(L):
    rng = np.random.default_rng(11)
    absorb = [round(.052 + .0118 * c + rng.normal(0, .012), 3) for c in CONC]
    pad = UNKNOWN + [np.nan] * (len(CONC) - len(UNKNOWN))
    return pd.DataFrame({L["x"]: [float(c) for c in CONC], L["y"]: absorb, L["unk"]: pad})


def curve(lang):
    L, ch = CS[lang], Chapter("curva-standard", lang)
    frame = curve_frame(L)
    base = {"X": L["x"], "Y": L["y"], "Unknown responses": L["unk"]}
    out = {}
    for name in ("Prediction", "Mean response"):
        res = run("Interpolate a standard curve", frame, **base, Uncertainty=name)
        out[name] = res
    pred, mean = out["Prediction"].tables["Interpolated values"], out["Mean response"].tables["Interpolated values"]
    fit = out["Prediction"].tables["Linear calibration"]["Value"]
    assert round(float(fit["Slope"]), 6) == .011835 and round(float(fit["Intercept"]), 6) == .053271
    assert round(float(fit["R²"]), 6) == .998834
    expect = [(15.018, 12.61, 17.41, 14.30, 15.72), (35.889, 33.50, 38.29, 35.19, 36.60),
              (54.816, 52.35, 57.32, 53.87, 55.79)]
    for i, (x, plo, phi, mlo, mhi) in enumerate(expect):
        assert round(float(pred.loc[i, "Interpolated X"]), 3) == x
        assert (round(float(pred.loc[i, "X lower"]), 2), round(float(pred.loc[i, "X upper"]), 2)) == (plo, phi)
        assert (round(float(mean.loc[i, "X lower"]), 2), round(float(mean.loc[i, "X upper"]), 2)) == (mlo, mhi)
        assert not bool(pred.loc[i, "Outside calibration"])
    assert bool(pred.loc[3, "Outside calibration"]) and pd.isna(pred.loc[3, "X lower"])
    assert round(float(pred.loc[3, "Interpolated X"]), 1) == 90.1
    top = frame.loc[frame[L["x"]] == 80, L["y"]]
    ch.csv("csv", L["csv"], frame)
    ch.project("alab", L["alab"], {L["sheet"]: Dataset(frame, analyses=[
        ("Interpolate a standard curve", opts("Interpolate a standard curve", **base, Uncertainty="Prediction")),
        ("Interpolate a standard curve", opts("Interpolate a standard curve", **base, Uncertainty="Mean response")),
    ])})
    ch.figure("curve", L["fig"], out["Prediction"].figure, svg=True)
    report = {"trama": VERSION, "data": "synthetic", "seed": 11, "standards": len(frame),
              "calibration": {"slope": float(fit["Slope"]), "intercept": float(fit["Intercept"]),
                              "r2": float(fit["R²"]), "slope_se": float(fit["Slope SE"])},
              "highest_standard_response": [float(v) for v in top],
              "unknowns": [{"response": float(pred.loc[i, "Response"]), "x": float(pred.loc[i, "Interpolated X"]),
                            "outside_calibration": bool(pred.loc[i, "Outside calibration"]),
                            "prediction_interval": None if pd.isna(pred.loc[i, "X lower"]) else
                            [float(pred.loc[i, "X lower"]), float(pred.loc[i, "X upper"])],
                            "mean_response_interval": None if pd.isna(mean.loc[i, "X lower"]) else
                            [float(mean.loc[i, "X lower"]), float(mean.loc[i, "X upper"])]} for i in range(4)]}
    ch.json("json", L["json"], report)
    return ch, {"report": report, "shots": {"alab": ch.data / L["alab"], "sheet": L["sheet"],
                                             "method": "Interpolate a standard curve"}}, None


# ---------------------------------------------------------------------------------------------------------
# Colonna calcolata: segnale normalizzato sulla quantità di proteina, 8 pozzetti.
# ---------------------------------------------------------------------------------------------------------
CC = {
    "it": {"sheet": "Pozzetti", "id": "Pozzetto", "sig": "Segnale (u.a.)", "prot": "Proteina (µg)",
           "new": "Segnale per µg", "csv": "pozzetti.csv", "alab": "esempio-colonna-calcolata.alab",
           "json": "risultati.json"},
    "en": {"sheet": "Wells", "id": "Well", "sig": "Signal (a.u.)", "prot": "Protein (µg)",
           "new": "Signal per µg", "csv": "wells.csv", "alab": "calculated-column-example.alab",
           "json": "results.json"},
}
PROTEIN = [8.2, 10.5, 6.9, 12.1, 9.4, 7.6, 11.3, 9.9]


def formula_of(L):
    return f'=COL("{L["sig"]}") / COL("{L["prot"]}")'


def computed(lang):
    L, ch = CC[lang], Chapter("colonne-calcolate", lang)
    rng = np.random.default_rng(5)
    signal = [round(p * 41.5 * (1 + rng.normal(0, .03)), 1) for p in PROTEIN]
    raw = pd.DataFrame({L["id"]: [f"P{i + 1}" for i in range(8)], L["sig"]: signal, L["prot"]: PROTEIN})
    dataset = Dataset(raw, table_format="multivariable")
    dataset.set_formula(L["new"], formula_of(L))
    frame = dataset.frame()
    norm = frame[L["new"]].astype(float)
    sig = frame[L["sig"]].astype(float)
    cv = lambda v: 100 * v.std(ddof=1) / v.mean()  # noqa: E731
    assert round(cv(sig), 2) == 19.39 and round(cv(norm), 2) == 2.38
    assert round(norm.mean(), 2) == 41.18 and round(norm.std(ddof=1), 2) == .98
    summary = run("Descriptive statistics", frame, Variables=[L["sig"], L["new"]]).tables
    ch.csv("csv", L["csv"], raw)
    descriptive = opts("Descriptive statistics", Variables=[L["sig"], L["new"]])
    dataset.analyses = [("Descriptive statistics", descriptive)]
    path = ch.project("alab", L["alab"], {L["sheet"]: dataset})
    back = load_project(path)[L["sheet"]]
    assert back.formulas == {L["new"]: formula_of(L)}
    assert np.allclose(back.frame()[L["new"]].astype(float), norm)
    # Caso limite: una cella esclusa nella colonna di origine lascia vuota la cella calcolata.
    excluded = load_project(path)[L["sheet"]]
    excluded.excluded = [(2, 2)]
    after = excluded.frame()[L["new"]]
    assert pd.isna(after.iloc[2]) and after.count() == 7 and round(float(after.mean()), 4) == 41.1798
    masked = run("Descriptive statistics", excluded.frame(mask_excluded=True), Variables=[L["sig"], L["new"]])
    summary_after = masked.tables["Summary"].loc[L["new"]]
    assert int(summary_after["N"]) == 7 and int(summary_after["Missing"]) == 1
    try:  # Senza COL("…") un nome con spazi e parentesi non è accettato.
        load_project(path)[L["sheet"]].set_formula("x", f'={L["sig"]} / {L["prot"]}')
        raise AssertionError("formula senza COL accettata")
    except ValueError:
        pass
    edited = load_project(path)[L["sheet"]]
    edited.raw.iat[0, 1] = 400.0
    assert round(float(edited.frame()[L["new"]].iloc[0]), 2) == 48.78
    stats = summary[next(iter(summary))]
    report = {"trama": VERSION, "data": "synthetic", "seed": 5, "rows": 8, "formula": formula_of(L),
              "signal": {"mean": float(sig.mean()), "sd": float(sig.std(ddof=1)), "cv_percent": float(cv(sig))},
              "normalized": {"mean": float(norm.mean()), "sd": float(norm.std(ddof=1)), "cv_percent": float(cv(norm)),
                             "values": [float(v) for v in norm]},
              "after_excluding_protein_P3": {"n": int(after.count()), "mean": float(after.mean())},
              "after_editing_signal_P1_to_400": float(edited.frame()[L["new"]].iloc[0]),
              "reopened_formula_identical": True,
              "descriptive_rows": [str(i) for i in stats.index]}
    ch.json("json", L["json"], report)
    return ch, {"report": report, "shots": {"alab": path, "sheet": L["sheet"], "formula": L["new"]}}, None


# ---------------------------------------------------------------------------------------------------------
# Export vettoriale: layout a due pannelli (curva e residui) esportato in SVG e PDF da Trama.
# ---------------------------------------------------------------------------------------------------------
EX = {
    "it": {"layout": "Figura 1", "alab": "esempio-layout.alab", "json": "risultati.json",
           "svg_text": "figura-1-testo.svg", "svg_paths": "figura-1-tracciati.svg", "pdf": "figura-1.pdf",
           "png": "figura-1-anteprima", "alab_small": "caso-limite-caratteri-predefiniti.alab",
           "svg_small": "caso-limite-caratteri-predefiniti.svg", "png_small": "caso-limite-caratteri-predefiniti"},
    "en": {"layout": "Figure 1", "alab": "layout-example.alab", "json": "results.json",
           "svg_text": "figure-1-text.svg", "svg_paths": "figure-1-paths.svg", "pdf": "figure-1.pdf",
           "png": "figure-1-preview", "alab_small": "edge-case-default-fonts.alab",
           "svg_small": "edge-case-default-fonts.svg", "png_small": "edge-case-default-fonts"},
}
# Caratteri dei grafici (Formato grafico → Dimensioni dei caratteri in punti) leggibili a 170 mm in due colonne.
READABLE = {"title_size": 22, "label_size": 20, "tick_size": 18}


def fixed_pdf_id(path):
    """Il salvataggio del PDF mette un /ID casuale: lo sostituisco con l'MD5 del file senza ID (stessa lunghezza)."""
    import hashlib
    import re
    data = path.read_bytes()
    match = re.search(rb"/ID\s*\[\s*<([0-9A-Fa-f]{32})>\s*<([0-9A-Fa-f]{32})>\s*\]", data)
    if match:
        blank = data[:match.start(1)] + b"0" * 32 + data[match.end(1):match.start(2)] + b"0" * 32 + data[match.end(2):]
        digest = hashlib.md5(blank).hexdigest().upper().encode()
        path.write_bytes(data[:match.start(1)] + digest + data[match.end(1):match.start(2)] + digest + data[match.end(2):])


def export_chapter(lang):
    L, C, ch = EX[lang], CS[lang], Chapter("esportazione", lang)
    frame = curve_frame(C)[[C["x"], C["y"]]]
    fit = opts("Linear regression", X=C["x"], Y=C["y"], Band="Confidence (mean)", Graph="Fit")
    residuals = opts("Linear regression", X=C["x"], Y=C["y"], Graph="Residuals vs fitted")
    layout = Layout(L["layout"], 2, [(C["sheet"], 0), (C["sheet"], 1)])
    analyses = [("Linear regression", fit), ("Linear regression", residuals)]
    path = ch.project("alab", L["alab"], {C["sheet"]: Dataset(
        frame, analyses=analyses, graph_styles={0: dict(READABLE), 1: dict(READABLE)})}, layouts=[layout])
    small = ch.project("alab_small", L["alab_small"], {C["sheet"]: Dataset(frame, analyses=analyses)},
                       layouts=[layout])
    return ch, {"shots": {"alab": path, "alab_small": small, "sheet": C["sheet"], "layout": L}}, layout


def text_sizes(path, width_mm):
    """Corpo effettivo in punti di ogni testo dell'SVG stampato a ``width_mm``: pagina e pannelli."""
    import re
    import xml.etree.ElementTree as ET
    root = ET.parse(path).getroot()
    base = width_mm / 25.4 * 72 / float(root.get("viewBox").split()[2])
    sizes = {"page": [], "panels": []}

    def walk(node, scale, where):
        found = re.search(r"scale\(([\d.]+)", node.get("transform") or "")
        scale *= float(found.group(1)) if found else 1.0
        if (node.get("id") or "").startswith("panel"):
            where = "panels"
        if node.tag.endswith("}text"):
            size = float(re.search(r"font-size: ([\d.]+)px", node.get("style")).group(1))
            sizes[where].append(round(size * scale * base, 2))
        for child in node:
            walk(child, scale, where)

    walk(root, 1.0, "page")
    return {k: [min(v), max(v)] for k, v in sizes.items()}


def export_files(ch, window, lang):
    """Esporta il layout come fa File → Esporta con opzioni… e controlla SVG e PDF."""
    import re
    import pypdfium2 as pdfium
    L = EX[lang]
    project = window.project
    layout = project.layouts[0]
    width = 170.0
    text_svg, path_svg, pdf = ch.fig / L["svg_text"], ch.fig / L["svg_paths"], ch.fig / L["pdf"]
    project.export_layout(layout, text_svg, {"format": "svg", "svg_text": "text", "width_mm": width,
                                             "transparent": False})
    project.export_layout(layout, path_svg, {"format": "svg", "svg_text": "paths", "width_mm": width,
                                             "transparent": False})
    project.export_layout(layout, pdf, {"format": "pdf", "width_mm": width, "transparent": False})
    fixed_pdf_id(pdf)
    project.export_layout(layout, ch.fig / f"{L['png']}.png", {"format": "png", "dpi": 110, "width_mm": width,
                                                               "transparent": False})
    for key, item in (("svg_text", text_svg), ("svg_paths", path_svg), ("pdf", pdf), ("png", ch.fig / f"{L['png']}.png")):
        ch.add(key, item)
    tsvg, psvg = text_svg.read_text(encoding="utf-8"), path_svg.read_text(encoding="utf-8")
    n_text, n_text_paths = len(re.findall(r"<text\b", tsvg)), len(re.findall(r"<text\b", psvg))
    images = len(re.findall(r"<image\b", tsvg)) + len(re.findall(r"<image\b", psvg))
    letters = re.findall(r">\s*([AB])\s*<", tsvg)
    size = re.search(r'<svg[^>]*\bwidth="([\d.]+)mm"[^>]*\bheight="([\d.]+)mm"', tsvg)
    assert n_text > 20 and n_text_paths == 0 and images == 0, (n_text, n_text_paths, images)
    assert set(letters) >= {"A", "B"}, letters
    width_mm, height_mm = float(size.group(1)), float(size.group(2))
    assert abs(width_mm - width) < .5, width_mm
    document = pdfium.PdfDocument(str(pdf))
    page = document[0]
    pdf_w, pdf_h = (v * 25.4 / 72 for v in page.get_size())
    pdf_text = page.get_textpage().get_text_range()
    pdf_images = sum(1 for obj in page.get_objects() if obj.type == pdfium.raw.FPDF_PAGEOBJ_IMAGE)
    assert len(document) == 1 and abs(pdf_w - width) < .5 and pdf_images == 0
    fonts = text_sizes(text_svg, width)
    assert fonts["panels"][0] >= 7.0, fonts
    report = {"trama": VERSION, "layout": layout.name, "columns": layout.columns, "panels": len(layout.panels),
              "width_mm": width,
              "svg_text": {"bytes": text_svg.stat().st_size, "text_elements": n_text, "embedded_images": 0,
                           "page_mm": [round(width_mm, 1), round(height_mm, 1)]},
              "svg_paths": {"bytes": path_svg.stat().st_size, "text_elements": n_text_paths, "embedded_images": 0},
              "pdf": {"bytes": pdf.stat().st_size, "pages": len(document), "page_mm": [round(pdf_w, 1), round(pdf_h, 1)],
                      "embedded_images": pdf_images, "searchable_text": bool(pdf_text.strip()),
                      "panel_letters_in_text": sorted(set(re.findall(r"\b[AB]\b", pdf_text)))},
              "graph_font_sizes": READABLE, "effective_text_pt": fonts}
    document.close()
    return report


def export_edge(ch, window, lang, report, app, settle):
    """Caso limite: lo stesso layout con i caratteri predefiniti dei grafici, esportato a 170 mm."""
    L = EX[lang]
    window.open_path(ch.data / L["alab_small"])
    settle()
    window.open_sheet(("layout", 0))
    settle()
    project = window.project
    assert Path(project.path).name == L["alab_small"], project.path
    layout = project.layouts[0]
    svg, png = ch.fig / L["svg_small"], ch.fig / f"{L['png_small']}.png"
    project.export_layout(layout, svg, {"format": "svg", "svg_text": "text", "width_mm": 170.0, "transparent": False})
    project.export_layout(layout, png, {"format": "png", "dpi": 110, "width_mm": 170.0, "transparent": False})
    ch.add("svg_small", svg)
    ch.add("png_small", png)
    fonts = text_sizes(svg, 170.0)
    assert fonts["panels"][1] < 5.0, fonts
    report["edge_default_fonts"] = {"effective_text_pt": fonts}
    ch.json("json", L["json"], report)
    return report


# ---------------------------------------------------------------------------------------------------------
# Schermate dell'app: tema chiaro, finestra 1280 × 800, come si apre il progetto allegato.
# ---------------------------------------------------------------------------------------------------------
def screenshots(slug, ch, info, lang, app):
    from PySide6.QtWidgets import QTabWidget
    from trama_qt.analysis_dialog import AnalysisDialog
    from trama_qt.window import MainWindow

    shots = info["shots"]
    window = MainWindow()
    window.resize(1280, 800)
    window.show()
    app.processEvents()
    window.open_path(shots["alab"])

    def settle(seconds=60):
        end = time.monotonic() + seconds
        while window.job is not None and time.monotonic() < end:
            app.processEvents()
            time.sleep(.03)
        for _ in range(15):
            app.processEvents()
        assert window.job is None, "calcolo non terminato"

    def save(key, widget, name):
        path = ch.app / f"{name}.png"
        assert widget.grab().save(str(path))
        ch.add(key, path)

    def dialog_for(index, tab=1, size=(960, 680)):
        run_ = window.project.runs[index]
        window.open_sheet(("data", shots["sheet"]))
        settle()
        _, frame = window._analysis_input()
        dialog = AnalysisDialog(window, frame, current=(run_.method, dict(run_.options)))
        dialog.resize(*size)
        dialog.show()
        for _ in range(20):
            app.processEvents()
        for tabs in dialog.findChildren(QTabWidget):
            if tabs.count() >= 2:
                tabs.setCurrentIndex(tab)
        for _ in range(20):
            app.processEvents()
        return dialog

    settle()
    for index, item in enumerate(window.project.runs):
        assert item.result is not None or item.calculation_error is None, (index, item.method)
    names = {"it": {"dialog": "dialogo-opzioni", "results": "risultati", "graph": "grafico", "sheet": "foglio",
                    "formula": "dialogo-formula", "layout": "layout", "export": "dialogo-esporta"},
             "en": {"dialog": "options-dialog", "results": "results", "graph": "graph", "sheet": "sheet",
                    "formula": "formula-dialog", "layout": "layout", "export": "export-dialog"}}[lang]
    extra = None
    if slug in {"k-means", "anova", "curva-standard"}:
        index = next(i for i, r in enumerate(window.project.runs) if r.method == shots["method"])
        dialog = dialog_for(index)
        save("app_dialog", dialog, names["dialog"])
        dialog.reject()
        window.open_sheet(("result", index))
        settle()
        if slug == "anova":  # I confronti di Tukey sono nella seconda scheda dei risultati.
            from PySide6.QtWidgets import QTabBar
            for bar in window.findChildren(QTabBar):
                labels = [bar.tabText(i) for i in range(bar.count())]
                if "Multiple comparisons" in labels:
                    bar.setCurrentIndex(labels.index("Multiple comparisons"))
            for _ in range(20):
                app.processEvents()
        save("app_results", window, names["results"])
        if slug == "curva-standard":
            window.open_sheet(("graph", index))
            settle()
            save("app_graph", window, names["graph"])
    elif slug == "colonne-calcolate":
        from trama_qt.formula import FormulaDialog
        window.open_sheet(("data", shots["sheet"]))
        settle()
        save("app_sheet", window, names["sheet"])
        dataset = window.project.tables[shots["sheet"]]
        dialog = FormulaDialog(window, dataset, shots["formula"])
        dialog.show()
        for _ in range(20):
            app.processEvents()
        save("app_formula", dialog, names["formula"])
        dialog.reject()
    elif slug == "esportazione":
        from analisi.layout_geometry import page_size
        from trama_qt import export_options
        from trama_qt.export_options import ExportOptionsDialog
        window.open_sheet(("layout", 0))
        settle()
        save("app_layout", window, names["layout"])
        layout = window.project.layouts[0]
        export_options.SESSION.clear()
        export_options.SESSION.update({"preset": "Custom", "format": "svg", "width_mm": 170.0, "svg_text": "text",
                                       "transparent": False, "dpi": 300})
        figure = window.project.layout_figure(layout)
        dialog = ExportOptionsDialog(window, tuple(figure.get_size_inches()),
                                     layout_size=page_size(layout.columns, len(layout.panels), layout.paper))
        dialog.show()
        for _ in range(20):
            app.processEvents()
        save("app_export", dialog, names["export"])
        dialog.reject()
        extra = export_edge(ch, window, lang, export_files(ch, window, lang), app, settle)
    window.worker.shutdown()
    window.close()
    return extra


CHAPTERS = {"k-means": kmeans, "anova": anova, "curva-standard": curve, "colonne-calcolate": computed,
            "esportazione": export_chapter}


def main(argv):
    only = [a for a in argv if not a.startswith("--")] or list(CHAPTERS)
    with_app = "--senza-app" not in argv
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    app = None
    if with_app:
        from PySide6.QtWidgets import QApplication
        from trama_qt import theme
        app = QApplication.instance() or QApplication([])
        theme.load_fonts()
        theme.STATE["mode"] = "light"
        theme.apply(app, dark=False)
    reports = {}
    for slug in only:
        for lang in ("it", "en"):
            set_language(lang)
            ch, info, _ = CHAPTERS[slug](lang)
            if with_app:
                extra = screenshots(slug, ch, info, lang, app)
                if extra is not None:
                    info["report"] = extra
            # Le due lingue devono dare gli stessi numeri.
            numbers = json.dumps(info.get("report"), sort_keys=True, ensure_ascii=False)
            reports.setdefault(slug, {})[lang] = numbers
            old = manifest.get(slug, {}).get(lang, {})
            if not with_app:  # senza schermate nuove restano quelle già fatte
                ch.files.update({k: v for k, v in old.items() if k.startswith("app_") and k not in ch.files})
            manifest.setdefault(slug, {})[lang] = ch.files
            print(f"ok {slug} {lang}: {len(ch.files)} file")
    for slug, by_lang in reports.items():
        if slug in {"k-means", "anova", "curva-standard"}:
            a, b = (json.loads(by_lang[x]) for x in ("it", "en"))
            for key in ("group_mean", "group_sd", "tukey_kramer"):
                a.pop(key, None), b.pop(key, None)
            assert a == b, f"{slug}: numeri diversi fra IT ed EN"
    manifest["_trama"] = VERSION
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    if app is not None:
        app.quit()


if __name__ == "__main__":
    with tempfile.TemporaryDirectory():
        main(sys.argv[1:])
