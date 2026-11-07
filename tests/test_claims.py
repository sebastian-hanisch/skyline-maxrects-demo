"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (smx_precomputed.json): jede der 16 Zellen frisch gerechnet; die Optima bei 12 und 20 Rechtecken stammen aus Stück 7 und werden stichprobenweise mit CP-SAT nachgerechnet
  (das zeigt zugleich, dass die Instanzen dieser Demo dieselben sind wie dort).
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt."""

import itertools
from pathlib import Path

import pytest

import smx_algorithm as A
import smx_constants as C
import smx_evaluation as ev
from smx_scenario import beispiel, mess_seed, zufallsinstanz

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ZELLEN = list(itertools.product(range(len(C.VERTEILUNGEN)), range(len(C.MESS_N))))


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def alle():
    return {(v, ni): ev.zeile(v, ni) for v, ni in ZELLEN}


def gerundete():
    return {k: ev.gerundet(ev.referenz(z)[1]) for k, z in alle().items()}


def test_raster_hat_alle_zellen_und_die_parameter():
    daten = ev.vorberechnet()
    assert daten["instanzen"] == C.INSTANZEN == 100 and daten["cap"] == C.CAP == 100 and daten["opt_herkunft"] == C.OPT_HERKUNFT
    assert set(daten["zellen"]) == {ev.zelle_schluessel(v, ni) for v, ni in ZELLEN} and len(ZELLEN) == 16
    for (v, ni), n in ((k, C.MESS_N[k[1]]) for k in ZELLEN):
        z = daten["zellen"][ev.zelle_schluessel(v, ni)]
        assert ("opt" in z) == (n in C.EXAKT_N)
        if "opt" in z:
            assert len(z["opt"]) == 100


@pytest.mark.parametrize("v,ni", ZELLEN)
def test_jede_zelle_stimmt_mit_frischer_rechnung(v, ni):
    gespeichert = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]
    if C.MESS_N[ni] in C.EXAKT_N:
        frisch = ev.messzelle(v, ni, gespeichert["opt"])
        frisch["opt"] = gespeichert["opt"]
    else:
        frisch = ev.messzelle(v, ni)
    assert frisch == gespeichert


def test_gespeicherte_optima_liegen_zwischen_schranke_und_bester_heuristik():
    """Für jede entschiedene Instanz bei 12 und 20 Rechtecken: Schranke <= Optimum <= beste Heuristik (die Packung mit dieser Zahl existiert)."""
    for v, ni in ZELLEN:
        if C.MESS_N[ni] not in C.EXAKT_N:
            continue
        opt = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]["opt"]
        for j, o in enumerate(opt):
            if o < 0:
                continue
            inst = zufallsinstanz(v, C.MESS_N[ni], mess_seed(v, ni, j))
            ober = min(A.anzahl(inst.rects, k, vf, inst.cap) for k in range(4) for vf in range(5))
            assert A.schranke(inst.rects, inst.cap) <= o <= ober, (v, ni, j)


STICHPROBE = {12: {0: (9, 11), 1: (6, 7), 2: (7, 9), 3: (17, 27)},       # je zwei Instanzen, die CP-SAT in Bruchteilen von Sekunden entscheidet (wie in Stück 7)
              20: {0: (28, 34), 1: (5, 6), 2: (0, 1), 3: (2, 6)}}


@pytest.mark.parametrize("n", (12, 20))
@pytest.mark.parametrize("v", range(len(C.VERTEILUNGEN)))
def test_stichprobe_der_optima_stimmt_mit_cpsat_ueberein(v, n):
    pytest.importorskip("ortools")
    from dev.opt import optimum_cpsat

    ni = C.MESS_N.index(n)
    opt = ev.vorberechnet()["zellen"][ev.zelle_schluessel(v, ni)]["opt"]
    for j in STICHPROBE[n][v]:
        inst = zufallsinstanz(v, n, mess_seed(v, ni, j))
        ober = min(A.anzahl(inst.rects, k, vf, inst.cap) for k in range(4) for vf in range(5))
        untergrenze = A.schranke(inst.rects, inst.cap)
        ist = ober if ober == untergrenze else optimum_cpsat(inst.rects, inst.cap, ober, 60.0)
        assert ist == opt[j] >= untergrenze, (v, n, j)


# --- Tabellen der README -------------------------------------------------------------------------------------------------------------------


def test_readme_tabellen_geben_jede_zeile_wieder():
    from dev.readme_bauen import tabellen

    for tabelle in tabellen():
        for zeile in tabelle.split("\n"):
            assert zeile in README, zeile


# --- Befunde der README --------------------------------------------------------------------------------------------------------------------


def test_beispiele_in_der_readme():
    t1, t2 = ev.tabelle(beispiel(0)), ev.tabelle(beispiel(1))
    assert [[t1[k][v] for k in range(4)] for v in range(5)] == [[5, 4, 5, 5], [4, 4, 3, 3], [5, 4, 3, 3], [5, 4, 3, 3], [4, 4, 3, 3]]
    assert [[t2[k][v] for k in range(4)] for v in range(5)] == [[3, 3, 4, 3], [3, 3, 3, 3], [3, 3, 2, 3], [3, 3, 3, 3], [3, 3, 3, 3]]
    assert [A.schranke(beispiel(b).rects, C.CAP) for b in (0, 1)] == [3, 2] and C.BEISPIEL_OPTIMUM == {0: 3, 1: 2}
    assert "Beispiel 1 (zwölf Rechtecke, Schranke 3, Optimum 3)" in README and "Beispiel 2 (zwölf andere Rechtecke, Schranke 2, Optimum 2)" in README
    assert "Der beste Regalplan (Höhe) braucht **4** Behälter, Skyline, MaxRects BSSF, BAF und BL nach Fläche je **3**" in README
    assert min(t1[k][0] for k in range(4)) == 4 and all(t1[2][v] == 3 for v in (1, 2, 3, 4))
    assert [(k, v) for k in range(4) for v in range(5) if t2[k][v] == 2] == [(2, 2)] and "findet nur **eine** das Optimum 2: MaxRects BSSF nach Fläche" in README


def test_bester_schluessel_je_verfahren():
    g = gerundete()
    zaehlung = {}
    for v in range(5):
        alleine = {}
        gleichauf = 0
        for k in g.values():
            b = ev.beste_schluessel_zelle(k, v)
            if len(b) == 1:
                alleine[b[0]] = alleine.get(b[0], 0) + 1
            else:
                gleichauf += 1
        zaehlung[v] = (alleine, gleichauf)
    assert zaehlung[0] == ({1: 16}, 0) and zaehlung[2] == ({2: 14}, 2) and zaehlung[1] == ({2: 11, 1: 4}, 1)
    assert "Beim Regal die **Höhe** in allen **16** Zellen; bei MaxRects BSSF die **Fläche** in **14** Zellen (in den übrigen zwei gleichauf mit der Höhe), bei Skyline die Fläche in **11**, die Höhe in 4, einmal gleichauf" in README
    # die zwei gleichauf liegenden BSSF-Zellen: klein mit n = 80 und hoch schmal mit n = 12, dort teilen sich Höhe und Fläche den ersten Platz
    gleichauf = {k: ev.beste_schluessel_zelle(x, 2) for k, x in g.items() if len(ev.beste_schluessel_zelle(x, 2)) > 1}
    assert gleichauf == {(2, 3): [1, 2], (3, 0): [1, 2]}


def test_regal_mit_hoehe_schlaegt_die_freien_verfahren_mit_hoehe_in_fuenf_zellen():
    g = gerundete()
    zellen = [(v, C.MESS_N[ni]) for (v, ni), k in g.items() if all(k[1][0] < k[1][vf] for vf in (1, 2, 3, 4))]
    assert zellen == [(0, 20), (0, 40), (0, 80), (1, 40), (1, 80)]
    assert "In **5** von 16 Zellen braucht das Regal mit Höhe im Mittel weniger Behälter als jedes der vier freien Verfahren mit Höhe: mittlere Rechtecke bei n = 20, 40, 80 und breit gestreute bei n = 40, 80" in README


def test_instanz_fuer_instanz_zaehlungen():
    z = alle()
    mr = [sum(x["mr_gegen_regal"][i] for x in z.values()) for i in range(3)]
    sk = [sum(x["skyline_gegen_mr"][i] for x in z.values()) for i in range(3)]
    assert mr == [307, 1260, 33] and sum(mr) == 1600 and sk == [17, 1296, 287] and sum(sk) == 1600
    assert "in **307** von 1600 Instanzen weniger Behälter, in 1260 gleich viele und in **33** mehr" in README
    assert "in 17 von 1600 Instanzen weniger Behälter, in 1296 gleich viele und in **287** mehr" in README


def test_mittelwerte_maxrects_gegen_regal_und_skyline_gegen_maxrects():
    g = gerundete()
    besser = [k for k, x in g.items() if x[2][2] < x[1][0]]
    gleich = [k for k, x in g.items() if x[2][2] == x[1][0]]
    assert len(besser) == 15 and gleich == [(2, 3)]                      # klein, n = 80
    assert "im Mittel ist es in **15** von 16 Zellen besser, in einer gleich (klein, n = 80)" in README
    abstand = [round(x[2][1] - x[2][2], 2) for x in g.values()]
    assert (min(abstand), max(abstand), sum(a < 0 for a in abstand)) == (-0.01, 0.44, 1)
    assert "im Mittel liegt Skyline 0,01 unter bis 0,44 über MaxRects (in einer Zelle besser)" in README


def test_maxrects_regeln_mit_flaeche():
    g = gerundete()
    bssf_bester, allein, spanne = 0, 0, 0.0
    for x in g.values():
        werte = {v: x[2][v] for v in (2, 3, 4)}
        kleinster = min(werte.values())
        bssf_bester += werte[2] == kleinster
        allein += werte[2] == kleinster and list(werte.values()).count(kleinster) == 1
        spanne = max(spanne, round(max(werte.values()) - kleinster, 2))
    assert (bssf_bester, allein, de(spanne)) == (14, 7, "0,19")
    assert "Mit der Fläche ist BSSF in **14** von 16 Zellen die beste der drei (in 7 allein); die drei Regeln liegen höchstens **0,19** Behälter auseinander" in README


def test_optimum_getroffen_und_offene_instanzen():
    zeilen = ev.optimum_zeilen()
    assert len(zeilen) == 8
    spannen = {n: [(min(round(r[k]) for r in zeilen if r["n"] == n), max(round(r[k]) for r in zeilen if r["n"] == n)) for k in ("regal", "skyline", "maxrects")] for n in (12, 20)}
    assert spannen[12] == [(67, 80), (66, 92), (72, 95)] and spannen[20] == [(49, 96), (51, 98), (60, 99)]
    assert ("treffen bei 12 Rechtecken das Regal 67 bis 80 %, Skyline 66 bis 92 %, MaxRects BSSF 72 bis 95 % der entschiedenen Instanzen, bei 20 Rechtecken 49 bis 96 %, 51 bis 98 % und 60 bis 99 %") in README
    offen12 = [ev.zeile(v, 0)["offen"] for v in range(4)]
    offen20 = [ev.zeile(v, 1)["offen"] for v in range(4)]
    assert offen12 == [0, 0, 1, 2] and offen20 == [27, 1, 0, 11] and sum(offen12) == 3 and sum(offen20) == 39
    assert "**3** von 400 bei 12 und **39** von 400 bei 20 Rechtecken (**27** bei mittleren, 1 bei breit gestreuten, 0 bei kleinen und 11 bei hohen schmalen)" in README
    assert ev.zeile(0, 1)["entschieden"] == 73 and "bei mittleren Rechtecken sind 27 von 100 offen" in README


# --- Beispiele und Texte --------------------------------------------------------------------------------------------------------------------


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    t = C.ASSUMPTIONS_MARKDOWN
    assert f"Behälter {C.CAP} mal {C.CAP}" in t and f"{C.INSTANZEN} Instanzen" in t and "bei 12 und 20 Rechtecken" in t and "bei 40 und 80 Rechtecken" in t
    assert C.MESS_N == (12, 20, 40, 80) and C.EXAKT_N == (12, 20)


def test_readme_nennt_die_verteilungen_wie_der_code():
    assert "*mittel* (Breite und Höhe 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *hoch schmal* (Breite 5 bis 30, Höhe 30 bis 80)" in README
    assert [(vt[2], vt[3]) for vt in C.VERTEILUNGEN] == [((20, 60), (20, 60)), ((5, 70), (5, 70)), ((10, 40), (10, 40)), ((5, 30), (30, 80))]
    assert "vier Verteilungen × vier Rechteckzahlen (12, 20, 40, 80) × **100 feste Instanzen**" in README
