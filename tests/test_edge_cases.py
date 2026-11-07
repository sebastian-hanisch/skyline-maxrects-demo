"""Randfälle: leere Eingabe, ein Rechteck, Rechteck gleich Behälter, genau passende Plätze, Gleichstände, Schritte, ungültige Eingaben."""

import pytest

import smx_algorithm as A
import smx_constants as C
from smx_scenario import Instance, mess_seed, zufallsinstanz

VERFAHREN = range(5)


@pytest.mark.parametrize("verfahren", VERFAHREN)
def test_leere_eingabe_ergibt_keine_behaelter(verfahren):
    assert A.pack((), [], 10, verfahren) == ([], [], [])
    assert A.schranken((), 10) == (0, 0, 0)


@pytest.mark.parametrize("verfahren", VERFAHREN)
def test_ein_rechteck_und_rechteck_gleich_behaelter(verfahren):
    bins, platz, _ = A.pack(((7, 3),), [0], 10, verfahren)
    assert bins == [[0]] and platz == [(0, 0, 0, 0)]
    bins, platz, _ = A.pack(((10, 10), (1, 1)), [0, 1], 10, verfahren)
    assert bins == [[0], [1]] and platz == [(0, 0, 0, 0), (1, 1, 0, 0)]


@pytest.mark.parametrize("verfahren", VERFAHREN)
def test_vier_gleiche_rechtecke_fuellen_den_behaelter_genau(verfahren):
    bins, platz, _ = A.pack(((5, 5), (5, 5), (5, 5), (5, 5)), [0, 1, 2, 3], 10, verfahren)
    assert bins == [[0, 1, 2, 3]] and sorted(platz) == [(0, 0, 0, 0), (1, 0, 5, 0), (2, 0, 0, 5), (3, 0, 5, 5)]


@pytest.mark.parametrize("verfahren", VERFAHREN)
def test_kein_platz_oeffnet_einen_neuen_behaelter(verfahren):
    # zwei Rechtecke der Höhe 6 und 5 passen nicht übereinander (11 > 10), und nebeneinander nicht (10 + 10 > 10)
    bins, _, _ = A.pack(((10, 6), (10, 5)), [0, 1], 10, verfahren)
    assert bins == [[0], [1]]


def test_skyline_verliert_den_hohlraum_unter_einem_ueberhang():
    # Von Hand: (6, 4) -> (0, 0); (4, 8) -> (6, 0) (niedrigste Stelle); (8, 2): überall liegt Höhe 8 unter einer Breite von 8, also (0, 8) bis zur Oberkante 10.
    # Der Raum (0 bis 6, 4 bis 8) unter dem Überhang ist für Skyline verloren, das letzte Rechteck (6, 4) passt nirgends: zwei Behälter.
    # MaxRects kennt den Raum als freies Rechteck (0, 4, 6, 4) und setzt (6, 4) dorthin: ein Behälter.
    rects = ((6, 4), (4, 8), (8, 2), (6, 4))
    sky = A.pack(rects, [0, 1, 2, 3], 10, 1)
    mr = A.pack(rects, [0, 1, 2, 3], 10, 2)
    assert len(sky[0]) == 2 and len(mr[0]) == 1
    assert (3, 0, 0, 4) in mr[1]


def test_maxrects_liefert_nie_ueberlappende_freie_rechtecke_ueber_platzierten():
    rects = ((6, 4), (4, 8), (8, 2), (6, 4))
    _, platz, zustand = A.pack(rects, [0, 1, 2, 3], 10, 2)
    for fx, fy, fw, fh in zustand[0]:
        for i, b, x, y in platz:
            w, h = rects[i]
            assert not (x < fx + fw and fx < x + w and y < fy + fh and fy < y + h)


@pytest.mark.parametrize("verfahren", VERFAHREN)
def test_anfang_der_reihenfolge_ist_der_anfang_der_packung(verfahren):
    rects = ((6, 4), (5, 3), (4, 5), (4, 2), (3, 3), (7, 2))
    order = [2, 0, 5, 1, 4, 3]
    voll = A.pack(rects, order, 10, verfahren)
    for k in range(len(order) + 1):
        teil = A.pack(rects, order[:k], 10, verfahren)
        assert teil[1] == voll[1][:k]


def test_gleichstand_beim_sortieren_haelt_die_lieferreihenfolge():
    assert A.reihenfolge(((3, 4), (5, 4), (2, 4)), 1) == [0, 1, 2]
    assert A.reihenfolge(((3, 4), (5, 4), (2, 4)), 3) == [1, 0, 2]
    assert A.reihenfolge(((2, 6), (3, 4), (4, 3)), 2) == [0, 1, 2]       # Flächen 12 und 12 und 12: Lieferreihenfolge


def test_schranke_nimmt_das_groessere_von_flaeche_und_grossen_rechtecken():
    assert A.schranken(((51, 51), (51, 51), (51, 51)), 100) == (1, 3, 3)
    assert A.schranken(((50, 50), (50, 50), (50, 50), (50, 50)), 100) == (1, 0, 1)      # genau die Hälfte ist nicht „über die Hälfte“
    assert A.schranken(((100, 100), (1, 1)), 100) == (2, 1, 2)


def test_ungueltige_eingaben_werfen():
    with pytest.raises(ValueError):
        A.pack(((11, 1),), [0], 10, 0)         # Breite größer als der Behälter
    with pytest.raises(ValueError):
        A.pack(((1, 11),), [0], 10, 1)         # Höhe größer als der Behälter
    with pytest.raises(ValueError):
        A.pack(((0, 1),), [0], 10, 2)          # Maß null
    with pytest.raises(ValueError):
        A.pack(((3, 4), (2, 2)), [0, 0], 10, 0)    # Rechteck doppelt
    with pytest.raises(ValueError):
        A.pack(((3, 4), (2, 2)), [0, 5], 10, 0)    # Nummer außerhalb
    with pytest.raises(ValueError):
        A.pack(((3, 4),), [0], 10, 7)              # unbekanntes Verfahren
    with pytest.raises(ValueError):
        A.reihenfolge(((3, 4),), 9)                # unbekannter Schlüssel
    with pytest.raises(ValueError):
        Instance(((3, 4),), 0)
    with pytest.raises(ValueError):
        Instance(((3, 11),), 10)


def test_zufallsinstanz_ist_deterministisch_und_haelt_die_bereiche():
    for v, (_, _, (wl, wh), (hl, hh)) in enumerate(C.VERTEILUNGEN):
        inst = zufallsinstanz(v, 50, 123)
        assert inst == zufallsinstanz(v, 50, 123) and inst != zufallsinstanz(v, 50, 124)
        assert all(wl <= w <= wh and hl <= h <= hh for w, h in inst.rects)
    assert mess_seed(0, 0, 0) == 1_001_000 and mess_seed(3, 3, 99) == 4_004_099
