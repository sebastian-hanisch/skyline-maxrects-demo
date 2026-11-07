"""Setzt die README zusammen: Tabellen und Text der Annahmen kommen aus denselben Funktionen wie in der App (nur zum Schreiben der README, nicht Teil der Laufzeit).

    python dev/readme_bauen.py [ANZAHL_TESTS]
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import smx_constants as C  # noqa: E402
import smx_evaluation as ev  # noqa: E402
from smx_scenario import beispiel  # noqa: E402

KOMBIS = ((1, 0), (2, 0), (1, 1), (2, 1), (1, 2), (2, 2), (2, 3), (2, 4))      # (Schlüssel, Verfahren) der Tabelle A


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def tabellen():
    """(A, B, Beispiel 1, Beispiel 2): A = Behälter über der Vergleichsbasis je Zelle für acht Kombinationen, B = Anteil Optimum getroffen, die Beispiele = Behälterzahlen je Verfahren und Schlüssel."""
    kopf = " | ".join(f"{C.VERFAHREN_KURZ[v]} {C.SCHLUESSEL_KURZ[k]}" for k, v in KOMBIS)
    ta = ["| Verteilung | n | Basis | " + kopf + " |", "|---|---|---|" + "---|" * len(KOMBIS)]
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            z = ev.zeile(v, ni)
            b, m = ev.referenz(z)
            ta.append(f"| {C.VERTEILUNG_KURZ[v]} | {n} | {'Optimum' if b == 'dem Optimum' else 'Schranke'} | " + " | ".join(de(m[k][vf]) for k, vf in KOMBIS) + " |")
    tb = ["| Verteilung | n | Regal Höhe | Skyline Fläche | BSSF Fläche |", "|---|---|---|---|---|"]
    for r in ev.optimum_zeilen():
        tb.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} | {r['n']} | {r['regal']:.0f} % | {r['skyline']:.0f} % | {r['maxrects']:.0f} % |")
    bsp = []
    for b in (0, 1):
        t = ev.tabelle(beispiel(b))
        zeilen = ["| Verfahren | " + " | ".join(C.SCHLUESSEL_KURZ[k] for k in range(4)) + " |", "|---|---|---|---|---|"]
        for vf in range(5):
            zeilen.append(f"| {C.VERFAHREN_KURZ[vf]} | " + " | ".join(str(t[k][vf]) for k in range(4)) + " |")
        bsp.append("\n".join(zeilen))
    return "\n".join(ta), "\n".join(tb), bsp[0], bsp[1]


if __name__ == "__main__":
    vorlage = (ROOT / "dev" / "readme_vorlage.md").read_text(encoding="utf-8")
    ta, tb, b1, b2 = tabellen()
    anzahl = sys.argv[1] if len(sys.argv) > 1 else "TESTZAHL"
    text = (vorlage.replace("{{TABELLE_A}}", ta).replace("{{TABELLE_B}}", tb).replace("{{BEISPIEL_1}}", b1).replace("{{BEISPIEL_2}}", b2)
            .replace("{{ANNAHMEN}}", C.ASSUMPTIONS_MARKDOWN).replace("{{TESTS}}", anzahl))
    (ROOT / "README.md").write_text(text, encoding="utf-8")
    print("README.md geschrieben")
