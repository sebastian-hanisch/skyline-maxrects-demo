"""Verdikte (reine Funktionen in smx_evaluation.py) an von Hand gesetzten Werten: jede Schwelle und jede Zahl im Text steht hier (DEMO-PLAYBOOK §12).

Die Analysen und Zellen werden von Hand gebaut, nicht aus Seeds gerechnet."""

import pytest

import smx_constants as C
import smx_evaluation as ev
from smx_scenario import Instance

GLEICH = tuple(tuple(5 for _ in range(5)) for _ in range(4))


def _analyse(schluessel, verfahren, count, liefer, schranke, opt, tabelle=GLEICH):
    return ev.Analysis(Instance(((5, 5),), 10), (0,), 1, ((0,),), ((0, 0, 0, 0),), (), count, liefer, schranke, opt, tabelle, ev.Settings(0, 0, 7, schluessel, verfahren, 0))


def _tab(spalten):
    """Tabelle 4 x 5 aus fünf Spalten (je Verfahren vier Werte für Lieferung, Höhe, Fläche, Breite)."""
    return tuple(tuple(spalten[v][k] for v in range(5)) for k in range(4))


# --- beste_schluessel und verdict_aktuell --------------------------------------------------------------------------------------------------


def test_beste_schluessel_nennt_alle_gleich_guten():
    t = _tab([(5, 4, 5, 4), (4, 4, 3, 3), (5, 4, 3, 3), (3, 3, 3, 3), (4, 4, 4, 4)])
    assert ev.beste_schluessel(t, 0) == [1, 3] and ev.beste_schluessel(t, 1) == [2, 3] and ev.beste_schluessel(t, 3) == [0, 1, 2, 3] and ev.beste_schluessel(t, 2) == [2, 3]


def test_aktuell_schadet_ist_eine_warnung_und_nennt_den_besseren_schluessel():
    t = _tab([(4, 3, 5, 4), (4, 4, 4, 4), (4, 4, 4, 4), (4, 4, 4, 4), (4, 4, 4, 4)])
    kind, text = ev.verdict_aktuell(_analyse(2, 0, 5, 4, 3, 3, t))
    assert kind == "warning"
    assert "Nach der Fläche sortiert und mit Regal gesetzt brauchen die Rechtecke **5** Behälter, in Lieferreihenfolge 4." in text
    assert "Sortieren schadet hier um 1." in text and "Das Optimum ist **3**: 2 zu viel (die Schranke ist 3)." in text
    assert "Für dieses Verfahren ist in der Tabelle Höhe besser (3)." in text


def test_aktuell_spart_ist_ein_erfolg_und_nennt_das_optimum():
    t = _tab([(5, 4, 5, 5), (4, 4, 4, 4), (4, 4, 4, 4), (4, 4, 4, 4), (4, 4, 4, 4)])
    kind, text = ev.verdict_aktuell(_analyse(1, 0, 4, 5, 3, 4, t))
    assert kind == "success" and "Nach der Höhe sortiert und mit Regal gesetzt brauchen die Rechtecke **4** Behälter, in Lieferreihenfolge 5." in text
    assert "Sortieren spart hier 1." in text and "Das ist das Optimum (die Schranke allein ergäbe 3)." in text and "Für dieses Verfahren ist das einer der besten Schlüssel dieser Instanz." in text


def test_aktuell_gleich_ist_info_und_nennt_mehrere_bessere_schluessel():
    t = tuple(tuple(3 if (k, v) in ((1, 2), (3, 2)) else 4 for v in range(5)) for k in range(4))
    kind, text = ev.verdict_aktuell(_analyse(2, 2, 4, 4, 2, 3, t))
    assert kind == "info" and "Sortieren ändert hier nichts." in text and "Sortieren schadet" not in text and "Sortieren spart" not in text
    assert "Für dieses Verfahren ist in der Tabelle Höhe oder Breite besser (3)." in text and "Das Optimum ist **3**: 1 zu viel (die Schranke ist 2)." in text


def test_aktuell_ohne_optimum_nennt_die_schranke():
    kind, text = ev.verdict_aktuell(_analyse(1, 1, 9, 11, 6, None))
    assert kind == "success" and "Sortieren spart hier 2." in text and "mit Skyline gesetzt" in text
    assert "Das Optimum ist für diese Instanz nicht berechnet; die Schranke ist 6." in text


def test_aktuell_lieferreihenfolge_ist_info_ohne_vergleich():
    kind, text = ev.verdict_aktuell(_analyse(0, 3, 4, 4, 4, 4))
    assert kind == "info" and "In der Lieferreihenfolge brauchen die Rechtecke mit BAF **4** Behälter." in text and "Sortieren schadet" not in text


@pytest.mark.parametrize("verfahren,name", [(0, "Regal"), (1, "Skyline"), (2, "BSSF"), (3, "BAF"), (4, "BL")])
def test_aktuell_nennt_das_verfahren(verfahren, name):
    assert f"mit {name} gesetzt" in ev.verdict_aktuell(_analyse(1, verfahren, 5, 4, 4, 4))[1]


# --- spannen und verdict_tabelle -----------------------------------------------------------------------------------------------------------


def test_spannen_verfahren_und_schluessel():
    t = _tab([(5, 4, 5, 5), (4, 4, 3, 3), (5, 4, 3, 3), (5, 4, 3, 3), (4, 4, 3, 3)])      # Beispiel 1 der Demo
    assert ev.spannen(t) == (2, 2)       # Verfahren: Zeile Fläche (5, 3, 3, 3, 3) -> 2, Zeile Lieferung (5, 4, 5, 5, 4) -> 1; Schlüssel: Spalte Regal (5 bis 4) -> 1, Spalte BSSF (5 bis 3) -> 2


def test_verdict_tabelle_verfahren_staerker_ist_erfolg():
    t = tuple((9, 3, 3, 3, 3) for _ in range(4))
    assert ev.spannen(t) == (6, 0)
    kind, text = ev.verdict_tabelle(_analyse(1, 0, 9, 9, 3, 3, t))
    assert kind == "success" and "bis zu **6**" in text and "bis zu **0**" in text and "Hier zählt das Verfahren mehr als der Schlüssel." in text


def test_verdict_tabelle_gleich_stark_ist_info():
    t = tuple(tuple(5 if (k, v) == (0, 0) else 4 for v in range(5)) for k in range(4))
    assert ev.spannen(t) == (1, 1)
    kind, text = ev.verdict_tabelle(_analyse(1, 0, 4, 4, 4, 4, t))
    assert kind == "info" and "Beide wirken hier gleich stark." in text


def test_verdict_tabelle_schluessel_staerker_ist_warnung():
    t = ((3, 3, 3, 3, 3), (8, 8, 8, 8, 8), (3, 3, 3, 3, 3), (3, 3, 3, 3, 3))
    assert ev.spannen(t) == (0, 5)
    kind, text = ev.verdict_tabelle(_analyse(1, 0, 8, 8, 3, 3, t))
    assert kind == "warning" and "bis zu **0**" in text and "bis zu **5**" in text and "Hier zählt der Schlüssel mehr als das Verfahren." in text


# --- referenz, verdict_messung -------------------------------------------------------------------------------------------------------------


def _zelle(tab, verteilung=0, n=40, exakt=False, entschieden=0, instanzen=100, mr=(16, 73, 11), sk=(0, 56, 44)):
    return {"verteilung": verteilung, "name": C.VERTEILUNG_LANG[verteilung], "n": n, "instanzen": instanzen, "exakt": exakt, "entschieden": entschieden,
            "offen": (instanzen - entschieden) if exakt else 0, "mittel_schranke": tab, "mittel_opt": tab if exakt and entschieden else None, "anteil_opt": None,
            "opt_minus_schranke": None, "opt_ueber_schranke": 0, "mr_gegen_regal": mr, "skyline_gegen_mr": sk, "gross_ueber_flaeche": 0}


def _mittel(spalten):
    return {k: {v: spalten[v][k] for v in range(5)} for k in range(4)}


# Mittel je Verfahren (Regal, Skyline, BSSF, BAF, BL) und Schlüssel (Lieferung, Höhe, Fläche, Breite): mittlere Rechtecke, n = 80, wie in der Phase 0
MITTEL_80 = _mittel([(6.04, 1.95, 3.64, 5.90), (3.92, 2.47, 2.34, 3.31), (3.40, 2.09, 1.90, 2.13), (3.53, 2.19, 1.99, 2.21), (3.49, 2.14, 1.96, 2.25)])
MITTEL_FREI_GUT = _mittel([(1.50, 0.90, 1.20, 1.40), (1.00, 0.80, 0.70, 0.90), (0.80, 0.70, 0.50, 0.80), (0.90, 0.75, 0.55, 0.85), (0.85, 0.72, 0.52, 0.82)])


def test_referenz_nimmt_das_optimum_wenn_bekannt_sonst_die_schranke():
    assert ev.referenz(_zelle(MITTEL_80, n=20, exakt=True, entschieden=73)) == ("dem Optimum", MITTEL_80)
    assert ev.referenz(_zelle(MITTEL_80, n=80)) == ("der Schranke", MITTEL_80)
    assert ev.referenz(_zelle(MITTEL_80, n=20, exakt=True, entschieden=0))[0] == "der Schranke"


def test_messung_regal_mit_hoehe_schlaegt_alle_freien_ist_warnung_mit_den_zahlen():
    kind, text = ev.verdict_messung(_zelle(MITTEL_80, n=80))
    assert kind == "warning"
    assert ("Für mittlere Rechtecke mit n = 80 ist der beste Schlüssel je Verfahren (Mittel über der Schranke, 100 Instanzen): Regal Höhe, Skyline Fläche, BSSF Fläche, BAF Fläche, BL Fläche.") in text
    assert "Regal mit Höhe 1.95; Skyline mit Höhe 2.47, mit Fläche 2.34; MaxRects BSSF mit Höhe 2.09, mit Fläche 1.90." in text
    assert "Mit der Höhe sortiert ist das **Regal besser als jede freie Platzierung**." in text
    assert "Bei dieser Rechteckzahl fehlt das Optimum und die Schranke ist locker: Lesen Sie nur die Unterschiede zwischen den Kombinationen, nicht den Abstand." in text


def test_messung_wenn_ein_freies_verfahren_mit_hoehe_gleich_gut_oder_besser_ist_info():
    kind, text = ev.verdict_messung(_zelle(MITTEL_FREI_GUT, verteilung=2, n=12, exakt=True, entschieden=96))
    assert kind == "info" and "Für kleine Rechtecke mit n = 12" in text and "Regal Höhe, Skyline Fläche, BSSF Fläche" in text and "Regal besser als jede" not in text
    assert "4 von 100 Instanzen sind nicht entschieden und fehlen im Mittel." in text and "(Mittel über dem Optimum, 96 Instanzen)" in text and "nicht den Abstand" not in text


def test_messung_nennt_gleich_gute_schluessel_mit_und():
    tab = {k: {v: 1.0 for v in range(5)} for k in range(4)}
    text = ev.verdict_messung(_zelle(tab))[1]
    assert "Regal Lieferung und Höhe und Fläche und Breite" in text


def test_messung_vergleicht_die_auf_zwei_stellen_gerundeten_werte():
    tab = {k: dict(v) for k, v in MITTEL_80.items()}
    tab[1][1] = 1.9504                  # Skyline mit Höhe angezeigt 1.95, gleich Regal mit Höhe: dann ist das Regal nicht „besser als jede“
    kind, text = ev.verdict_messung(_zelle(tab, n=80))
    assert kind == "info" and "Regal besser als jede" not in text and "Skyline mit Höhe 1.95" in text


# --- verdict_instanz -----------------------------------------------------------------------------------------------------------------------


def test_instanz_maxrects_besser_ist_erfolg_mit_beiden_zaehlungen():
    kind, text = ev.verdict_instanz(_zelle(MITTEL_80, mr=(16, 73, 11), sk=(0, 56, 44)))
    assert kind == "success"
    assert ("Von 100 Instanzen braucht MaxRects BSSF mit Fläche in **16** weniger Behälter als das Regal mit Höhe, in 73 gleich viele und in 11 mehr. "
            "Skyline mit Fläche braucht gegenüber MaxRects BSSF mit Fläche in 0 weniger, in 56 gleich viele und in **44** mehr. MaxRects mit Fläche ist hier das bessere Verfahren.") in text


def test_instanz_gleich_und_regal_besser():
    kind, text = ev.verdict_instanz(_zelle(MITTEL_80, mr=(5, 90, 5)))
    assert kind == "info" and "Beide Kombinationen sind hier gleich gut." in text
    kind, text = ev.verdict_instanz(_zelle(MITTEL_80, mr=(3, 90, 7)))
    assert kind == "warning" and "Hier ist das Regal mit Höhe besser." in text


# --- Experiment 2 ---------------------------------------------------------------------------------------------------------------------------


def _zeilen():
    return [{"verteilung": 0, "n": 12, "entschieden": 100, "offen": 0, "instanzen": 100, "regal": 69.0, "skyline": 73.0, "maxrects": 72.0},
            {"verteilung": 0, "n": 20, "entschieden": 73, "offen": 27, "instanzen": 100, "regal": 49.0, "skyline": 51.0, "maxrects": 60.0},
            {"verteilung": 2, "n": 20, "entschieden": 100, "offen": 0, "instanzen": 100, "regal": 96.0, "skyline": 98.0, "maxrects": 99.0}]


def test_optimum_verdikt_nennt_die_seltenste_und_die_haeufigste_zelle():
    kind, text = ev.verdict_optimum(_zeilen())
    assert kind == "info"
    assert ("MaxRects BSSF mit Fläche trifft das Optimum am seltensten bei mittleren Rechtecken mit n = 20 (60 % der 73 entschiedenen Instanzen, Regal mit Höhe 49 %, Skyline mit Fläche 51 %) "
            "und am häufigsten bei kleinen Rechtecken mit n = 20 (99 % der 100 entschiedenen Instanzen).") in text


def test_optimum_verdikt_ohne_optimum():
    z = [{"verteilung": 0, "n": 20, "entschieden": 0, "offen": 100, "instanzen": 100, "regal": None, "skyline": None, "maxrects": None}]
    assert ev.verdict_optimum(z) == ("info", "Es gibt keine Zelle mit bekanntem Optimum.")
