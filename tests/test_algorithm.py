"""Kern an der Mini-Instanz von Hand und an den Handbeispielen der App (DEMO-PLAYBOOK §1b).

Handrechnung Mini-Instanz (Behälter 10 mal 10; Rechtecke 0: (6, 4), 1: (5, 3), 2: (4, 5), 3: (4, 2); Fläche 69, Schranke 1), Lieferreihenfolge:
  Regal (erstes passendes): 0 -> Regal 0 (Höhe 4, Breite 6); 1 -> 6 + 5 > 10, neues Regal 1 bei y = 4 (Höhe 3); 2 (4, 5) -> Regal 0 und 1 zu niedrig, neues Regal bei y = 7: 7 + 5 > 10, neuer Behälter;
      3 (4, 2) -> Regal 0 (6 + 4 = 10).                                                                                          => [[0, 1, 3], [2]]
  Skyline: 0 -> (0, 0), Profil 4 über den Spalten 0 bis 5. 1 (5, 3): jede Stelle hat Höhe 4 (die Spalten 0 bis 5 sind 4), links zuerst: (0, 4), Profil 7 über 0 bis 4, Spalte 5 hat 4.
      2 (4, 5): niedrigste Stelle ist die Spalte 6 mit Höhe 0 (x = 6, Breite 4 bis Spalte 9): (6, 0), Profil 5 über 6 bis 9. 3 (4, 2): kleinste Höhe unter einer Breite 4 ist 5 bei x = 5 (Spalten 5 bis 8:
      4, 5, 5, 5): (5, 5); die Spalte 5 hat darunter einen Hohlraum der Höhe 1, der verloren ist.                                    => [[0, 1, 2, 3]], Plätze (0,0), (0,4), (6,0), (5,5)
  MaxRects BSSF: frei [(0,0,10,10)]. 0 -> (0, 0); frei [(6,0,4,10), (0,4,10,6)]. 1 (5, 3): nur (0,4,10,6) passt -> (0, 4); frei [(6,0,4,10), (5,4,5,6), (0,7,10,3)].
      2 (4, 5): (6,0,4,10) passt mit Restkanten (0, 5), (5,4,5,6) mit (1, 1): kleinste kurze Kante gewinnt, also (6, 0); frei [(5,4,1,6), (5,5,5,5), (0,7,10,3)] (das Teil (6,5,4,5) liegt in (5,5,5,5)).
      3 (4, 2): (5,5,5,5) mit Restkanten (1, 3), (0,7,10,3) mit (1, 6): (5, 5).                                                     => [[0, 1, 2, 3]]
  MaxRects BAF: wie BSSF bis zum dritten Rechteck; 2 (4, 5): (6,0,4,10) hat Fläche 40, (5,4,5,6) hat 30, also (5, 4); 3 (4, 2): frei [(9,0,1,10), (6,0,4,4), (0,7,5,3), (0,9,10,1)], Flächen 16 und 15 passen:
      (0, 7).                                                                                                                         => Plätze (0,0), (0,4), (5,4), (0,7)
  MaxRects BL: gleiche Plätze wie BSSF (die untere Kante entscheidet für (6, 0) und (5, 5)).
"""

import pytest

import smx_algorithm as A
import smx_constants as C
import smx_evaluation as ev
from smx_scenario import beispiel


def _pack(inst, schluessel, verfahren):
    return A.pack(inst.rects, A.reihenfolge(inst.rects, schluessel), inst.cap, verfahren)


def test_regal_auf_der_mini_instanz(mini):
    bins, platz, zustand = _pack(mini, 0, 0)
    assert bins == [[0, 1, 3], [2]]
    assert sorted(platz) == [(0, 0, 0, 0), (1, 0, 0, 4), (2, 1, 0, 0), (3, 0, 6, 0)]
    assert zustand == [[[0, 4, 10], [4, 3, 5]], [[0, 5, 4]]]


def test_skyline_auf_der_mini_instanz(mini):
    bins, platz, zustand = _pack(mini, 0, 1)
    assert bins == [[0, 1, 2, 3]]
    assert sorted(platz) == [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 0), (3, 0, 5, 5)]
    assert zustand == [[7] * 9 + [5]]          # Spalten 0 bis 4 durch Rechteck 1, 5 bis 8 durch Rechteck 3 (Höhe 7), Spalte 9 nur durch Rechteck 2 (Höhe 5)


def test_maxrects_bssf_auf_der_mini_instanz_mit_den_freien_rechtecken(mini):
    bins, platz, zustand = _pack(mini, 0, 2)
    assert bins == [[0, 1, 2, 3]] and sorted(platz) == [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 0), (3, 0, 5, 5)]
    # Schritt für Schritt: der Zustand nach k Rechtecken ist der Zustand des Anfangs der Reihenfolge
    assert A.pack(mini.rects, [0], 10, 2)[2] == [[(6, 0, 4, 10), (0, 4, 10, 6)]]
    assert A.pack(mini.rects, [0, 1], 10, 2)[2] == [[(6, 0, 4, 10), (5, 4, 5, 6), (0, 7, 10, 3)]]
    assert A.pack(mini.rects, [0, 1, 2], 10, 2)[2] == [[(5, 4, 1, 6), (5, 5, 5, 5), (0, 7, 10, 3)]]


def test_maxrects_baf_und_bl_auf_der_mini_instanz(mini):
    assert sorted(_pack(mini, 0, 3)[1]) == [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 5, 4), (3, 0, 0, 7)]
    assert A.pack(mini.rects, [0, 1, 2], 10, 3)[2] == [[(9, 0, 1, 10), (6, 0, 4, 4), (0, 7, 5, 3), (0, 9, 10, 1)]]
    assert sorted(_pack(mini, 0, 4)[1]) == [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 0), (3, 0, 5, 5)]


def test_skyline_zustand_nach_zwei_schritten(mini):
    assert A.pack(mini.rects, [0, 1], 10, 1)[2] == [[7, 7, 7, 7, 7, 4, 0, 0, 0, 0]]
    assert A.pack(mini.rects, [0, 1, 2], 10, 1)[2] == [[7, 7, 7, 7, 7, 4, 5, 5, 5, 5]]


def test_schranke_der_mini_instanz(mini):
    assert A.schranken(mini.rects, mini.cap) == (1, 0, 1)
    assert A.schranken(((60, 60), (55, 70), (30, 30)), 100) == (1, 2, 2)


# --- Beispiel 1: die ersten Schritte von Hand ----------------------------------------------------------------------------------------------------


def test_beispiel_1_reihenfolge_nach_flaeche():
    """Flächen: Teil 10 (56, 60) = 3360, Teil 0 (43, 57) = 2451, Teil 9 (47, 50) = 2350, Teil 11 (46, 51) = 2346, Teil 1 (41, 57) = 2337, Teil 2 (50, 43) = 2150, Teil 6 (48, 40) = 1920,
    Teil 3 (27, 59) = 1593, Teil 4 (56, 24) = 1344, Teil 5 (29, 39) = 1131, Teil 8 (20, 51) = 1020, Teil 7 (32, 25) = 800."""
    assert A.reihenfolge(beispiel(0).rects, 2) == [10, 0, 9, 11, 1, 2, 6, 3, 4, 5, 8, 7]


def test_beispiel_1_maxrects_bssf_nach_flaeche_erste_schritte():
    """Von Hand: Teil 10 (56, 60) -> (0, 0), frei [(56,0,44,100), (0,60,100,40)]. Teil 0 (43, 57): nur (56,0,44,100) passt (Höhe 57 > 40 oben) -> (56, 0), frei [(99,0,1,100), (56,57,44,43), (0,60,100,40)].
    Teil 9 (47, 50) passt in keines (47 > 44, 50 > 40): neuer Behälter."""
    rects = beispiel(0).rects
    order = A.reihenfolge(rects, 2)
    assert A.pack(rects, order[:1], 100, 2)[2] == [[(56, 0, 44, 100), (0, 60, 100, 40)]]
    bins, platz, zustand = A.pack(rects, order[:2], 100, 2)
    assert bins == [[10, 0]] and sorted(platz) == [(0, 0, 56, 0), (10, 0, 0, 0)]
    assert zustand == [[(99, 0, 1, 100), (56, 57, 44, 43), (0, 60, 100, 40)]]
    bins, platz, zustand = A.pack(rects, order[:3], 100, 2)
    assert bins == [[10, 0], [9]] and sorted(platz)[-1] == (10, 0, 0, 0) and (9, 1, 0, 0) in platz


def test_beispiel_1_skyline_nach_flaeche_erste_schritte():
    """Von Hand: Teil 10 (56, 60) -> (0, 0), Profil 60 über den Spalten 0 bis 55. Teil 0 (43, 57): unter jeder Breite 43 ab Spalte 0 bis 55 liegt Höhe 60; ab Spalte 56 bis 99 ist es 0: x = 56 -> (56, 0),
    Profil 57 über 56 bis 98."""
    rects = beispiel(0).rects
    order = A.reihenfolge(rects, 2)
    prof = A.pack(rects, order[:2], 100, 1)[2][0]
    assert prof == [60] * 56 + [57] * 43 + [0] and sorted(A.pack(rects, order[:2], 100, 1)[1]) == [(0, 0, 56, 0), (10, 0, 0, 0)]


# --- die Handbeispiele der App (Phase-0-Rechnung, in den Tests nachgerechnet) -----------------------------------------------------------------------


def test_beispiele_zwanzig_kombinationen_der_phase_0():
    erwartet = {0: [[5, 4, 5, 5], [4, 4, 3, 3], [5, 4, 3, 3], [5, 4, 3, 3], [4, 4, 3, 3]],       # je Verfahren (Regal, Skyline, BSSF, BAF, BL): Lieferung, Höhe, Fläche, Breite
                1: [[3, 3, 4, 3], [3, 3, 3, 3], [3, 3, 2, 3], [3, 3, 3, 3], [3, 3, 3, 3]]}
    # die Tabelle oben ist nach Verfahren 0 (Regal), 1 (Skyline), 2 (BSSF), 3 (BAF), 4 (BL) geordnet; Beispiel 1: Regal 5 4 5 5, Skyline 4 4 3 3, BSSF 5 4 3 3, BAF 5 4 3 3, BL 4 4 3 3
    for b, soll in erwartet.items():
        inst = beispiel(b)
        for v, zeile in enumerate(soll):
            assert [A.anzahl(inst.rects, k, v, inst.cap) for k in range(4)] == zeile, (b, v)
    assert [A.schranke(beispiel(b).rects, C.CAP) for b in (0, 1)] == [3, 2] and C.BEISPIEL_OPTIMUM == {0: 3, 1: 2}


def test_beispiel_2_nur_eine_kombination_findet_das_optimum():
    inst = beispiel(1)
    kombis = [(k, v) for k in range(4) for v in range(5) if A.anzahl(inst.rects, k, v, inst.cap) == 2]
    assert kombis == [(2, 2)]


def test_alle_ergebnisse_der_beispiele_sind_zulaessige_packungen():
    for b in (0, 1):
        inst = beispiel(b)
        for k in C.SCHLUESSEL:
            for v in C.VERFAHREN:
                bins, platz, _ = _pack(inst, k, v)
                assert A.packung_pruefen(inst.rects, platz, inst.cap) and sorted(i for bb in bins for i in bb) == list(range(inst.n)), (b, k, v)


def test_packungspruefer_erkennt_fehler():
    rects = ((6, 4), (5, 3), (4, 2))
    ok = [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 0)]
    assert A.packung_pruefen(rects, ok, 10)
    assert not A.packung_pruefen(rects, [(0, 0, 0, 0), (1, 0, 5, 0), (2, 0, 6, 4)], 10)     # (0) und (1) überlappen
    assert not A.packung_pruefen(rects, [(0, 0, 5, 0), (1, 0, 0, 4), (2, 0, 6, 5)], 10)     # Rechteck 0 ragt über den Rand (5 + 6 > 10)
    assert A.packung_pruefen(rects, [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 8)], 10)         # 8 + 2 = 10: genau am oberen Rand, gültig
    assert not A.packung_pruefen(rects, [(0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 6, 9)], 10)     # 9 + 2 = 11
    assert not A.packung_pruefen(rects, ok[:2], 10)                                           # Rechteck 2 fehlt
    assert A.packung_pruefen(rects, ok[:2], 10, vollstaendig=False)                           # Anfang einer Packung ist erlaubt
    assert not A.packung_pruefen(rects, ok + [(2, 0, 0, 7)], 10, vollstaendig=False)         # Rechteck 2 doppelt
    assert A.packung_pruefen(rects, [(0, 0, 0, 0), (1, 1, 0, 0), (2, 1, 5, 0)], 10)         # zwei Behälter, kein Konflikt


@pytest.mark.parametrize("verfahren", range(5))
def test_analyse_stimmt_mit_dem_kern_ueberein(verfahren):
    a = ev.analyse(ev.Settings(0, 0, 7, 2, verfahren, 5))
    assert a.count == A.anzahl(a.inst.rects, 2, verfahren, a.inst.cap) and a.schritt == 5 and sum(len(b) for b in a.bins) == 5 and len(a.platz) == 5
    assert a.liefer == A.anzahl(a.inst.rects, 0, verfahren, a.inst.cap) and a.opt == 3 and a.schranke == 3
    assert ev.analyse(ev.Settings(0, 0, 7, 2, verfahren, 0)).schritt == 12 == ev.analyse(ev.Settings(0, 0, 7, 2, verfahren, 999)).schritt
