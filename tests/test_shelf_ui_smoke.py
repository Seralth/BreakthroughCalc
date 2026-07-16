"""Offscreen end-to-end smoke of the desktop Sources Shelf.

Requires PySide6 (skipped where unavailable — CI's python job installs only
pytest; the Qt path is exercised on dev machines). Uses an isolated settings
file so real profiles are never touched.
"""

import os

import pytest

PySide6 = pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

import breakthrough_calc.gui as gui  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture()
def window(app, tmp_path, monkeypatch):
    monkeypatch.setattr(gui, "settings_path",
                        lambda: str(tmp_path / "settings.json"))
    w = gui.MainWindow()
    yield w
    w.deleteLater()


def test_shelf_auto_fields_and_pe_auto_rows(window):
    w = window
    w.shelf_page._rows["purify_cleanse"].set_owned(9)
    w.shelf_page._rows["six_eared_macaque"].set_owned(17)
    w.shelf_page._rows["chroma"].set_owned(12)
    w._on_shelf_changed()
    w.virya.setCurrentIndex(3)
    for key in ("bless_pp", "bless_window", "pill_limit"):
        w._set_shelf_auto(key, True)
    assert w.bless_pp.value() == 40           # 0.20 + 0.20, percent widget
    assert w.bless_window.value() == 20
    assert w.pill_limit.value() == 1          # base 0 + Chroma Tier 12
    assert w.pe_rows.total() == 4             # Chroma +1 and +3 auto rows
    # Respira self-fill: attempts = base 10 + Purify T6 + Chroma T3, and
    # Base EXP = Stage estimate x (1 + 14% books) once the stage has one.
    assert w.respira_per_day.value() == 12.0
    from breakthrough_calc.labels import stage_disp
    w.stage.setCurrentText(stage_disp("Nascent"))
    assert w.respira_exp.value() == round(3157 * 1.14)  # 4+7 books +3 friend
    # a manual entry sticks through further changes; clearing restores
    w.respira_per_day.setValue(15.0)
    w.recalc()
    assert w.respira_per_day.value() == 15.0
    w.respira_per_day.setValue(0.0)
    w.recalc()
    assert w.respira_per_day.value() == 12.0


def test_shelf_state_round_trips_through_profiles(window):
    w = window
    w.shelf_page._rows["chroma"].set_owned(6)
    w._on_shelf_changed()
    state = w._collect_state()
    w._apply_state(state)
    assert w._shelf["owned"] == {"chroma": 6}


def test_legacy_profile_migrates_once_with_identical_values(window):
    w = window
    state = w._collect_state()
    legacy = {k: v for k, v in state.items() if k != "shelf"}
    legacy["pill_sources"] = [["Chroma (R8 technique)", 4.0],
                              ["My custom", 2.0]]
    legacy["respira_sources"] = ["Daji (immortal friend, lv 73)"]
    legacy["respira_per_day"] = 12.0
    w._apply_state(legacy)
    assert sorted(w._shelf["owned"]) == ["chroma", "daji"]
    # Chroma implied at tier 6 also grants its tier-3 Respira attempt, so the
    # rebase subtracts daji(1) + chroma(1); the field value must not move.
    assert w._shelf["bases"] == {"respira_attempts": 10.0,
                                 "pill_attempts": 0.0}
    assert w.respira_per_day.value() == 12.0
    manual = w.pe_rows.sources()
    assert ["My custom", 2.0] in manual
    assert not any(label == "Chroma (R8 technique)" for label, _ in manual)
    assert abs(w.pe_rows.total() - 6.0) < 1e-9   # auto 4 + custom 2
    assert w._shelf["auto"] == ["pill_limit", "respira_per_day"]
    # and the engine receives the same numbers through the registry
    inp = w._inputs()
    assert abs(inp.pill_effect - 0.06) < 1e-9
    assert inp.respira_per_day == 12.0
