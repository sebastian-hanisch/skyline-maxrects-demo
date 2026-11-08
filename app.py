"""Packen: Freiflächen verwalten, Skyline und MaxRects - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 8 der Reihe „Packen: Reihenfolge und Platzierungsregel“. Rechtecke ohne Überlappung in Behälter: Statt in Regale zu zwingen, verwalten Skyline und MaxRects den freien Platz.
Passt der Sortierschlüssel noch? Das Messraster (vorberechnet in smx_precomputed.json) zeigt die Antwort an je 100 Zufallsinstanzen.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import smx_constants as C
from smx_evaluation import (
    SCHLUESSEL_LISTE,
    VERFAHREN_LISTE,
    Settings,
    analyse,
    optimum_zeilen,
    referenz,
    verdict_aktuell,
    verdict_instanz,
    verdict_messung,
    verdict_optimum,
    verdict_tabelle,
    zeile,
)
from smx_layout import dunkles_design, kopf_css
from smx_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from smx_visualization import build_behaelter, build_messung

st.set_page_config(page_title="Packen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in smx_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Freiflächen verwalten: Skyline und MaxRects")
st.markdown(
    """
Stück 7 hat Rechtecke in **Regale** gezwungen. Hier verwaltet das Verfahren den **freien Platz** im Behälter: *Skyline* merkt sich die Oberkante der gesetzten Rechtecke, *MaxRects* die Liste aller größten freien Rechtecke. Zwei Fragen: **Was bringt das gegenüber dem Regal**, und **passt der Sortierschlüssel noch**, der beim Regal der beste war (die Höhe)? Die Demo zeigt an zwölf Rechtecken, wie der freie Platz Schritt für Schritt schrumpft, und an einem Messraster aus je 100 Zufallsinstanzen, wie viel an Verfahren und Schlüssel hängt.

Weiter unten: der Abschnitt **🔬 Experimente**, **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert Packen mit freiem Platz", expanded=True):
    st.markdown(
        """
1. **Schlüssel wählen:** Die Rechtecke werden in der Lieferreihenfolge genommen oder absteigend nach Höhe, Fläche oder Breite sortiert.
2. **Verfahren anwenden, Rechteck für Rechteck:** Das *Regal* setzt das Rechteck in die erste Zeile, in die es passt. *Skyline* setzt es an die niedrigste Stelle der Oberkante (bei Gleichstand links); was unter einem Überhang frei bleibt, ist verloren. *MaxRects* setzt es in die Ecke des freien Rechtecks, das nach einer Regel am besten passt: **BSSF** die kleinste kurze Restkante, **BAF** die kleinste Fläche, **BL** die unterste Position. Danach wird der freie Platz neu zerlegt. Passt es in keinen Behälter, wird ein neuer geöffnet.
3. **Schritt-Regler:** Mit dem Regler *Schritt* sehen Sie den Zustand nach den ersten k Rechtecken, samt freiem Platz (grün umrandet bei MaxRects, rote Linie bei Skyline, gestrichelte Zeilen beim Regal).
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Rechtecke**")
    quelle = st.selectbox("Instanz", list(C.QUELLEN), format_func=C.QUELLEN.get, key="quelle_select",
                          help="Die beiden Beispiele haben je zwölf feste Rechtecke. Die anderen vier sind Zufallsinstanzen mit verschiedener Verteilung der Maße.")
    n_index = st.selectbox("Zahl der Rechtecke (nur Zufallsinstanzen)", list(range(len(C.N_WERTE))), format_func=lambda i: str(C.N_WERTE[i]), key="n_select",
                           help="Gilt nur für Zufallsinstanzen.")
    seed = st.number_input("Startzahl der Zufallsinstanz", *bounds("seed_input"), key="seed_input", step=1,
                           help="Wirkt nur bei den Zufallsinstanzen.")
    st.button("🎲 Neue Zufallsinstanz würfeln", width="stretch", on_click=randomize_seed)
    st.markdown("**Packen**")
    schluessel = st.selectbox("Sortierschlüssel", list(C.SCHLUESSEL), format_func=C.SCHLUESSEL.get, key="schluessel_select",
                              help="Wonach die Rechtecke sortiert werden, absteigend. „Lieferreihenfolge“ sortiert nicht.")
    verfahren = st.selectbox("Verfahren", list(C.VERFAHREN), format_func=C.VERFAHREN.get, key="verfahren_select",
                             help="Wie der Platz im Behälter verwaltet wird und wohin das nächste Rechteck kommt.")
    schritt = st.number_input("Schritt (0 = alle Rechtecke)", *bounds("schritt_input"), key="schritt_input", step=1,
                              help="Zeigt den Zustand nach den ersten k Rechtecken in der Reihenfolge des Schlüssels. Größere Werte als die Zahl der Rechtecke zeigen alle.")

sync_query_params({"quelle_select": int(quelle), "n_select": int(n_index), "seed_input": int(seed), "schluessel_select": int(schluessel), "verfahren_select": int(verfahren),
                   "schritt_input": int(schritt)})

settings = Settings(int(quelle), int(n_index), int(seed), int(schluessel), int(verfahren), int(schritt))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3 = st.columns(3)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
if a.opt is not None:
    m1.metric("Behälter (ganze Packung)", a.count, delta=a.count - a.opt, delta_color="inverse", help="Delta: gewählte Behälterzahl minus Optimum.")
    m2.metric("Optimum (exakt, über alle Packungen)", a.opt, delta="Referenz", delta_color="off")
else:
    m1.metric("Behälter (ganze Packung)", a.count)
    m2.metric("Optimum", "nicht berechnet", delta="nur für die Beispiele", delta_color="off")
m3.metric("Untere Schranke", a.schranke, delta="Fläche oder große Rechtecke", delta_color="off")
flaeche = sum(w * h for w, h in a.inst.rects)
st.caption(f"{a.inst.n} Rechtecke, Gesamtfläche {flaeche} von {a.inst.cap * a.inst.cap} je Behälter. In Lieferreihenfolge brauchen sie mit dem gewählten Verfahren {a.liefer} Behälter.")
st.markdown(f"**Zustand nach {a.schritt} von {a.inst.n} Rechtecken:** jeder gestrichelte Rahmen ist ein Behälter, die Farbe zeigt die Reihenfolge des Setzens, die Zahl die Nummer des Rechtecks in der Lieferreihenfolge.")
st.plotly_chart(build_behaelter(a.inst.rects, a.platz, a.zustand, settings.verfahren, a.inst.cap), width="stretch", key="main_chart")
st.caption("Die Rechtecke sind maßstäblich. Grün umrandet: freie Rechtecke (MaxRects); rote Linie: Oberkante (Skyline); gestrichelte Zeilen: Regale. Was unter der roten Linie frei aussieht, ist für Skyline verloren.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was verändert die Behälterzahl mehr, das Verfahren oder der Sortierschlüssel?")
kind, text = verdict_aktuell(a)
getattr(st, kind)(text)

zeilen = ["| Schlüssel \\ Verfahren | " + " | ".join(C.VERFAHREN_KURZ[v] for v in VERFAHREN_LISTE) + " |", "|---|" + "---|" * len(VERFAHREN_LISTE)]
for k in SCHLUESSEL_LISTE:
    zellen = []
    for v in VERFAHREN_LISTE:
        wert = str(a.tabelle[k][v])
        zellen.append(f"**{wert}**" if (k, v) == (settings.schluessel, settings.verfahren) else wert)
    zeilen.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(zellen) + " |")
st.markdown("Behälterzahl der ganzen Packung für alle 20 Kombinationen (die gewählte ist fett):\n\n" + "\n".join(zeilen))
kind, text = verdict_tabelle(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experimente: Gilt das für viele Instanzen?")
st.caption(
    f"Gemessen an je {C.INSTANZEN} festen Zufallsinstanzen pro Zelle, Behälter {C.CAP} mal {C.CAP}, ganzzahlige Maße der Rechtecke ohne Drehung; dieselben Instanzen und Optima wie in Stück 7. "
    "Die Zahlen sind vorberechnet (`generate_precomputed.py`)."
)
e1, e2 = st.columns(2)
verteilung = e1.selectbox("Verteilung der Rechtecke", list(range(len(C.VERTEILUNGEN))), index=0, format_func=lambda i: C.VERTEILUNGEN[i][1], key="exp_verteilung")
ni = e2.selectbox("Zahl der Rechtecke n", list(range(len(C.MESS_N))), index=3, format_func=lambda i: str(C.MESS_N[i]), key="exp_n")
z = zeile(int(verteilung), int(ni))

st.markdown("### Experiment 1: Welcher Schlüssel zu welchem Verfahren?")
basis, mittel = referenz(z)
st.plotly_chart(build_messung(mittel, f"Behälter über {basis} (Mittel)"), width="stretch", key="exp_chart")
tab = ["| Schlüssel | " + " | ".join(C.VERFAHREN_KURZ[v] for v in VERFAHREN_LISTE) + " |", "|---|" + "---|" * len(VERFAHREN_LISTE)]
for k in SCHLUESSEL_LISTE:
    tab.append(f"| {C.SCHLUESSEL_KURZ[k]} | " + " | ".join(f"{mittel[k][v]:.2f}" for v in VERFAHREN_LISTE) + " |")
st.markdown("\n".join(tab))
st.caption(f"Mittlere Behälter über {basis}: Mittel über die Instanzen der Zelle" + (" (nur die entschiedenen)" if z["exakt"] else "") + ". Regal ist First Fit; Skyline, BSSF, BAF und BL sind die freien Verfahren.")
kind, text = verdict_messung(z)
getattr(st, kind)(text)

st.markdown("### Experiment 2: Instanz für Instanz und wie nah am Optimum")
kind, text = verdict_instanz(z)
getattr(st, kind)(text)
oz = optimum_zeilen()
tab2 = ["| Rechtecke | Regal | Skyline | MaxRects |", "|---|---|---|---|"]
for r in oz:
    f = lambda x: "-" if x is None else f"{x:.0f} %"  # noqa: E731
    offen = f", {r['offen']} offen" if r["offen"] else ""
    tab2.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} {r['n']}{offen} | {f(r['regal'])} | {f(r['skyline'])} | {f(r['maxrects'])} |")
st.markdown("\n".join(tab2))
st.caption(
    "Anteil der entschiedenen Instanzen, in denen die Kombination genau das Optimum braucht: Regal mit Höhe, Skyline mit Fläche, MaxRects BSSF mit Fläche (jeweils der Schlüssel, der meist am besten ist). "
    "„offen“ hinter dem Namen: Zahl der nicht entschiedenen Instanzen; die entschiedenen sind die leichteren. Das Optimum gilt über alle Packungen."
)
kind, text = verdict_optimum(oz)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist |
|---|---|
| **Keine Drehung** | Dürfen die Rechtecke gedreht werden, ändert sich die Aufgabe, und viele Verfahren nutzen das; die Demo misst es nicht. |
| **Nur diese Verfahren und Regeln** | Es gibt weitere Regeln (etwa „Berührungspunkt“ bei MaxRects) und andere Verfahren (Guillotine, Extreme Points). Die Demo vergleicht nur Regal, Skyline und drei MaxRects-Regeln. |
| **Die Maße sind zufällig verteilt** | Nur vier Verteilungen mit festen Bereichen sind gemessen. Andere Verteilungen können anders ausfallen. |
| **Die Schranke ist scharf** | In 2D ist sie locker; bei 40 und 80 Rechtecken fehlt das Optimum ganz, dort zählt nur der Vergleich der Kombinationen. |
| **Alle Rechtecke sind vor dem Packen bekannt** | Wer jedes Rechteck sofort einsortieren muss, kann nicht sortieren. Das ist Online-Packen. Mehr dazu: [Online](https://sebastianhanisch.net/konzepte-online-algorithmen.html). |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Rechtecke mit ganzzahliger Breite und Höhe und Behälter der Größe $C \times C$. *Gesucht:* eine überlappungsfreie Platzierung aller Rechtecke in möglichst wenigen Behältern, ohne Drehung.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Rechtecke |
| $w_i$, $h_i$ | Breite und Höhe von Rechteck $i$, $1 \le w_i, h_i \le C$ |
| $C$ | Seitenlänge eines Behälters |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Behältern über alle Platzierungen |
| $L$ | untere Schranke für $\mathrm{OPT}$ |

**Reihenfolge.** Ein Schlüssel ordnet jedem Rechteck eine Zahl $s_i$ zu: $h_i$, $w_i h_i$ oder $w_i$; die Rechtecke werden nach fallendem $s_i$ genommen, Gleichstände in der Lieferreihenfolge. Jedes Verfahren setzt die Rechtecke der Reihe nach, jedes kommt in den ersten Behälter, in dem es nach der Regel des Verfahrens passt, sonst in einen neuen; gesetzte Rechtecke bleiben liegen.

**Regal.** Zeilen der Höhe des ersten Rechtecks; ein Rechteck kommt auf die erste Zeile, auf der $h_i$ höchstens die Zeilenhöhe ist und die belegte Breite plus $w_i$ höchstens $C$ ergibt; sonst öffnet es eine neue Zeile über der letzten.

**Skyline.** Das Profil $p(x)$ ist die Oberkante der gesetzten Rechtecke über der Spalte $x$. Ein Rechteck der Breite $w$ liegt an der Stelle $x$ mit dem kleinsten $y = \max_{x \le u < x + w} p(u)$ (bei Gleichstand links), sofern $y + h \le C$; danach ist $p(u) = y + h$ für $x \le u < x + w$. Was unter $y$ zwischen den Spalten frei ist, wird nie wieder genutzt.

**MaxRects.** Der freie Platz eines Behälters ist die Menge $F$ der maximalen leeren Rechtecke (leer, und in keiner Richtung erweiterbar). Ein Rechteck $(w, h)$ passt in $f = (f_x, f_y, f_w, f_h) \in F$, wenn $w \le f_w$ und $h \le f_h$, und kommt an die linke untere Ecke von $f$. Die Wahl unter den passenden $f$: *BSSF* das kleinste Paar (kurze Restkante, lange Restkante) $= (\min(f_w - w, f_h - h), \max(f_w - w, f_h - h))$; *BAF* die kleinste Fläche $f_w f_h$ (dann BSSF); *BL* die kleinste Oberkante $f_y + h$ (dann links). Nach dem Setzen wird jedes überlappte $f$ in bis zu vier Teile links, rechts, unten und oben vom gesetzten Rechteck zerlegt, und Rechtecke, die in einem anderen enthalten sind, fallen weg; dann ist $F$ wieder genau die Menge der maximalen leeren Rechtecke.

**Schranken.** $L_{\mathrm{Fl}} = \left\lceil \tfrac{1}{C^2} \sum_i w_i h_i \right\rceil \le \mathrm{OPT}$. Rechtecke mit $w_i > C/2$ und $h_i > C/2$ („große“) enthalten in jedem Behälter den Mittelpunkt und überlappen deshalb paarweise; also $L_{\mathrm{gr}} = |\{ i : w_i > C/2, h_i > C/2 \}| \le \mathrm{OPT}$ und $L = \max(L_{\mathrm{Fl}}, L_{\mathrm{gr}})$.

**Exaktes Optimum** (Stück 7, nicht diese App). CP-SAT mit `NoOverlap2D` minimiert die Zahl benutzter Behälter; das Optimum gilt über alle Packungen. Es wird mit Herkunftsvermerk aus Stück 7 übernommen.

**Literatur** (Zusammenfassungen aus Suchtreffern, Originale nicht gelesen). Jylänki (2010) beschreibt in „A Thousand Ways to Pack the Bin“ MaxRects mit Regeln wie BL, BAF, BSSF und BLSF und Skyline-Verfahren. Die Demo übernimmt daraus keine Zahl, keine Gütegarantie und keine Aussage zu Dichte oder Geschwindigkeit.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
