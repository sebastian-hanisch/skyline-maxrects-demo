"""Konstanten: Regler-Grenzen, feste Beispiele, Messraster, Farben und Presets."""

CAP = 100                 # Behälter 100 x 100 (Breite und Höhe)

# --- Beispiele (Rechtecke als (Breite, Höhe) in Lieferreihenfolge; zwölf Rechtecke aus dem Messraster von Stück 7) -----------------------------
# Beispiel 1 (mittlere Rechtecke, Instanz 4 von 100): Schranke 3, Optimum 3; Regal (First Fit) Lieferung / Höhe / Fläche / Breite 5 / 4 / 5 / 5, Skyline 4 / 4 / 3 / 3, MaxRects BSSF 5 / 4 / 3 / 3.
# Beispiel 2 (mittlere Rechtecke, Instanz 99): Schranke 2, Optimum 2; Regal 3 / 3 / 4 / 3, Skyline 3 / 3 / 3 / 3, MaxRects BSSF 3 / 3 / 2 / 3 (Phase 0, in den Tests nachgerechnet).
BEISPIELE = {
    0: ((43, 57), (41, 57), (50, 43), (27, 59), (56, 24), (29, 39), (48, 40), (32, 25), (20, 51), (47, 50), (56, 60), (46, 51)),
    1: ((20, 45), (38, 48), (54, 24), (41, 46), (25, 56), (51, 30), (36, 30), (21, 46), (55, 25), (50, 50), (47, 26), (21, 22)),
}
BEISPIEL_OPTIMUM = {0: 3, 1: 2}

# Quellen der Instanz: 0 und 1 = Handbeispiele, 2 bis 5 = Zufallsinstanzen mit der jeweiligen Verteilung
QUELLEN = {0: "Beispiel 1 (zwölf Rechtecke)", 1: "Beispiel 2 (zwölf andere Rechtecke)", 2: "zufällig, mittlere Rechtecke", 3: "zufällig, breit gestreute Rechtecke",
           4: "zufällig, kleine Rechtecke", 5: "zufällig, hohe schmale Rechtecke"}
ZUFALL_QUELLEN = (2, 3, 4, 5)
N_WERTE = (12, 20, 40)                    # Zahl der Rechtecke der Zufallsinstanzen in der App

# Verteilungen (dieselben wie in Stück 7): (Schlüssel, Name, Bereich der Breite, Bereich der Höhe)
VERTEILUNGEN = (
    ("mittel", "mittlere Rechtecke (20 bis 60)", (20, 60), (20, 60)),
    ("breit", "breit gestreute Rechtecke (5 bis 70)", (5, 70), (5, 70)),
    ("klein", "kleine Rechtecke (10 bis 40)", (10, 40), (10, 40)),
    ("hochschmal", "hohe schmale Rechtecke (Breite 5 bis 30, Höhe 30 bis 80)", (5, 30), (30, 80)),
)
VERTEILUNG_KURZ = ("mittel", "breit", "klein", "hoch schmal")
VERTEILUNG_LANG = ("mittlere Rechtecke", "breit gestreute Rechtecke", "kleine Rechtecke", "hohe schmale Rechtecke")
VERTEILUNG_DAT = ("mittleren Rechtecken", "breit gestreuten Rechtecken", "kleinen Rechtecken", "hohen schmalen Rechtecken")   # nach „bei“

SCHLUESSEL = {0: "Lieferreihenfolge (nicht sortiert)", 1: "nach Höhe (höchstes zuerst)", 2: "nach Fläche (größte zuerst)", 3: "nach Breite (breiteste zuerst)"}
SCHLUESSEL_KURZ = {0: "Lieferung", 1: "Höhe", 2: "Fläche", 3: "Breite"}
SCHLUESSEL_MIT = {0: "der Lieferreihenfolge", 1: "der Höhe", 2: "der Fläche", 3: "der Breite"}

VERFAHREN = {
    0: "Regal: erstes passendes Regal (FFDH)",
    1: "Skyline: niedrigste Stelle, dann links",
    2: "MaxRects: kleinste kurze Restkante (BSSF)",
    3: "MaxRects: kleinste Fläche des freien Rechtecks (BAF)",
    4: "MaxRects: unterste Position, dann links (BL)",
}
VERFAHREN_KURZ = {0: "Regal", 1: "Skyline", 2: "BSSF", 3: "BAF", 4: "BL"}
VERFAHREN_NAME = {0: "dem Regal (First Fit)", 1: "Skyline", 2: "MaxRects BSSF", 3: "MaxRects BAF", 4: "MaxRects BL"}
MAXRECTS_REGEL = {2: "bssf", 3: "baf", 4: "bl"}

SEED_MAX, DEFAULT_SEED = 999999, 7

# --- Messraster ---------------------------------------------------------------------------------------------------------------------------
INSTANZEN = 100                           # Instanzen je Zelle; der Wert steht neben jeder Zahl
MESS_N = (12, 20, 40, 80)
EXAKT_N = (12, 20)                        # in diesen Zellen gibt es das Optimum (aus Stück 7 übernommen, CP-SAT mit Zeitlimit, ggf. nicht entschieden)
OPT_HERKUNFT = "regalverfahren-demo/rgv_precomputed.json (Stück 7): gleiche Verteilungen und Seeds, Optimum je Instanz mit CP-SAT (60 Sekunden Zeitlimit), -1 = nicht entschieden"

COLOR_LINE = "#c0392b"
COLOR_FREI = "#2F6B65"
COLOR_PROFIL = "#c0392b"
REGAL_FARBEN = ("#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756", "#72b7b2", "#9d755d", "#bab0ac", "#eeca3b", "#ff9da6")
VERFAHREN_FARBEN = {0: "#9d755d", 1: "#c0392b", 2: "#2F6B65", 3: "#4c78a8", 4: "#b279a2"}

PRESETS = {
    "Beispiel 1, Höhe, Regal": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 1, "verfahren": 0, "schritt": 0},
    "Beispiel 1, Fläche, MaxRects BSSF": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 2, "verfahren": 2, "schritt": 0},
    "Beispiel 2, Fläche, MaxRects BSSF": {"quelle": 1, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 2, "verfahren": 2, "schritt": 0},
    "Beispiel 1, Fläche, Skyline, Schritt 5": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "schluessel": 2, "verfahren": 1, "schritt": 5},
}
PRESET_HELP = {
    "Beispiel 1, Höhe, Regal": "Zwölf Rechtecke nach der Höhe sortiert und in Regale gesetzt: der beste Regalplan braucht vier Behälter.",
    "Beispiel 1, Fläche, MaxRects BSSF": "Dieselben zwölf Rechtecke, nach der Fläche sortiert und in die freien Rechtecke gesetzt, die am knappsten passen: drei Behälter, so viele wie das Optimum.",
    "Beispiel 2, Fläche, MaxRects BSSF": "Ein zweites Beispiel: Von den zwanzig Kombinationen findet nur diese das Optimum, zwei Behälter.",
    "Beispiel 1, Fläche, Skyline, Schritt 5": "Skyline nach dem fünften Rechteck: die rote Linie ist die Oberkante, unter der nichts mehr frei ist.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Rechtecke mit ganzzahliger Breite und Höhe, ohne Drehung; Behälter {CAP} mal {CAP}; alle Rechtecke sind vor dem Packen bekannt; jedes Rechteck kommt in den ersten Behälter, in dem es nach der Regel des Verfahrens passt.

**Grenzen.** Das Messraster deckt vier Verteilungen der Rechteckmaße und vier Rechteckzahlen ab, jeweils mit {INSTANZEN} Instanzen je Zelle; es sind dieselben Instanzen wie in Stück 7. Praxisdaten, Drehung und weitere Verfahren und Regeln kommen nicht vor. Das exakte Optimum (über alle Packungen) gibt es bei 12 und 20 Rechtecken, bei 20 nur für die Instanzen, die CP-SAT in der Zeit entschieden hat; bei 40 und 80 Rechtecken fehlt es.

**Bekannte Probleme und Unsicherheiten.** Bei 40 und 80 Rechtecken ist der Maßstab die Schranke, die in 2D locker ist: Ein Teil des Abstands ist Schranke, nicht schlechtes Packen. Die entschiedenen Instanzen bei 20 Rechtecken sind die leichteren, die Mittel dort sind nach unten verzerrt. Die Optima stammen aus Stück 7 und werden nur stichprobenweise nachgerechnet. Die Mittelwerte des Rasters gelten für diese festen Instanzen; mit anderen Startzahlen ändern sie sich etwas, und eine einzelne Zelle ist kein Gesetz. Zur Laufzeit der Verfahren macht die Demo keine Aussage. Die Literaturhinweise im Mathematik-Expander stammen aus Suchtreffern (nur Inhaltsverzeichnis und Zweitbeschreibungen), die Originale wurden nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button, Schritt-Regler und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
