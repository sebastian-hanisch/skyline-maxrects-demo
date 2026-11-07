"""Erzeugt smx_precomputed.json: das Messraster (vier Verteilungen der Rechteckmaße × Rechteckzahlen 12, 20, 40, 80 × 100 feste Instanzen, 20 Kombinationen aus Schlüssel und Verfahren).

    python generate_precomputed.py                         # rechnet alle Zellen neu; die Optima (bei 12 und 20 Rechtecken) kommen aus ../regalverfahren-demo/rgv_precomputed.json (etwa 5 bis 10 Minuten)
    python generate_precomputed.py --opt-aus PFAD          # dasselbe mit anderer Quelle der Optima
    python generate_precomputed.py --keep-opt              # behält die in der Datei gespeicherten Optima und rechnet nur die Behälterzahlen neu
    python generate_precomputed.py --check                 # rechnet alle Zellen mit den gespeicherten Optima nach und vergleicht mit der Datei

Die Instanzen sind dieselben wie in Stück 7 (gleiche Verteilungen, gleiche Seeds); das Optimum je Instanz hat dort CP-SAT mit Zeitlimit berechnet (-1 = nicht entschieden). Hier wird es nur
übernommen und in den Tests stichprobenweise mit CP-SAT nachgerechnet."""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import smx_constants as C
import smx_evaluation as ev

STANDARD_QUELLE = Path(__file__).resolve().parent.parent / "regalverfahren-demo" / "rgv_precomputed.json"


def _zelle(args):
    v, ni, opt = args
    t = time.perf_counter()
    z = ev.messzelle(v, ni, opt)
    if opt is not None:
        z["opt"] = opt
    return v, ni, z, time.perf_counter() - t


def erzeugen(quelle: Path | None, behalten: bool) -> dict:
    if behalten:
        alt = ev.vorberechnet()
        optima = {k: z["opt"] for k, z in alt["zellen"].items() if "opt" in z}
    else:
        rgv = json.loads(quelle.read_text(encoding="utf-8"))
        assert rgv["instanzen"] == C.INSTANZEN and rgv["cap"] == C.CAP
        optima = {k: z["opt"] for k, z in rgv["zellen"].items() if "opt" in z}
    auftraege = []
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            auftraege.append((v, ni, optima[ev.zelle_schluessel(v, ni)] if n in C.EXAKT_N else None))
    daten = {"instanzen": C.INSTANZEN, "cap": C.CAP, "opt_herkunft": C.OPT_HERKUNFT, "zellen": {}}
    with ProcessPoolExecutor(max(1, min(4, (os.cpu_count() or 2) // 2))) as pool:
        for v, ni, z, sekunden in pool.map(_zelle, auftraege):
            daten["zellen"][ev.zelle_schluessel(v, ni)] = z
            print(f"{ev.zelle_schluessel(v, ni)}: {sekunden:.0f} s", flush=True)
    daten["zellen"] = {k: daten["zellen"][k] for k in sorted(daten["zellen"], key=lambda s: [ev.zelle_schluessel(v, ni) for v in range(4) for ni in range(4)].index(s))}
    return daten


def pruefen() -> int:
    gespeichert = ev.vorberechnet()
    schlecht = 0
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            schl = ev.zelle_schluessel(v, ni)
            z = gespeichert["zellen"][schl]
            if n in C.EXAKT_N:
                frisch = ev.messzelle(v, ni, z["opt"])
                frisch["opt"] = z["opt"]
            else:
                frisch = ev.messzelle(v, ni)
            if frisch != z:
                schlecht += 1
                print("ABWEICHUNG", schl)
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(pruefen())
    quelle = Path(sys.argv[sys.argv.index("--opt-aus") + 1]) if "--opt-aus" in sys.argv else STANDARD_QUELLE
    daten = erzeugen(quelle, "--keep-opt" in sys.argv)
    ev.PRECOMPUTED.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED.name)
