"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 10 Sekunden.

  Skyline                      gegen  eine Umsetzung, die das Höhenprofil jedes Mal NEU aus der Liste der gesetzten Rechtecke liest (keine laufende Spaltenliste).
  MaxRects (BSSF, BAF, BL)     gegen  eine Umsetzung, die in jedem Schritt ALLE maximalen leeren Rechtecke nach Definition aus einem Belegungsraster aufzählt (kleine Behälter, Kante 12 bis 16).
  Freie Rechtecke              gegen  das Belegungsraster: ihre Vereinigung ist genau die leere Fläche, sie sind maximal und enthalten kein gesetztes Rechteck (nach jedem Schritt).
  Regal                        gegen  die zweite Umsetzung aus Stück 7 in Form einer naiven Neuberechnung (Belegung jedes Mal aus den Listen summiert).
  Optimum (aus Stück 7)        gegen  CP-SAT, in tests/test_claims.py (Stichprobe).
  Eigenschaften:  gemeinsames Skalieren, Eingabereihenfolge bei sortierten Schlüsseln ohne Gleichstand, Zustand ist der Anfang der Packung, Fläche der gesetzten Rechtecke höchstens Behälterfläche.
"""

import random

import pytest

import smx_algorithm as A


def instanzen(anzahl, n_lo, n_hi, cap_lo=10, cap_hi=40, seed0=0):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        yield cap, tuple((rng.randint(1, cap), rng.randint(1, cap)) for _ in range(n))


# --- Skyline: das Profil wird jedes Mal aus den gesetzten Rechtecken gelesen -------------------------------------------------------------------------


def skyline_naiv(rects, order, cap):
    gesetzt = []                                   # je Behälter: Liste (x, y, w, h)
    platz = []
    for i in order:
        w, h = rects[i]
        wahl = None
        for b, lst in enumerate(gesetzt):
            def hoehe(x):
                return max([y + hh for (xx, y, ww, hh) in lst if xx < x + 1 and x < xx + ww] + [0])      # Höhe über der Spalte x (Spalte = Intervall [x, x + 1))
            kandidaten = [(max(hoehe(c) for c in range(x, x + w)), x) for x in range(cap - w + 1)]
            kandidaten = [(y, x) for y, x in kandidaten if y + h <= cap]
            if kandidaten:
                y, x = min(kandidaten)
                wahl = (b, x, y)
                break
        if wahl is None:
            gesetzt.append([])
            wahl = (len(gesetzt) - 1, 0, 0)
        b, x, y = wahl
        gesetzt[b].append((x, y, w, h))
        platz.append((i, b, x, y))
    return platz


def test_skyline_gegen_das_profil_aus_der_liste():
    for cap, rects in instanzen(40, 1, 14, cap_lo=8, cap_hi=40, seed0=100):
        for schluessel in (0, 1, 2):
            order = A.reihenfolge(rects, schluessel)
            assert A.pack(rects, order, cap, 1)[1] == skyline_naiv(rects, order, cap), (cap, rects, schluessel)


# --- MaxRects: alle maximalen leeren Rechtecke aus einem Belegungsraster ---------------------------------------------------------------------------


def belegung(gesetzt, cap):
    return [[any(x <= c < x + w and y <= r < y + h for (x, y, w, h) in gesetzt) for c in range(cap)] for r in range(cap)]       # raster[reihe][spalte]


def maximale_leere(gesetzt, cap):
    """Alle maximalen leeren Rechtecke (x, y, w, h) nach Definition: leer und in keiner der vier Richtungen um eine Zelle erweiterbar."""
    raster = belegung(gesetzt, cap)

    def leer(x, y, w, h):
        return all(not raster[r][c] for r in range(y, y + h) for c in range(x, x + w))

    gefunden = []
    for x in range(cap):
        for y in range(cap):
            for w in range(1, cap - x + 1):
                for h in range(1, cap - y + 1):
                    if not leer(x, y, w, h):
                        break
                    links = x > 0 and leer(x - 1, y, 1, h)
                    rechts = x + w < cap and leer(x + w, y, 1, h)
                    unten = y > 0 and leer(x, y - 1, w, 1)
                    oben = y + h < cap and leer(x, y + h, w, 1)
                    if not (links or rechts or unten or oben):
                        gefunden.append((x, y, w, h))
    return gefunden


def maxrects_naiv(rects, order, cap, regel):
    gesetzt = []                                   # je Behälter
    platz = []
    for i in order:
        w, h = rects[i]
        wahl = None
        for b, lst in enumerate(gesetzt):
            for (fx, fy, fw, fh) in maximale_leere(lst, cap):
                if w <= fw and h <= fh:
                    kurz, lang = min(fw - w, fh - h), max(fw - w, fh - h)
                    score = (kurz, lang, fy, fx) if regel == "bssf" else (fw * fh, kurz, fy, fx) if regel == "baf" else (fy + h, fx, kurz, lang)
                    if wahl is None or score < wahl[0]:
                        wahl = (score, b, fx, fy)
            if wahl is not None:
                break
        if wahl is None:
            gesetzt.append([])
            wahl = (None, len(gesetzt) - 1, 0, 0)
        _, b, x, y = wahl
        gesetzt[b].append((x, y, w, h))
        platz.append((i, b, x, y))
    return platz


@pytest.mark.parametrize("verfahren,regel", [(2, "bssf"), (3, "baf"), (4, "bl")])
def test_maxrects_gegen_die_aufzaehlung_aller_maximalen_leeren_rechtecke(verfahren, regel):
    for cap, rects in instanzen(14, 1, 9, cap_lo=10, cap_hi=14, seed0=500):
        for schluessel in (0, 2):
            order = A.reihenfolge(rects, schluessel)
            assert A.pack(rects, order, cap, verfahren)[1] == maxrects_naiv(rects, order, cap, regel), (cap, rects, schluessel, regel)


def test_freie_rechtecke_sind_nach_jedem_schritt_genau_die_maximalen_leeren_rechtecke():
    for cap, rects in instanzen(12, 1, 8, cap_lo=10, cap_hi=14, seed0=700):
        order = A.reihenfolge(rects, 2)
        for k in range(len(order) + 1):
            bins, platz, zustand = A.pack(rects, order[:k], cap, 2)
            for b, frei in enumerate(zustand):
                gesetzt = [(x, y, rects[i][0], rects[i][1]) for i, bb, x, y in platz if bb == b]
                assert sorted(frei) == sorted(maximale_leere(gesetzt, cap)), (cap, rects, k, b)


def test_vereinigung_der_freien_rechtecke_ist_die_leere_flaeche():
    for cap, rects in instanzen(12, 1, 8, cap_lo=10, cap_hi=14, seed0=900):
        order = A.reihenfolge(rects, 1)
        bins, platz, zustand = A.pack(rects, order, cap, 4)
        for b, frei in enumerate(zustand):
            gesetzt = [(x, y, rects[i][0], rects[i][1]) for i, bb, x, y in platz if bb == b]
            raster = belegung(gesetzt, cap)
            for r in range(cap):
                for c in range(cap):
                    in_frei = any(fx <= c < fx + fw and fy <= r < fy + fh for fx, fy, fw, fh in frei)
                    assert in_frei == (not raster[r][c]), (cap, rects, b, r, c)


# --- Regal: naive Neuberechnung ----------------------------------------------------------------------------------------------------------------


def regal_naiv(rects, order, cap):
    behaelter = []                                   # je Behälter: Liste von Regalen {"y": ..., "teile": [...]}
    for i in order:
        w, h = rects[i]
        platziert = False
        for b in range(len(behaelter)):
            for sh in behaelter[b]:
                hoehe = rects[sh["teile"][0]][1]
                belegt = sum(rects[t][0] for t in sh["teile"])
                if h <= hoehe and belegt + w <= cap:
                    sh["teile"].append(i)
                    platziert = True
                    break
            if platziert:
                break
        if platziert:
            continue
        for b in range(len(behaelter)):
            oben = sum(rects[sh["teile"][0]][1] for sh in behaelter[b])
            if oben + h <= cap:
                behaelter[b].append({"teile": [i]})
                platziert = True
                break
        if not platziert:
            behaelter.append([{"teile": [i]}])
    return [[t for sh in b for t in sh["teile"]] for b in behaelter]


def test_regal_gegen_die_naive_zweitumsetzung():
    for cap, rects in instanzen(40, 1, 25, cap_lo=10, cap_hi=100, seed0=300):
        for schluessel in range(4):
            order = A.reihenfolge(rects, schluessel)
            bins, platz, _ = A.pack(rects, order, cap, 0)
            assert sorted(sorted(b) for b in bins) == sorted(sorted(b) for b in regal_naiv(rects, order, cap)), (cap, rects, schluessel)


# --- Eigenschaften -----------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("verfahren", range(5))
def test_alle_packungen_sind_zulaessig_und_nie_unter_der_schranke(verfahren):
    for cap, rects in instanzen(40, 1, 25, cap_lo=10, cap_hi=100, seed0=1000):
        for schluessel in range(4):
            order = A.reihenfolge(rects, schluessel)
            bins, platz, _ = A.pack(rects, order, cap, verfahren)
            assert A.packung_pruefen(rects, platz, cap) and len(bins) >= A.schranke(rects, cap), (cap, rects, schluessel)
            for b in bins:
                assert sum(rects[i][0] * rects[i][1] for i in b) <= cap * cap


@pytest.mark.parametrize("verfahren", range(5))
def test_gemeinsames_skalieren_aendert_die_behaelterzahl_nicht(verfahren):
    for cap, rects in instanzen(25, 1, 12, cap_lo=10, cap_hi=30, seed0=1300):
        gross = tuple((3 * w, 3 * h) for w, h in rects)
        for k in range(4):
            assert A.anzahl(gross, k, verfahren, 3 * cap) == A.anzahl(rects, k, verfahren, cap), (cap, rects, k)


def test_eingabereihenfolge_aendert_die_sortierten_schluessel_ohne_gleichstand_nicht():
    rng = random.Random(1500)
    geprueft = 0
    for cap, rects in instanzen(60, 2, 15, cap_lo=60, cap_hi=300, seed0=1500):
        gemischt = list(rects)
        rng.shuffle(gemischt)
        for k in range(1, 4):
            if len(set(A.schluessel_wert(rects, k))) < len(rects):
                continue
            geprueft += 1
            for v in range(5):
                a = A.pack(rects, A.reihenfolge(rects, k), cap, v)[1]
                b = A.pack(tuple(gemischt), A.reihenfolge(tuple(gemischt), k), cap, v)[1]
                lage = lambda rs, pl: sorted((rs[i], bb, x, y) for i, bb, x, y in pl)    # noqa: E731
                assert lage(rects, a) == lage(tuple(gemischt), b), (cap, rects, k, v)
    assert geprueft >= 100            # der Test prüft wirklich etwas
