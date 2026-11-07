"""Kern der Demo (nur Standardbibliothek): Sortierschlüssel, die Verfahren Regal, Skyline und MaxRects, Schranken und der unabhängige Prüfer.

Ein Behälter ist `cap` mal `cap`. Rechtecke kommen in der Reihenfolge `order` und liegen danach fest; jedes Rechteck kommt in den ersten Behälter, in dem es nach der Regel des Verfahrens
passt, sonst in einen neuen. Packungen sind Listen von Behältern (je Behälter die Teilenummern, Index in der Lieferreihenfolge), Platzierungen (Teil, Behälter, x, y) mit der linken unteren
Ecke und der Zustand je Behälter (Regale, Höhenprofil oder freie Rechtecke), mit dem die App die Freiflächen zeigt."""


def schluessel_wert(rects, schluessel: int):
    """Sortierzahlen der Rechtecke (größer = früher); `None` bei der Lieferreihenfolge. 1 Höhe, 2 Fläche, 3 Breite."""
    if schluessel == 0:
        return None
    if schluessel == 1:
        return [h for _, h in rects]
    if schluessel == 2:
        return [w * h for w, h in rects]
    if schluessel == 3:
        return [w for w, _ in rects]
    raise ValueError(f"Schlüssel {schluessel!r} unbekannt")


def reihenfolge(rects, schluessel: int) -> list:
    """Teilenummern in der Reihenfolge, in der gepackt wird: absteigend nach der Sortierzahl; Gleichstände bleiben in der Lieferreihenfolge."""
    z = schluessel_wert(rects, schluessel)
    if z is None:
        return list(range(len(rects)))
    return sorted(range(len(rects)), key=lambda i: (-z[i], i))


def _regal_setzen(regale, bins, platz, i, w, h, cap):
    """Regal, erstes passendes: gibt True zurück, wenn das Rechteck gesetzt wurde. Regal = [y, Höhe, belegte Breite]; ein Rechteck passt, wenn es nicht höher ist als das Regal und die Breite reicht;
    sonst neues Regal direkt über dem letzten im ersten Behälter mit genug Resthöhe."""
    for b in range(len(regale)):
        for sh in regale[b]:
            if h <= sh[1] and sh[2] + w <= cap:
                platz.append((i, b, sh[2], sh[0]))
                bins[b].append(i)
                sh[2] += w
                return True
    for b in range(len(regale)):
        oben = regale[b][-1][0] + regale[b][-1][1]
        if oben + h <= cap:
            regale[b].append([oben, h, w])
            bins[b].append(i)
            platz.append((i, b, 0, oben))
            return True
    return False


def _skyline_setzen(profile, bins, platz, i, w, h, cap):
    """Skyline: im ersten Behälter, in dem es passt, an die niedrigste Stelle (bei Gleichstand die linkeste). Ein Rechteck liegt auf dem höchsten Punkt des Profils unter seiner Breite;
    Höhlen darunter gehen verloren."""
    for b, prof in enumerate(profile):
        beste = None
        for x in range(0, cap - w + 1):
            y = max(prof[x:x + w])
            if y + h <= cap and (beste is None or y < beste[0]):
                beste = (y, x)
        if beste is not None:
            y, x = beste
            for k in range(x, x + w):
                prof[k] = y + h
            platz.append((i, b, x, y))
            bins[b].append(i)
            return True
    return False


def _maximal(frei):
    """Entfernt freie Rechtecke, die in einem anderen enthalten sind (bei Gleichheit bleibt das erste)."""
    behalten = []
    for i, a in enumerate(frei):
        if any(j != i and b[0] <= a[0] and b[1] <= a[1] and a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3] and (b != a or j < i) for j, b in enumerate(frei)):
            continue
        behalten.append(a)
    return behalten


def _maxrects_setzen(behaelter, bins, platz, i, w, h, cap, regel):
    """MaxRects: im ersten Behälter, der ein freies Rechteck für das Teil hat, an die Ecke (links unten) des nach der Regel besten freien Rechtecks. bssf: kleinste kurze Restkante, dann
    kleinste lange; baf: kleinste Fläche des freien Rechtecks, dann bssf; bl: niedrigste Oberkante, dann linkeste Position. Danach wird jedes freie Rechteck, das das gesetzte überlappt,
    in bis zu vier Teile zerlegt und die Liste auf die maximalen Rechtecke gekürzt."""
    wahl = None
    for b, frei in enumerate(behaelter):
        for (fx, fy, fw, fh) in frei:
            if w <= fw and h <= fh:
                kurz, lang = min(fw - w, fh - h), max(fw - w, fh - h)
                if regel == "bssf":
                    score = (kurz, lang, fy, fx)
                elif regel == "baf":
                    score = (fw * fh, kurz, fy, fx)
                else:
                    score = (fy + h, fx, kurz, lang)
                if wahl is None or score < wahl[0]:
                    wahl = (score, b, fx, fy)
        if wahl is not None:
            break
    if wahl is None:
        behaelter.append([(0, 0, cap, cap)])
        bins.append([])
        wahl = (None, len(behaelter) - 1, 0, 0)
    _, b, px, py = wahl
    platz.append((i, b, px, py))
    bins[b].append(i)
    neu = []
    for (fx, fy, fw, fh) in behaelter[b]:
        if px >= fx + fw or px + w <= fx or py >= fy + fh or py + h <= fy:
            neu.append((fx, fy, fw, fh))
            continue
        if px > fx:
            neu.append((fx, fy, px - fx, fh))
        if px + w < fx + fw:
            neu.append((px + w, fy, fx + fw - px - w, fh))
        if py > fy:
            neu.append((fx, fy, fw, py - fy))
        if py + h < fy + fh:
            neu.append((fx, py + h, fw, fy + fh - py - h))
    behaelter[b] = _maximal(neu)
    return True


def pack(rects, order, cap: int, verfahren: int):
    """Rechtecke in der Reihenfolge `order` packen (`order` darf nur einen Anfang der Reihenfolge enthalten: jedes Verfahren arbeitet Rechteck für Rechteck, der Anfang liefert den Zustand
    nach so vielen Schritten). Verfahren 0 Regal (erstes passendes), 1 Skyline, 2 bis 4 MaxRects (BSSF, BAF, BL). Gibt (bins, platz, zustand) zurück: bins[b] = Teilenummern des Behälters in der
    Reihenfolge des Setzens, platz = Liste (Teil, Behälter, x, y), zustand[b] = Regale [y, Höhe, belegte Breite] (Regal), Höhenprofil je Spalte (Skyline) oder freie Rechtecke (x, y, w, h) (MaxRects)."""
    if verfahren not in (0, 1, 2, 3, 4):
        raise ValueError(f"Verfahren {verfahren!r} unbekannt")
    order = list(order)
    if len(set(order)) != len(order) or any(not 0 <= i < len(rects) for i in order):
        raise ValueError("die Reihenfolge darf jedes Rechteck höchstens einmal enthalten")
    for t in rects:
        if len(t) != 2 or any(x <= 0 or x > cap for x in t):
            raise ValueError(f"Rechteck {t!r} ungültig (zwei Maße, je 1 bis {cap})")
    zustand, bins, platz = [], [], []
    for i in order:
        w, h = rects[i]
        if verfahren == 0:
            gesetzt = _regal_setzen(zustand, bins, platz, i, w, h, cap)
            if not gesetzt:
                zustand.append([[0, h, w]])
                bins.append([i])
                platz.append((i, len(zustand) - 1, 0, 0))
        elif verfahren == 1:
            gesetzt = _skyline_setzen(zustand, bins, platz, i, w, h, cap)
            if not gesetzt:
                prof = [0] * cap
                for k in range(w):
                    prof[k] = h
                zustand.append(prof)
                bins.append([i])
                platz.append((i, len(zustand) - 1, 0, 0))
        else:
            _maxrects_setzen(zustand, bins, platz, i, w, h, cap, {2: "bssf", 3: "baf", 4: "bl"}[verfahren])
    return bins, platz, zustand


def anzahl(rects, schluessel: int, verfahren: int, cap: int) -> int:
    return len(pack(rects, reihenfolge(rects, schluessel), cap, verfahren)[0])


def packung_pruefen(rects, platz, cap: int, vollstaendig: bool = True) -> bool:
    """Unabhängiger Prüfer: jedes Rechteck höchstens einmal (bei `vollstaendig` genau einmal), ganz im Behälter, keine zwei Rechtecke eines Behälters überlappen."""
    nummern = sorted(p[0] for p in platz)
    if vollstaendig and nummern != list(range(len(rects))):
        return False
    if len(set(nummern)) != len(nummern) or any(not 0 <= i < len(rects) for i in nummern):
        return False
    je = {}
    for i, b, x, y in platz:
        w, h = rects[i]
        if x < 0 or y < 0 or x + w > cap or y + h > cap:
            return False
        je.setdefault(b, []).append((x, y, x + w, y + h))
    for lst in je.values():
        for a in range(len(lst)):
            for c in range(a + 1, len(lst)):
                p, q = lst[a], lst[c]
                if p[0] < q[2] and q[0] < p[2] and p[1] < q[3] and q[1] < p[3]:
                    return False
    return True


def schranken(rects, cap: int):
    """(Flächenschranke, Zahl der großen Rechtecke, Schranke): die Fläche aller Rechtecke durch die Behälterfläche aufgerundet; die Zahl der Rechtecke, die in beiden Maßen
    über die Hälfte reichen (zwei solche überlappen in jedem Behälter über dem Mittelpunkt, jedes braucht also einen eigenen Behälter); das Größere von beiden."""
    flaeche = -(-sum(w * h for w, h in rects) // (cap * cap))
    gross = sum(1 for w, h in rects if 2 * w > cap and 2 * h > cap)
    return flaeche, gross, max(flaeche, gross)


def schranke(rects, cap: int) -> int:
    return schranken(rects, cap)[2]
