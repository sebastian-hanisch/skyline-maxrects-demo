"""Kennzahlen, Verdikt-Logik und das Messraster (vorberechnet in smx_precomputed.json, erzeugt von generate_precomputed.py)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import smx_algorithm as A
import smx_constants as C
from smx_scenario import Instance, mess_seed, quelle_instanz, zufallsinstanz

PRECOMPUTED = Path(__file__).resolve().parent / "smx_precomputed.json"
SCHLUESSEL_LISTE = tuple(sorted(C.SCHLUESSEL))
VERFAHREN_LISTE = tuple(sorted(C.VERFAHREN))
SCHLUESSEL_FLAECHE, SCHLUESSEL_HOEHE = 2, 1
REGAL, SKYLINE, BSSF = 0, 1, 2


@dataclass(frozen=True)
class Settings:
    quelle: int = 0
    n_index: int = 0
    seed: int = C.DEFAULT_SEED
    schluessel: int = 1
    verfahren: int = 0
    schritt: int = 0            # 0 = alle Rechtecke, sonst der Zwischenstand nach so vielen Rechtecken


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    order: tuple          # alle Teilenummern in der Reihenfolge, in der gepackt wird
    schritt: int          # Zahl der gesetzten Rechtecke im gezeigten Zustand (1 bis n; bei n = 0: 0)
    bins: tuple           # Behälter (Teilenummern) im gezeigten Zustand
    platz: tuple          # Platzierungen im gezeigten Zustand
    zustand: tuple        # Regale, Höhenprofile oder freie Rechtecke je Behälter im gezeigten Zustand
    count: int            # Behälterzahl der ganzen Packung (alle Rechtecke)
    liefer: int           # Behälterzahl in Lieferreihenfolge mit demselben Verfahren
    schranke: int
    opt: object           # Optimum (int) bei den Handbeispielen, sonst None
    tabelle: tuple        # tabelle[schluessel][verfahren] = Behälterzahl, 4 x 5
    settings: Settings


def tabelle(inst: Instance) -> tuple:
    """Behälterzahl für jede Kombination aus Schlüssel (Zeile) und Verfahren (Spalte)."""
    return tuple(tuple(A.anzahl(inst.rects, k, v, inst.cap) for v in VERFAHREN_LISTE) for k in SCHLUESSEL_LISTE)


def wirksamer_schritt(settings: Settings, n: int) -> int:
    """Zahl der gezeigten Schritte: 0 oder mehr als n bedeutet alle Rechtecke."""
    return n if settings.schritt <= 0 or settings.schritt > n else settings.schritt


def analyse(s: Settings) -> Analysis:
    inst = quelle_instanz(s.quelle, C.N_WERTE[s.n_index], s.seed)
    order = A.reihenfolge(inst.rects, s.schluessel)
    schritt = wirksamer_schritt(s, inst.n)
    bins_voll, platz_voll, _ = A.pack(inst.rects, order, inst.cap, s.verfahren)
    assert A.packung_pruefen(inst.rects, platz_voll, inst.cap)
    bins, platz, zustand = A.pack(inst.rects, order[:schritt], inst.cap, s.verfahren)
    assert A.packung_pruefen(inst.rects, platz, inst.cap, vollstaendig=False)
    tab = tabelle(inst)
    return Analysis(inst, tuple(order), schritt, tuple(tuple(b) for b in bins), tuple(platz), tuple(zustand), len(bins_voll), tab[0][s.verfahren], A.schranke(inst.rects, inst.cap),
                    C.BEISPIEL_OPTIMUM.get(s.quelle), tab, s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def beste_schluessel(tab: tuple, verfahren: int) -> list:
    """Schlüssel mit der kleinsten Behälterzahl in der Spalte des Verfahrens."""
    spalte = [tab[k][verfahren] for k in SCHLUESSEL_LISTE]
    return [k for k in SCHLUESSEL_LISTE if tab[k][verfahren] == min(spalte)]


def verdict_aktuell(a: Analysis) -> tuple[str, str]:
    """Verdikt zur gewählten Kombination: Behälterzahl der ganzen Packung gegen die Lieferreihenfolge (gleiches Verfahren), gegen das Optimum, wo es bekannt ist, und gegen den besten Schlüssel."""
    s = a.settings
    schluessel = C.SCHLUESSEL_MIT[s.schluessel]
    verfahren = C.VERFAHREN_KURZ[s.verfahren]
    if a.opt is None:
        opt_teil = f" Das Optimum ist für diese Instanz nicht berechnet; die Schranke ist {a.schranke}."
    elif a.count == a.opt:
        opt_teil = f" Das ist das Optimum (die Schranke allein ergäbe {a.schranke})."
    else:
        opt_teil = f" Das Optimum ist **{a.opt}**: {a.count - a.opt} zu viel (die Schranke ist {a.schranke})."
    beste = beste_schluessel(a.tabelle, s.verfahren)
    bester = a.tabelle[beste[0]][s.verfahren]
    if a.count == bester:
        passt = " Für dieses Verfahren ist das einer der besten Schlüssel dieser Instanz."
    else:
        passt = f" Für dieses Verfahren ist in der Tabelle {' oder '.join(C.SCHLUESSEL_KURZ[k] for k in beste)} besser ({bester})."
    if s.schluessel == 0:
        return "info", f"In der Lieferreihenfolge brauchen die Rechtecke mit {verfahren} **{a.count}** Behälter." + opt_teil + passt
    kopf = f"Nach {schluessel} sortiert und mit {verfahren} gesetzt brauchen die Rechtecke **{a.count}** Behälter, in Lieferreihenfolge {a.liefer}."
    if a.count > a.liefer:
        return "warning", kopf + f" Sortieren schadet hier um {a.count - a.liefer}." + opt_teil + passt
    if a.count < a.liefer:
        return "success", kopf + f" Sortieren spart hier {a.liefer - a.count}." + opt_teil + passt
    return "info", kopf + " Sortieren ändert hier nichts." + opt_teil + passt


def spannen(t: tuple) -> tuple[int, int]:
    """(verfahren, schluessel) der 4 x 5 Tabelle: größter Unterschied zwischen den Verfahren innerhalb einer Zeile; größter Unterschied zwischen den Schlüsseln innerhalb einer Spalte."""
    verfahren = max(max(z) - min(z) for z in t)
    schluessel = max(max(t[k][v] for k in range(len(t))) - min(t[k][v] for k in range(len(t))) for v in range(len(t[0])))
    return verfahren, schluessel


def verdict_tabelle(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Was verändert die Behälterzahl mehr, das Verfahren oder der Schlüssel? Gezählt über die ganze 4 x 5 Tabelle dieser Instanz."""
    verfahren, schluessel = spannen(a.tabelle)
    teil = (f"Zwischen den fünf Verfahren unterscheidet sich die Behälterzahl bei gleichem Schlüssel um bis zu **{verfahren}**; "
            f"zwischen den vier Schlüsseln bei gleichem Verfahren um bis zu **{schluessel}**.")
    if verfahren > schluessel:
        return "success", teil + " Hier zählt das Verfahren mehr als der Schlüssel."
    if verfahren == schluessel:
        return "info", teil + " Beide wirken hier gleich stark."
    return "warning", teil + " Hier zählt der Schlüssel mehr als das Verfahren."


# ------------------------------------------------------------------------------------------------------------------------------------------
# Messraster


def messzelle(verteilung: int, n_index: int, opt: list | None = None) -> dict:
    """Rechnet eine Zelle des Messrasters frisch: Summen (ganze Zahlen, damit der Vergleich exakt ist) über INSTANZEN feste Instanzen.

    ueber_schranke[k][v] = Summe über alle Instanzen von (Behälter mit Schlüssel k und Verfahren v minus Schranke). regal_hoehe_gegen_maxrects_flaeche und skyline_flaeche_gegen_maxrects_flaeche: [besser,
    gleich, schlechter] = Zahl der Instanzen, in denen MaxRects BSSF mit Fläche weniger, gleich viele, mehr Behälter braucht als das Regal mit Höhe (erste Zahl: MaxRects besser) beziehungsweise Skyline
    mit Fläche weniger, gleich viele, mehr als MaxRects BSSF mit Fläche (erste Zahl: Skyline besser). gross_ueber_flaeche: Zahl der Instanzen, in denen die Schranke „große Rechtecke“ über der
    Flächenschranke liegt. Mit `opt` (Optimum je Instanz, -1 = nicht entschieden) zusätzlich, nur über die entschiedenen Instanzen: ueber_opt[k][v], trifft_opt[k][v] (Zahl der Instanzen mit Behälter
    gleich Optimum), opt_minus_schranke (Summe), opt_ueber_schranke (Zahl der Instanzen mit Optimum über der Schranke) und entschieden."""
    n = C.MESS_N[n_index]
    ks = [str(k) for k in SCHLUESSEL_LISTE]
    vs = [str(v) for v in VERFAHREN_LISTE]
    out = {"ueber_schranke": {k: dict.fromkeys(vs, 0) for k in ks}, "mr_flaeche_gegen_regal_hoehe": [0, 0, 0], "skyline_flaeche_gegen_mr_flaeche": [0, 0, 0], "gross_ueber_flaeche": 0}
    if opt is not None:
        out.update({"entschieden": 0, "ueber_opt": {k: dict.fromkeys(vs, 0) for k in ks}, "trifft_opt": {k: dict.fromkeys(vs, 0) for k in ks}, "opt_minus_schranke": 0, "opt_ueber_schranke": 0})
    for j in range(C.INSTANZEN):
        inst = zufallsinstanz(verteilung, n, mess_seed(verteilung, n_index, j))
        flaeche, gross, s = A.schranken(inst.rects, inst.cap)
        t = tabelle(inst)
        out["gross_ueber_flaeche"] += gross > flaeche
        for k in SCHLUESSEL_LISTE:
            for v in VERFAHREN_LISTE:
                out["ueber_schranke"][str(k)][str(v)] += t[k][v] - s
        mr, rg, sk = t[SCHLUESSEL_FLAECHE][BSSF], t[SCHLUESSEL_HOEHE][REGAL], t[SCHLUESSEL_FLAECHE][SKYLINE]
        out["mr_flaeche_gegen_regal_hoehe"][0 if mr < rg else 1 if mr == rg else 2] += 1
        out["skyline_flaeche_gegen_mr_flaeche"][0 if sk < mr else 1 if sk == mr else 2] += 1
        if opt is not None and opt[j] >= 0:
            out["entschieden"] += 1
            out["opt_minus_schranke"] += opt[j] - s
            out["opt_ueber_schranke"] += opt[j] > s
            for k in SCHLUESSEL_LISTE:
                for v in VERFAHREN_LISTE:
                    out["ueber_opt"][str(k)][str(v)] += t[k][v] - opt[j]
                    out["trifft_opt"][str(k)][str(v)] += t[k][v] == opt[j]
    return out


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zelle_schluessel(verteilung: int, n_index: int) -> str:
    return f"{C.VERTEILUNGEN[verteilung][0]}|{C.MESS_N[n_index]}"


def zeile(verteilung: int, n_index: int, daten: dict | None = None) -> dict:
    """Mittelwerte und Anteile einer Zelle aus den vorberechneten Summen."""
    daten = daten or vorberechnet()
    z = daten["zellen"][zelle_schluessel(verteilung, n_index)]
    k = daten["instanzen"]
    exakt = "entschieden" in z
    e = z.get("entschieden", 0)

    def tab(summen, nenner):
        return {s: {v: summen[str(s)][str(v)] / nenner for v in VERFAHREN_LISTE} for s in SCHLUESSEL_LISTE}

    return {
        "verteilung": verteilung,
        "name": C.VERTEILUNG_LANG[verteilung],
        "n": C.MESS_N[n_index],
        "instanzen": k,
        "exakt": exakt,
        "entschieden": e,
        "offen": (k - e) if exakt else 0,
        "mittel_schranke": tab(z["ueber_schranke"], k),
        "mittel_opt": tab(z["ueber_opt"], e) if exakt and e else None,
        "anteil_opt": {s: {v: 100.0 * z["trifft_opt"][str(s)][str(v)] / e for v in VERFAHREN_LISTE} for s in SCHLUESSEL_LISTE} if exakt and e else None,
        "opt_minus_schranke": z["opt_minus_schranke"] / e if exakt and e else None,
        "opt_ueber_schranke": z.get("opt_ueber_schranke", 0),
        "mr_gegen_regal": tuple(z["mr_flaeche_gegen_regal_hoehe"]),
        "skyline_gegen_mr": tuple(z["skyline_flaeche_gegen_mr_flaeche"]),
        "gross_ueber_flaeche": z["gross_ueber_flaeche"],
    }


def referenz(z: dict) -> tuple[str, dict]:
    """(Name der Vergleichsbasis, Mittel je Schlüssel und Verfahren): das Optimum, wo es für mindestens eine Instanz der Zelle bekannt ist, sonst die Schranke."""
    if z["exakt"] and z["entschieden"]:
        return "dem Optimum", z["mittel_opt"]
    return "der Schranke", z["mittel_schranke"]


def gerundet(m: dict) -> dict:
    return {k: {v: round(m[k][v], 2) for v in VERFAHREN_LISTE} for k in SCHLUESSEL_LISTE}


def beste_schluessel_zelle(g: dict, verfahren: int) -> list:
    """Schlüssel mit dem kleinsten (auf zwei Stellen gerundeten) Mittel für das Verfahren."""
    kleinster = min(g[k][verfahren] for k in SCHLUESSEL_LISTE)
    return [k for k in SCHLUESSEL_LISTE if g[k][verfahren] == kleinster]


def verdict_messung(z: dict) -> tuple[str, str]:
    """Verdikt zur gewählten Zelle: bester Schlüssel je Verfahren; Regal mit Höhe gegen die freien Verfahren mit Höhe und gegen MaxRects BSSF mit Fläche. Auf zwei Stellen gerundet verglichen."""
    basis, m = referenz(z)
    g = gerundet(m)
    n_inst = z["entschieden"] if basis == "dem Optimum" else z["instanzen"]
    teile = []
    for v in VERFAHREN_LISTE:
        teile.append(f"{C.VERFAHREN_KURZ[v]} {' und '.join(C.SCHLUESSEL_KURZ[k] for k in beste_schluessel_zelle(g, v))}")
    kopf = (f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} ist der beste Schlüssel je Verfahren (Mittel über {basis}, {n_inst} Instanzen): " + ", ".join(teile) + ".")
    zahlen = (f" Regal mit Höhe {g[SCHLUESSEL_HOEHE][REGAL]:.2f}; Skyline mit Höhe {g[SCHLUESSEL_HOEHE][SKYLINE]:.2f}, mit Fläche {g[SCHLUESSEL_FLAECHE][SKYLINE]:.2f}; "
              f"MaxRects BSSF mit Höhe {g[SCHLUESSEL_HOEHE][BSSF]:.2f}, mit Fläche {g[SCHLUESSEL_FLAECHE][BSSF]:.2f}.")
    fuss = ""
    if basis == "dem Optimum" and z["offen"]:
        fuss += f" {z['offen']} von {z['instanzen']} Instanzen sind nicht entschieden und fehlen im Mittel."
    if basis == "der Schranke":
        fuss += " Bei dieser Rechteckzahl fehlt das Optimum und die Schranke ist locker: Lesen Sie nur die Unterschiede zwischen den Kombinationen, nicht den Abstand."
    regal = g[SCHLUESSEL_HOEHE][REGAL]
    if all(regal < g[SCHLUESSEL_HOEHE][v] for v in (1, 2, 3, 4)):
        return "warning", kopf + zahlen + " Mit der Höhe sortiert ist das **Regal besser als jede freie Platzierung**." + fuss
    return "info", kopf + zahlen + fuss


def verdict_instanz(z: dict) -> tuple[str, str]:
    """Verdikt zu Experiment 2: Instanz für Instanz MaxRects BSSF mit Fläche gegen das Regal mit Höhe, und Skyline mit Fläche gegen MaxRects BSSF mit Fläche."""
    b, g, s = z["mr_gegen_regal"]
    sb, sg, ss = z["skyline_gegen_mr"]
    teil = (f"Von {z['instanzen']} Instanzen braucht MaxRects BSSF mit Fläche in **{b}** weniger Behälter als das Regal mit Höhe, in {g} gleich viele und in {s} mehr. "
            f"Skyline mit Fläche braucht gegenüber MaxRects BSSF mit Fläche in {sb} weniger, in {sg} gleich viele und in **{ss}** mehr.")
    if b > s:
        return "success", teil + " MaxRects mit Fläche ist hier das bessere Verfahren."
    if b == s:
        return "info", teil + " Beide Kombinationen sind hier gleich gut."
    return "warning", teil + " Hier ist das Regal mit Höhe besser."


def optimum_zeilen(daten: dict | None = None) -> list:
    """Experiment 2: für alle Zellen mit Optimum (n = 12 und 20, vier Verteilungen): Anteil der Instanzen, in denen Regal mit Höhe, Skyline mit Fläche und MaxRects BSSF mit Fläche das Optimum treffen."""
    zeilen = []
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            if n in C.EXAKT_N:
                z = zeile(v, ni, daten)
                t = z["anteil_opt"]
                zeilen.append({"verteilung": v, "n": n, "entschieden": z["entschieden"], "offen": z["offen"], "instanzen": z["instanzen"],
                               "regal": None if t is None else t[SCHLUESSEL_HOEHE][REGAL], "skyline": None if t is None else t[SCHLUESSEL_FLAECHE][SKYLINE],
                               "maxrects": None if t is None else t[SCHLUESSEL_FLAECHE][BSSF]})
    return zeilen


def verdict_optimum(zeilen: list) -> tuple[str, str]:
    """Verdikt zu Experiment 2: in welcher Zelle MaxRects BSSF mit Fläche das Optimum am seltensten und in welcher am häufigsten trifft (auf ganze Prozent gerundet)."""
    gueltig = [z for z in zeilen if z["maxrects"] is not None]
    if not gueltig:
        return "info", "Es gibt keine Zelle mit bekanntem Optimum."
    selten = min(gueltig, key=lambda z: (round(z["maxrects"]), z["n"], z["verteilung"]))
    haeufig = max(gueltig, key=lambda z: (round(z["maxrects"]), -z["n"], -z["verteilung"]))
    return "info", (f"MaxRects BSSF mit Fläche trifft das Optimum am seltensten bei {C.VERTEILUNG_DAT[selten['verteilung']]} mit n = {selten['n']} ({selten['maxrects']:.0f} % der {selten['entschieden']} "
                    f"entschiedenen Instanzen, Regal mit Höhe {selten['regal']:.0f} %, Skyline mit Fläche {selten['skyline']:.0f} %) und am häufigsten bei {C.VERTEILUNG_DAT[haeufig['verteilung']]} "
                    f"mit n = {haeufig['n']} ({haeufig['maxrects']:.0f} % der {haeufig['entschieden']} entschiedenen Instanzen).")
