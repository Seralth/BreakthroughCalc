"""ProfileStore: settings file I/O, CRUD, and legacy migration.

ProfileStore handles the on-disk settings file (profiles, current selection,
app-level theme/lang) and migrates legacy v1 files -- a data-loss risk with
no coverage. Every test writes to a pytest tmp_path; the real settings file
is never touched.
"""

import json

import pytest

from breakthrough_calc.profiles import ProfileStore, settings_path


@pytest.fixture
def store(tmp_path):
    return ProfileStore(str(tmp_path / "settings.json"))


def test_roundtrip_persists_to_disk(tmp_path):
    path = str(tmp_path / "settings.json")
    state = {"culti_level": 42, "pill_rank": "5R", "nested": {"a": [1, 2, 3]}}

    ProfileStore(path).set("Default", state)

    # A fresh store reading the same file must see identical state.
    assert ProfileStore(path).get("Default") == state


def test_set_makes_profile_current(store):
    store.set("Alpha", {"x": 1})
    store.set("Beta", {"x": 2})
    assert store.current == "Beta"
    assert store.get("Alpha") == {"x": 1}
    assert store.get("Beta") == {"x": 2}


def test_first_write_keeps_the_implicit_default_profile(store):
    """A fresh file reads as a lone 'Default'; the first set() persists that
    seed alongside the new profile rather than dropping it."""
    store.set("A", {"n": 1})
    assert set(store.names()) == {"Default", "A"}


def test_multiple_profiles_are_independent(store):
    store.set("A", {"n": 1})
    store.set("B", {"n": 2})
    store.set("C", {"n": 3})
    assert {"A", "B", "C"}.issubset(set(store.names()))
    assert store.get("A") == {"n": 1}
    assert store.get("C") == {"n": 3}
    # Overwriting one leaves the others untouched.
    store.set("B", {"n": 99})
    assert store.get("B") == {"n": 99}
    assert store.get("A") == {"n": 1}


def test_current_setter_switches_without_touching_state(store):
    store.set("A", {"n": 1})
    store.set("B", {"n": 2})
    store.current = "A"
    assert store.current == "A"
    assert store.get("A") == {"n": 1}
    assert store.get("B") == {"n": 2}


def test_current_falls_back_when_stored_name_is_missing(tmp_path):
    path = str(tmp_path / "settings.json")
    # Hand-craft a store whose "current" points at a deleted profile.
    obj = {"version": 2, "current": "Ghost", "profiles": {"Real": {"n": 1}}}
    with open(path, "w") as f:
        json.dump(obj, f)
    assert ProfileStore(path).current == "Real"


def test_delete_returns_new_current_and_drops_profile(store):
    # Establish an exact two-profile file so the surviving name is determined.
    store.write({"version": 2, "current": "Drop",
                 "profiles": {"Keep": {"n": 1}, "Drop": {"n": 2}}})
    newcur = store.delete("Drop")
    assert newcur == "Keep"          # first remaining profile becomes current
    assert store.current == "Keep"
    assert "Drop" not in store.names()
    assert store.get("Keep") == {"n": 1}


def test_delete_last_profile_is_refused(store):
    store.write({"version": 2, "current": "Only",
                 "profiles": {"Only": {"n": 1}}})
    assert store.delete("Only") is None
    # The store always keeps at least one profile.
    assert store.names() == ["Only"]
    assert store.get("Only") == {"n": 1}


def test_missing_file_reads_as_empty_default(store):
    obj = store.read()
    assert obj["profiles"] == {"Default": {}}
    assert obj["current"] == "Default"
    assert store.names() == ["Default"]


def test_corrupt_file_reads_as_empty_default(tmp_path):
    path = str(tmp_path / "settings.json")
    with open(path, "w") as f:
        f.write("{ this is not valid json ")
    obj = ProfileStore(path).read()
    assert obj["profiles"] == {"Default": {}}
    assert obj["current"] == "Default"


def test_legacy_v1_flat_file_migrates_into_default_profile(tmp_path):
    """A pre-profiles settings file is one flat state dict with no 'profiles'
    key; read() must wrap it into a single 'Default' profile without loss."""
    path = str(tmp_path / "settings.json")
    legacy = {"culti_level": 7, "theme": "Seralth", "pill_rank": "3R"}
    with open(path, "w") as f:
        json.dump(legacy, f)

    store = ProfileStore(path)
    obj = store.read()
    assert obj["profiles"] == {"Default": legacy}
    assert obj["current"] == "Default"
    assert store.get("Default") == legacy


def test_writes_to_unwritable_path_are_swallowed(tmp_path):
    """The read-only-install contract: I/O errors never crash the app. A
    directory path makes open(..., 'w') raise OSError inside write()."""
    dir_path = tmp_path / "a_directory"
    dir_path.mkdir()
    store = ProfileStore(str(dir_path))
    # Neither of these may raise despite the un-openable path.
    store.set("Default", {"n": 1})
    store.write({"version": 2, "current": "Default", "profiles": {}})
    # And read() degrades gracefully to the empty default.
    assert store.read()["profiles"] == {"Default": {}}


def test_settings_path_prefers_portable_location_next_to_appimage(monkeypatch,
                                                                  tmp_path):
    """With APPIMAGE set to a writable dir, settings live next to the
    AppImage as '<name>.settings.json' -- no real user config is touched."""
    appimage = tmp_path / "BreakthroughCalc.AppImage"
    monkeypatch.setenv("APPIMAGE", str(appimage))
    result = settings_path()
    assert result == str(tmp_path / "BreakthroughCalc.AppImage.settings.json")
