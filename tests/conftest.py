"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smx_scenario import Instance  # noqa: E402


@pytest.fixture
def mini():
    """Vier Rechtecke (Breite, Höhe) = (6, 4), (5, 3), (4, 5), (4, 2) mit den Nummern 0 bis 3, Behälter 10 mal 10, Fläche 69, Schranke 1.

    Von Hand gerechnet (Details in tests/test_algorithm.py): Das Regal braucht 2 Behälter, Skyline und MaxRects je 1."""
    return Instance(((6, 4), (5, 3), (4, 5), (4, 2)), 10)
