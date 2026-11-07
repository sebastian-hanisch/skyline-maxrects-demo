"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen, jeder Hilfetext stimmt mit der Rechnung überein."""

import smx_algorithm as A
import smx_constants as C
import smx_evaluation as ev
import smx_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_widget_bounds():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            assert spec.lo <= preset[key] <= spec.hi, (name, key)


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_defaults_of_the_widgets_equal_the_default_settings():
    s = ev.Settings()
    schluessel = ("quelle_select", "n_select", "seed_input", "schluessel_select", "verfahren_select", "schritt_input")
    assert [P.SETTING_SPECS[k].default for k in schluessel] == [s.quelle, s.n_index, s.seed, s.schluessel, s.verfahren, s.schritt]


def _a(name, **aender):
    return ev.analyse(ev.Settings(**{**C.PRESETS[name], **aender}))


def test_presets_behaupten_nur_was_stimmt():
    eins = _a("Beispiel 1, Höhe, Regal")
    assert eins.count == 4 and "der beste Regalplan braucht vier Behälter" in C.PRESET_HELP["Beispiel 1, Höhe, Regal"]
    # ... und es ist der beste Regalplan: kein Schlüssel ist mit dem Regal besser
    assert min(A.anzahl(eins.inst.rects, k, 0, 100) for k in range(4)) == 4
    zwei = _a("Beispiel 1, Fläche, MaxRects BSSF")
    assert zwei.count == 3 == zwei.opt and "drei Behälter, so viele wie das Optimum" in C.PRESET_HELP["Beispiel 1, Fläche, MaxRects BSSF"]
    drei = _a("Beispiel 2, Fläche, MaxRects BSSF")
    assert drei.count == 2 == drei.opt and "findet nur diese das Optimum" in C.PRESET_HELP["Beispiel 2, Fläche, MaxRects BSSF"]
    assert [(k, v) for k in range(4) for v in range(5) if drei.tabelle[k][v] == 2] == [(2, 2)]
    vier = _a("Beispiel 1, Fläche, Skyline, Schritt 5")
    assert vier.schritt == 5 and len(vier.platz) == 5 and "Skyline nach dem fünften Rechteck" in C.PRESET_HELP["Beispiel 1, Fläche, Skyline, Schritt 5"]
    assert all(A.packung_pruefen(x.inst.rects, x.platz, x.inst.cap, vollstaendig=False) for x in (eins, zwei, drei, vier))
