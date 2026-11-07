"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import smx_constants as C

ABSTAND = 8     # Platz zwischen zwei Behältern in der Zeichnung


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def profil_linie(profil, x0):
    """Oberkante eines Höhenprofils als Treppenlinie (x, y): ein Punkt am Anfang und am Ende jedes Abschnitts gleicher Höhe."""
    xs, ys = [], []
    start = 0
    for k in range(1, len(profil) + 1):
        if k == len(profil) or profil[k] != profil[start]:
            xs += [x0 + start, x0 + k]
            ys += [profil[start], profil[start]]
            start = k
    return xs, ys


def build_behaelter(rects, platz, zustand, verfahren, cap):
    """Alle Behälter nebeneinander, jedes Rechteck an seiner Stelle; die Farbe zeigt die Reihenfolge des Setzens, die Beschriftung die Teilenummer (Lieferreihenfolge).

    Darüber die Freiflächen des Verfahrens: bei MaxRects die freien Rechtecke (grün umrandet), bei Skyline die Oberkante des Höhenprofils (rote Linie), beim Regal die Regale (grau gestrichelt).
    Die Behälterrahmen sind rot gestrichelt. Das Achsenverhältnis ist 1 : 1, damit die Rechtecke maßstäblich sind."""
    anzahl = max(len(zustand), 1)
    shapes = []
    for b in range(anzahl):
        x0 = b * (cap + ABSTAND)
        shapes.append(dict(type="rect", x0=x0, y0=0, x1=x0 + cap, y1=cap, line=dict(color=C.COLOR_LINE, width=2, dash="dash"), fillcolor="rgba(0,0,0,0)"))
    fig = go.Figure()
    for s, (i, b, x, y) in enumerate(platz):
        w, h = rects[i]
        x0 = b * (cap + ABSTAND) + x
        shapes.append(dict(type="rect", x0=x0, y0=y, x1=x0 + w, y1=y + h, line=dict(color="white", width=1.5), fillcolor=C.REGAL_FARBEN[s % len(C.REGAL_FARBEN)], opacity=0.85))
    if verfahren == 0:
        for b, regale in enumerate(zustand):
            for y, h, _belegt in regale:
                x0 = b * (cap + ABSTAND)
                shapes.append(dict(type="rect", x0=x0, y0=y, x1=x0 + cap, y1=y + h, line=dict(color="rgba(128,128,128,0.8)", width=1, dash="dot"), fillcolor="rgba(0,0,0,0)"))
    elif verfahren >= 2:
        for b, frei in enumerate(zustand):
            for fx, fy, fw, fh in frei:
                x0 = b * (cap + ABSTAND) + fx
                shapes.append(dict(type="rect", x0=x0, y0=fy, x1=x0 + fw, y1=fy + fh, line=dict(color=C.COLOR_FREI, width=1.5), fillcolor="rgba(47,107,101,0.10)"))
    fig.add_trace(go.Scatter(x=[b * (cap + ABSTAND) + x + rects[i][0] / 2 for i, b, x, y in platz], y=[y + rects[i][1] / 2 for i, b, x, y in platz], mode="text",
                             text=[str(i + 1) for i, *_ in platz], textfont=dict(color="white", size=11),
                             hovertext=[f"Schritt {s + 1}: Teil {i + 1}, {rects[i][0]} × {rects[i][1]}, Behälter {b + 1}, links unten ({x}, {y})" for s, (i, b, x, y) in enumerate(platz)], hoverinfo="text", showlegend=False))
    if verfahren == 1:
        for b, profil in enumerate(zustand):
            xs, ys = profil_linie(profil, b * (cap + ABSTAND))
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_PROFIL, width=3), hoverinfo="skip", showlegend=False))
    fig.update_layout(shapes=shapes)
    breite = anzahl * (cap + ABSTAND) - ABSTAND
    fig.update_xaxes(range=[-2, breite + 2], constrain="domain", showgrid=False, zeroline=False, tickmode="array", tickvals=[b * (cap + ABSTAND) + cap / 2 for b in range(anzahl)],
                     ticktext=[f"B{b + 1}" for b in range(anzahl)])
    fig.update_yaxes(range=[-2, cap + 2], constrain="domain", showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1, title_text="Höhe")
    return _base(fig, 340)


def build_messung(werte, titel):
    """Mittlere Behälter über der Vergleichsbasis: je Schlüssel fünf Balken (die Verfahren); werte = {Schlüssel: {Verfahren: Wert}}."""
    fig = go.Figure()
    schluessel = sorted(werte)
    namen = [C.SCHLUESSEL_KURZ[k] for k in schluessel]
    for v in sorted(werte[schluessel[0]]):
        zahlen = [werte[k][v] for k in schluessel]
        fig.add_trace(go.Bar(name=C.VERFAHREN_KURZ[v], x=namen, y=zahlen, marker_color=C.VERFAHREN_FARBEN[v], text=[f"{w:.2f}" for w in zahlen], textposition="outside", cliponaxis=False,
                             hovertemplate="%{x}, " + C.VERFAHREN_KURZ[v] + ": %{y:.2f}<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text=titel)
    return _base(fig, 380)
