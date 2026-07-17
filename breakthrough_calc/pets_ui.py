"""Pets tab (Qt only — every number comes from pets.py).

PetsPage renders the pet exchange planner: what you own in pets and rare
essences, and per pet the total copies/rarity reachable by going all-in on
it. The reasoning behind the recommendations lives in Guide → Pets.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QSpinBox, QVBoxLayout,
    QWidget,
)

from .i18n import tr
from .pets import plan


class PetsPage(QWidget):
    """The pet planner: spin boxes in, all-in projection table out."""

    changed = Signal()

    def __init__(self, catalog: dict, parent=None):
        super().__init__(parent)
        self.catalog = catalog
        self._pet_spins: dict[str, QSpinBox] = {}
        self._ess_spins: dict[str, QSpinBox] = {}

        v = QVBoxLayout(self)
        intro = QLabel(tr(
            "Enter what you own once; each pet row then shows the copies "
            "and rarity you could reach by going all-in on that pet."))
        intro.setWordWrap(True)
        v.addWidget(intro)

        row = QHBoxLayout()
        pets_box = QGroupBox(tr("Pets owned"))
        pf = QFormLayout(pets_box)
        for p in catalog.get("pets", []):
            sp = QSpinBox()
            sp.setRange(0, 999)
            sp.valueChanged.connect(self._on_edit)
            self._pet_spins[p["id"]] = sp
            pf.addRow(p["name"], sp)
        row.addWidget(pets_box, 1)

        ess_box = QGroupBox(tr("Rare essences owned"))
        ef = QFormLayout(ess_box)
        for e in catalog.get("essences", []):
            sp = QSpinBox()
            sp.setRange(0, 9999)
            sp.valueChanged.connect(self._on_edit)
            self._ess_spins[e["id"]] = sp
            ef.addRow(e["name"], sp)
        row.addWidget(ess_box, 1)
        v.addLayout(row)

        self._result = QLabel()
        self._result.setTextFormat(Qt.RichText)
        v.addWidget(self._result)
        hint = QLabel(tr("The Guide's Pets page explains which pet to pick "
                         "and why."))
        hint.setWordWrap(True)
        v.addWidget(hint)
        v.addStretch(1)
        self._refresh()

    def _on_edit(self, *_):
        self._refresh()
        self.changed.emit()

    def _refresh(self):
        pets = self.catalog.get("pets", [])
        if not pets:
            self._result.setText("")
            return
        st = self.state()
        plans = plan(self.catalog, st["owned"], st["essences"])
        h = (f"<h3>{tr('Going all-in on one pet')}</h3>"
             "<table cellpadding='4' cellspacing='0' border='1' "
             "style='border-collapse:collapse'><tr>"
             + "".join(f"<th>{c}</th>" for c in (
                 tr("Pet"), tr("Copies"), tr("Rarity"), tr("Pet realm")))
             + "</tr>")
        for p in pets:
            pl = plans[p["id"]]
            h += ("<tr>"
                  f"<td>{p['name']}</td>"
                  f"<td align='right'>{pl.copies}</td>"
                  f"<td>{pl.rarity or '—'}</td>"
                  f"<td>{pl.realm or '—'}</td>"
                  "</tr>")
        self._result.setText(h + "</table>")

    # ---- persistence (profile state, sibling of "shelf") -------------------
    def state(self) -> dict:
        return {
            "owned": {pid: sp.value()
                      for pid, sp in self._pet_spins.items() if sp.value()},
            "essences": {eid: sp.value()
                         for eid, sp in self._ess_spins.items() if sp.value()},
        }

    def set_state(self, st: dict | None):
        st = st or {}
        for spins, key in ((self._pet_spins, "owned"),
                           (self._ess_spins, "essences")):
            vals = st.get(key) or {}
            for sid, sp in spins.items():
                sp.blockSignals(True)
                try:
                    sp.setValue(int(vals.get(sid, 0)))
                except (TypeError, ValueError):
                    sp.setValue(0)
                sp.blockSignals(False)
        self._refresh()
