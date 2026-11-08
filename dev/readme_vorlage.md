# Freiflächen verwalten: Skyline und MaxRects – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-skyline-maxrects-demo.streamlit.app/)**

Stück 8 der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Teile und einer Regel, wohin das nächste kommt). Stück 7 hat Rechtecke in Regale gezwungen; diese Demo verwaltet stattdessen den **freien Platz** im Behälter (Skyline: die Oberkante der gesetzten Rechtecke, MaxRects: die Liste aller größten freien Rechtecke) und fragt, ob der Sortierschlüssel, der beim Regal der beste war, auch hier der beste ist. Die Fall-Demos zu Zuschnitt und Paletten zeigen die Anwendung samt Kostenmodell; diese Demo erklärt den Mechanismus davor.

## Warum dieses Problem

Beim Regal war die Höhe der beste Schlüssel. Bei freier Platzierung ist es meistens die Fläche („das größte zuerst“), und mit der Höhe sortiert ist das Regal bei mittleren (ab n = 20) und breit gestreuten Rechtecken (ab n = 40) sogar besser als Skyline und MaxRects. Der beste Schlüssel hängt also vom Verfahren ab. Die Demo zeigt an zwölf Rechtecken, dass der beste Regalplan vier Behälter braucht, jede freie Platzierung nach der Fläche aber drei, und misst dasselbe an je 100 Zufallsinstanzen in 16 Zellen, denselben Instanzen wie in Stück 7.

## Modell

Rechtecke mit ganzzahliger Breite und Höhe, ohne Drehung, in Behältern der Größe 100 mal 100, alle vorab bekannt; jedes Rechteck kommt in den ersten Behälter, in dem es nach der Regel des Verfahrens passt, sonst in einen neuen. **Regal:** das erste passende Regal (First Fit, wie in Stück 7). **Skyline:** an die niedrigste Stelle der Oberkante der gesetzten Rechtecke, bei Gleichstand links; was unter einem Überhang frei bleibt, ist verloren. **MaxRects:** in die linke untere Ecke des freien Rechtecks, das nach einer Regel am besten passt, bei **BSSF** die kleinste kurze Restkante, bei **BAF** die kleinste Fläche des freien Rechtecks, bei **BL** die unterste Position; danach wird jedes überlappte freie Rechteck in bis zu vier Teile zerlegt und die Liste auf die maximalen Rechtecke gekürzt. **Schlüssel** (absteigend, Gleichstand: Lieferreihenfolge): Lieferreihenfolge, Höhe, Fläche, Breite. **Schranken:** die Fläche aller Rechtecke durch die Behälterfläche, aufgerundet, und die Zahl der Rechtecke, die in beiden Maßen über die Hälfte reichen; das Größere von beiden. **Optimum** über alle Packungen mit CP-SAT (in Stück 7 berechnet, hier mit Herkunftsvermerk übernommen). **Vier Verteilungen:** *mittel* (Breite und Höhe 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *hoch schmal* (Breite 5 bis 30, Höhe 30 bis 80). Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`smx_algorithm.py`): `schluessel_wert`, `reihenfolge`, `pack` (fünf Verfahren; liefert Behälter, Platzierungen und den Zustand je Behälter: Regale, Höhenprofil oder freie Rechtecke; ein Anfang der Reihenfolge liefert den Zustand nach so vielen Schritten), `schranken`, `packung_pruefen` (unabhängiger Prüfer: jedes Rechteck genau einmal, im Behälter, keine Überlappung).
- **Handbeispiele:** zwei feste Mengen von je zwölf Rechtecken aus dem Raster von Stück 7. Die App zeichnet die Behälter maßstäblich samt Freiflächen (Schritt-Regler) und zeigt alle 20 Kombinationen aus Schlüssel und Verfahren.
- **Messraster:** vier Verteilungen × vier Rechteckzahlen (12, 20, 40, 80) × **100 feste Instanzen** je Zelle, dieselben Instanzen wie in Stück 7. Maßstab ist bei 12 und 20 Rechtecken das Optimum (aus Stück 7 übernommen, nur die entschiedenen Instanzen), bei 40 und 80 die Schranke. Die Summen stehen als ganze Zahlen in `smx_precomputed.json` (erzeugt von `generate_precomputed.py`, Optima aus `regalverfahren-demo/rgv_precomputed.json`).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_skyline_maxrects.py`. Tabellenwerte sind Mittel über die Instanzen einer Zelle von (Behälter minus Vergleichsbasis).

| Frage | Befund |
|---|---|
| Beispiel 1 (zwölf Rechtecke, Schranke 3, Optimum 3) | Der beste Regalplan (Höhe) braucht **4** Behälter, Skyline, MaxRects BSSF, BAF und BL nach Fläche je **3** (Tabelle unten) |
| Beispiel 2 (zwölf andere Rechtecke, Schranke 2, Optimum 2) | Von den 20 Kombinationen findet nur **eine** das Optimum 2: MaxRects BSSF nach Fläche |
| Welcher Schlüssel ist am besten? | Beim Regal die **Höhe** in allen **16** Zellen; bei MaxRects BSSF die **Fläche** in **14** Zellen (in den übrigen zwei gleichauf mit der Höhe), bei Skyline die Fläche in **11**, die Höhe in 4, einmal gleichauf (klar ist der Vorsprung der Fläche bei Skyline nur bei mittleren und breit gestreuten Rechtecken; bei kleinen und hohen schmalen liegt der Unterschied im Rauschen) |
| Schlägt das Regal mit Höhe die freien Verfahren mit Höhe? | In **5** von 16 Zellen braucht das Regal mit Höhe im Mittel weniger Behälter als jedes der vier freien Verfahren mit Höhe: mittlere Rechtecke bei n = 20, 40, 80 und breit gestreute bei n = 40, 80 |
| MaxRects gegen Regal, Instanz für Instanz | MaxRects BSSF mit Fläche braucht gegen das Regal mit Höhe in **307** von 1600 Instanzen weniger Behälter, in 1260 gleich viele und in **33** mehr; im Mittel ist es in **15** von 16 Zellen besser, in einer gleich (klein, n = 80) |
| Skyline gegen MaxRects, Instanz für Instanz | Skyline mit Fläche braucht gegen MaxRects BSSF mit Fläche in 17 von 1600 Instanzen weniger Behälter, in 1296 gleich viele und in **287** mehr; im Mittel liegt Skyline 0,01 unter bis 0,44 über MaxRects (in einer Zelle besser) |
| Welche MaxRects-Regel ist am besten? | Mit der Fläche ist BSSF in **14** von 16 Zellen die beste der drei (in 7 allein); die drei Regeln liegen höchstens **0,19** Behälter auseinander |
| Wie nah am Optimum? | Mit Höhe beim Regal und Fläche bei Skyline und MaxRects BSSF treffen bei 12 Rechtecken das Regal 67 bis 80 %, Skyline 66 bis 92 %, MaxRects BSSF 72 bis 95 % der entschiedenen Instanzen, bei 20 Rechtecken 49 bis 96 %, 51 bis 98 % und 60 bis 99 % |
| Wie viele Instanzen sind nicht entschieden? | **3** von 400 bei 12 und **39** von 400 bei 20 Rechtecken (**27** bei mittleren, 1 bei breit gestreuten, 0 bei kleinen und 11 bei hohen schmalen); die Zahl hängt von der Rechenzeit in Stück 7 ab |

**Beispiel 1** (Behälterzahl je Verfahren und Schlüssel):

{{BEISPIEL_1}}

**Beispiel 2:**

{{BEISPIEL_2}}

**Behälter über der Vergleichsbasis** (Mittel; Basis: Optimum bei 12 und 20 Rechtecken, nur über die entschiedenen Instanzen, sonst die Schranke; acht Kombinationen aus Verfahren und Schlüssel; bei 40 und 80 Rechtecken ist die Schranke locker, dort zählt nur der Vergleich der Kombinationen):

{{TABELLE_A}}

**Optimum getroffen** (Anteil der entschiedenen Instanzen, in denen die Kombination genau das Optimum braucht):

{{TABELLE_B}}

## Ehrliche Grenzen

- Alle Aussagen gelten für Rechtecke ohne Drehung, vier Verteilungen mit festen Bereichen, vier Rechteckzahlen, eine Behältergröße und genau diese fünf Verfahren mit je einer festen Regel für den Behälter („erster passender“). Weitere Regeln, andere Verfahren und Praxisdaten sind nicht gemessen.
- Das Optimum gilt über **alle** Packungen. Es stammt aus Stück 7 (CP-SAT mit Zeitlimit): Bei 20 Rechtecken sind die nicht entschiedenen Instanzen die schweren und fehlen im Mittel; bei mittleren Rechtecken sind 27 von 100 offen, der Mittelwert dort ist nach unten verzerrt. Die Optima werden hier nur stichprobenweise nachgerechnet.
- Bei 40 und 80 Rechtecken fehlt das Optimum; die Schranke ist in 2D locker, also ist dort nur der Vergleich der Kombinationen belastbar, nicht der Abstand zur Schranke.
- Zur **Laufzeit** der Verfahren macht die Demo keine Aussage: Sie hängt an der Umsetzung (hier Python, Skyline mit Spaltenabtastung).
- Die Literaturhinweise (Jylänki 2010, MaxRects und Skyline) stammen aus Suchtreffern (nur Inhaltsverzeichnis und Zweitbeschreibungen); es wird keine Zahl, keine Gütegarantie und keine Aussage zu Dichte oder Geschwindigkeit daraus übernommen.
- Das Raster sagt nichts über Rechtecke, die einzeln nacheinander ohne Kenntnis der späteren eintreffen (Online-Packen, Konzepte-Reihe Online-Algorithmen).

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

{{ANNAHMEN}}

## Verifikation

- **Kern:** alle fünf Verfahren an einer von Hand gerechneten Mini-Instanz (vier Rechtecke, Behälter 10 mal 10, mit Platzierungen, Profil und freien Rechtecken nach jedem Schritt, bei MaxRects BAF und BL mit ihrer abweichenden Wahl); Beispiel 1 mit den ersten Schritten von MaxRects und Skyline nach Fläche; beide Handbeispiele mit allen 20 Behälterzahlen; unabhängiger Packungsprüfer; Randfälle (leere Eingabe, ein Rechteck, Rechteck gleich Behälter, Grenzen inklusive, kein Platz, Hohlraum unter einem Überhang, Anfang der Reihenfolge, ungültige Eingaben).
- **Orakel** (`tests/test_oracle_skyline_maxrects.py`): Skyline gegen eine Umsetzung, die das Profil jedes Mal aus der Liste der gesetzten Rechtecke liest (40 Instanzen, drei Schlüssel); MaxRects mit allen drei Regeln gegen eine Umsetzung, die in jedem Schritt alle maximalen leeren Rechtecke nach Definition aus einem Belegungsraster aufzählt (Behälter 10 bis 14, 14 Instanzen, zwei Schlüssel); die freien Rechtecke sind nach jedem Schritt genau die maximalen leeren Rechtecke und ihre Vereinigung ist genau die leere Fläche; das Regal gegen eine naive Neuberechnung; Eigenschaften: Packungen zulässig und nie unter der Schranke, gemeinsames Skalieren, Eingabereihenfolge bei sortierten Schlüsseln.
- **Messraster:** jede der 16 Zellen wird frisch gerechnet und exakt mit `smx_precomputed.json` verglichen; die Optima werden bei 12 und 20 Rechtecken stichprobenweise mit CP-SAT nachgerechnet; jede Zahl dieser README als Textsuche (`tests/test_claims.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, erstes Preset gleich Standardeinstellung, jeder Hilfetext stimmt mit der Rechnung überein; Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, der Schritt-Regler an seinen Grenzen, Startzahl an den Grenzen) und Footer-Test.
- **Tests gesamt:** {{TESTS}}.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `dev/opt.py` | exaktes Optimum mit CP-SAT (nur für die Stichprobe in den Tests) |
| `dev/readme_bauen.py`, `dev/readme_vorlage.md` | setzen die README aus der Vorlage, den Tabellen der Messzellen und dem Text der Annahmen zusammen |
| `generate_precomputed.py` | erzeugt `smx_precomputed.json` (Messraster, Optima aus Stück 7); `--check` vergleicht, `--keep-opt` behält die gespeicherten Optima |
| `requirements-dev.txt` | Laufzeit plus pytest und ortools |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `smx_algorithm.py` | Kern: Schlüssel, Verfahren, Schranken, Packungsprüfer |
| `smx_constants.py` | Beispiele, Reglerwerte, Messraster, Farben, Presets, Text der Annahmen |
| `smx_evaluation.py` | Analyse, Verdikte, Messzellen |
| `smx_layout.py` | Fester Kopf (Stylesheet) |
| `smx_precomputed.json` | vorberechnete Summen und Optima des Messrasters |
| `smx_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `smx_scenario.py` | Instanzen: Handbeispiele und Zufallsinstanzen mit festen Seeds (wie in Stück 7) |
| `smx_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Mini-Instanz und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, Messraster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Drehung der Rechtecke, weitere Regeln (etwa Berührungspunkt bei MaxRects) und andere Verfahren (Guillotine, Extreme Points):** nicht Gegenstand dieses Stücks.
- **Laufzeitvergleich der Verfahren:** hängt an der Umsetzung, keine Aussage.
- **Neu berechnetes Optimum:** die Optima kommen aus Stück 7; ein eigener CP-SAT-Lauf wäre derselbe, nur länger.
- **Gütegarantien und Zahlen aus der Literatur:** Die Originale wurden nicht gelesen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
