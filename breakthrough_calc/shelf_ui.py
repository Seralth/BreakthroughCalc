"""Sources Shelf widgets (Qt only — every number comes from shelf.py).

ShelfPage renders the catalog as set-once ownership controls and emits
`changed`; ProvenanceChip decorates an input field with the shelf's derived
value for its target and toggles the field between manual (default — the
user types, chip is informational) and auto (field read-only, shelf-driven).
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSpinBox, QTabWidget, QVBoxLayout, QWidget,
)

from .i18n import tr
from .shelf import Derived


class ProvenanceChip(QPushButton):
    """Compact "shelf: 14 · 3 sources" button beside an input field.

    Click toggles auto mode for the field. The chip only RENDERS state the
    MainWindow hands it; it owns no derivation."""

    toggled_auto = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self._auto = False
        self.clicked.connect(self._flip)
        self.update_view(None, False)

    def _flip(self):
        self._auto = not self._auto
        self.toggled_auto.emit(self._auto)

    def update_view(self, derived: Derived | None, auto: bool,
                    display_total: float | None = None):
        self._auto = auto
        total = display_total if display_total is not None else (
            derived.total if derived else 0.0)
        n = len(derived.contributions) + len(derived.custom) if derived else 0
        prefix = tr("auto") if auto else tr("shelf")
        approx = "≥" if derived is not None and derived.incomplete else ""
        self.setText(f"{prefix}: {approx}{total:g} · {n}")
        lines = []
        if derived:
            for c in derived.contributions:
                lvl = f" ({c.level_label})" if c.level_label else ""
                mark = "" if c.data_status == "exact" else " *"
                lines.append(f"{c.name}{lvl}: +{c.value:g}{mark}")
            for label, value in derived.custom:
                lines.append(f"{label}: +{value:g}")
            if derived.incomplete:
                lines.append(tr("Some owned sources have unrecorded amounts."))
        state = tr("Click to let the shelf fill this field.") if not auto \
            else tr("Shelf-managed. Click to edit manually.")
        self.setToolTip("\n".join(lines + [state]) if lines else state)


class _SourceRow(QWidget):
    """One catalog entry: ownership controls per its levels.kind."""

    changed = Signal()

    def __init__(self, entry: dict, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.kind = entry["levels"]["kind"]
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        self._spins: list = []
        self._check = None
        self._combo = None
        notes = [e.get("note", "") for e in entry["effects"] if e.get("note")]
        if entry.get("note"):
            notes.append(entry["note"])
        tip = "\n".join(notes)

        if self.kind in ("binary", "custom"):
            self._check = QCheckBox(entry["name"])
            self._check.toggled.connect(self._on_edit)
            h.addWidget(self._check, 1)
            if self.kind == "custom":
                for p in entry["levels"]["params"]:
                    h.addWidget(QLabel(tr(p["label"])))
                    sp = QSpinBox()
                    sp.setRange(p["min"], p["max"])
                    sp.valueChanged.connect(self._on_edit)
                    self._spins.append(sp)
                    h.addWidget(sp)
        else:
            h.addWidget(QLabel(entry["name"]), 1)
            if self.kind == "ladder":
                self._combo = QComboBox()
                self._combo.addItem("—")
                for label in entry["levels"]["labels"]:
                    self._combo.addItem(label)
                self._combo.currentIndexChanged.connect(self._on_edit)
                h.addWidget(self._combo)
            else:
                sp = QSpinBox()
                mx = entry["levels"].get("max")
                sp.setRange(0, mx if isinstance(mx, int) else 999)
                sp.setSpecialValueText("—")
                if self.kind == "tier":
                    sp.setPrefix(tr("Tier "))
                sp.valueChanged.connect(self._on_edit)
                self._spins.append(sp)
                h.addWidget(sp)
                if self.kind == "level":
                    self._check = QCheckBox(tr("Maxed"))
                    self._check.toggled.connect(self._on_edit)
                    h.addWidget(self._check)
        if tip:
            self.setToolTip(tip)

    def _on_edit(self, *_):
        if self.kind == "level" and self._check is not None:
            self._spins[0].setEnabled(not self._check.isChecked())
        if self.kind == "custom":
            for sp in self._spins:
                sp.setEnabled(self._check.isChecked())
        self.changed.emit()

    def owned(self):
        """The owned level in shelf semantics, or None when not owned."""
        if self.kind == "binary":
            return 1 if self._check.isChecked() else None
        if self.kind == "custom":
            if not self._check.isChecked():
                return None
            return [sp.value() for sp in self._spins]
        if self.kind == "ladder":
            i = self._combo.currentIndex()
            return i if i > 0 else None
        if self.kind == "level" and self._check.isChecked():
            return -1
        v = self._spins[0].value()
        return v if v > 0 else None

    def set_owned(self, value):
        for w in ([self._check] if self._check else []) + self._spins:
            w.blockSignals(True)
        if self._combo is not None:
            self._combo.blockSignals(True)
        try:
            if self.kind == "binary":
                self._check.setChecked(value is not None)
            elif self.kind == "custom":
                self._check.setChecked(value is not None)
                if isinstance(value, list):
                    for sp, v in zip(self._spins, value):
                        sp.setValue(int(v))
                for sp in self._spins:
                    sp.setEnabled(value is not None)
            elif self.kind == "ladder":
                self._combo.setCurrentIndex(int(value) if value else 0)
            elif self.kind == "level":
                maxed = value == -1
                self._check.setChecked(maxed)
                self._spins[0].setValue(0 if value is None or maxed else int(value))
                self._spins[0].setEnabled(not maxed)
            else:
                self._spins[0].setValue(int(value) if value else 0)
        finally:
            for w in ([self._check] if self._check else []) + self._spins:
                w.blockSignals(False)
            if self._combo is not None:
                self._combo.blockSignals(False)


def _star_marker(entry: dict, row: _SourceRow) -> None:
    if entry.get("data_status") != "exact":
        star = QLabel("*")
        star.setToolTip(tr("Amounts not exactly established."))
        lay = row.layout()
        lay.insertWidget(lay.count(), star)


class _BookRow(_SourceRow):
    """A Library book: the tier control plus chapter dots (one per bonus
    threshold, filled while the owned tier reaches it)."""

    def __init__(self, entry: dict, parent=None):
        super().__init__(entry, parent)
        self._thresholds = sorted({e.get("min_level", 1)
                                   for e in entry.get("effects", [])})
        self._dots = QLabel()
        self.layout().addWidget(self._dots)
        self.changed.connect(self._update_dots)
        self._update_dots()

    def _update_dots(self):
        owned = self.owned()
        lvl = None if owned is None else (10**9 if owned == -1 else owned)
        marks = []
        for ml in self._thresholds:
            on = lvl is not None and (
                lvl >= (ml if isinstance(ml, int) else 10**9))
            marks.append("●" if on else "○")
        self._dots.setText(" ".join(marks))

    def set_owned(self, value):
        super().set_owned(value)
        self._update_dots()


class _RowsPane(QWidget):
    """A scroll-friendly pane of _SourceRows for the given categories,
    grouped by category label."""

    changed = Signal()

    def __init__(self, catalog: dict, categories: tuple, parent=None):
        super().__init__(parent)
        self.rows: dict[str, _SourceRow] = {}
        v = QVBoxLayout(self)
        by_cat: dict[str, list] = {}
        for s in catalog.get("sources", []):
            by_cat.setdefault(s["category"], []).append(s)
        for cat in catalog.get("categories", []):
            if cat["id"] not in categories:
                continue
            entries = by_cat.get(cat["id"])
            if not entries:
                continue
            box = QGroupBox(tr(cat["label"]))
            bv = QVBoxLayout(box)
            for entry in entries:
                row = _SourceRow(entry)
                _star_marker(entry, row)
                row.changed.connect(self.changed)
                self.rows[entry["id"]] = row
                bv.addWidget(row)
            v.addWidget(box)
        v.addStretch(1)


class _LibraryPane(QWidget):
    """The Universal bookshelf: technique books grouped into rank shelves
    (R1 … R9), each book with a tier control and chapter dots. A second
    Exclusive shelf is a placeholder until those manuals are recorded."""

    changed = Signal()

    def __init__(self, catalog: dict, parent=None):
        super().__init__(parent)
        self.rows: dict[str, _SourceRow] = {}
        v = QVBoxLayout(self)
        intro = QLabel(tr(
            "Set each book's tier once; the bonuses it has unlocked flow to "
            "the calculator on their own. Dots show the book's chapter "
            "bonuses: filled ones are active at your tier."))
        intro.setWordWrap(True)
        v.addWidget(intro)
        tabs = QTabWidget()
        v.addWidget(tabs)

        universal = QWidget()
        uv = QVBoxLayout(universal)
        books = [s for s in catalog.get("sources", [])
                 if s["category"] == "technique_book"]
        by_rank: dict[str, list] = {}
        for b in books:
            by_rank.setdefault(b.get("rank", "?"), []).append(b)
        for rank in sorted(by_rank, key=lambda r: (len(r), r)):
            shelf = QGroupBox(rank)
            sv = QVBoxLayout(shelf)
            for entry in by_rank[rank]:
                row = _BookRow(entry)
                _star_marker(entry, row)
                row.changed.connect(self.changed)
                self.rows[entry["id"]] = row
                sv.addWidget(row)
            uv.addWidget(shelf)
        uv.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(universal)
        tabs.addTab(scroll, tr("Universal"))

        exclusive = QLabel(tr(
            "Exclusive technique manuals give combat stats only, so they "
            "are not tracked yet. This shelf will fill in later."))
        exclusive.setWordWrap(True)
        exclusive.setAlignment(Qt.AlignTop)
        exclusive.setMargin(12)
        tabs.addTab(exclusive, tr("Exclusive"))


class ShelfPage(QWidget):
    """The Vault: set-once ownership home. Library (technique books on rank
    shelves), Treasury (curios), Companions (immortal friends + blessings)
    with the residual-base inputs for targets whose field is base + shelf
    contributions. Same owned()/bases()/set_state API the MainWindow has
    always used."""

    changed = Signal()

    def __init__(self, catalog: dict, parent=None):
        super().__init__(parent)
        self.catalog = catalog
        v = QVBoxLayout(self)
        intro = QLabel(tr(
            "Record what you own once; fields with a shelf chip can then "
            "fill themselves. Entries marked * carry amounts that are not "
            "exactly established."))
        intro.setWordWrap(True)
        v.addWidget(intro)

        bases = QGroupBox(tr("Base values (before sources)"))
        bh = QHBoxLayout(bases)
        self.base_respira = QDoubleSpinBox()
        self.base_respira.setRange(0, 1e5)
        self.base_respira.setValue(10)
        self.base_respira.setToolTip(tr(
            "Daily Respira attempts before any owned source. The game "
            "grants 10 by default."))
        self.base_pills = QDoubleSpinBox()
        self.base_pills.setRange(0, 1e5)
        self.base_pills.setToolTip(tr(
            "Daily pill limit before any owned source."))
        bh.addWidget(QLabel(tr("Respira attempts / day")))
        bh.addWidget(self.base_respira)
        bh.addWidget(QLabel(tr("Daily pill limit")))
        bh.addWidget(self.base_pills)
        bh.addStretch(1)
        self.base_respira.valueChanged.connect(self.changed)
        self.base_pills.valueChanged.connect(self.changed)
        v.addWidget(bases)

        self._panes = [
            (_LibraryPane(catalog), tr("Library")),
            (_RowsPane(catalog, ("curio",)), tr("Treasury")),
            (_RowsPane(catalog, ("immortal_friend", "blessing", "other")),
             tr("Companions")),
        ]
        tabs = QTabWidget()
        self._rows: dict[str, _SourceRow] = {}
        for pane, label in self._panes:
            pane.changed.connect(self.changed)
            self._rows.update(pane.rows)
            tabs.addTab(pane, label)
        v.addWidget(tabs, 1)

    def owned(self) -> dict:
        out = {}
        for sid, row in self._rows.items():
            val = row.owned()
            if val is not None:
                out[sid] = val
        return out

    def bases(self) -> dict:
        return {"respira_attempts": self.base_respira.value(),
                "pill_attempts": self.base_pills.value()}

    def set_state(self, owned: dict, bases: dict):
        for sid, row in self._rows.items():
            row.set_owned(owned.get(sid))
        for widget, key, default in (
                (self.base_respira, "respira_attempts", 10.0),
                (self.base_pills, "pill_attempts", 0.0)):
            widget.blockSignals(True)
            widget.setValue(float(bases.get(key, default)))
            widget.blockSignals(False)
