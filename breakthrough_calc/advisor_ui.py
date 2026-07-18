"""Advisor page (Qt only — every ranking comes from advisor.py).

Renders the plan / random-draws split: the plan lists steps you can work
toward deterministically; the draws list prices what a lucky curio pull
would be worth, since curios cannot simply be bought.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel, QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

from .advisor import rank
from .engine import fmt_days
from .i18n import tr, tr_duration


class AdvisorPage(QWidget):
    """Ranks the next Vault step against the current calculator inputs."""

    refreshed = Signal()

    def __init__(self, engine, catalog: dict, get_inputs, get_shelf,
                 parent=None):
        super().__init__(parent)
        self._engine = engine
        self._catalog = catalog
        self._get_inputs = get_inputs
        self._get_shelf = get_shelf

        v = QVBoxLayout(self)
        intro = QLabel(tr(
            "What to work on next, priced in days saved on your current "
            "projection. The plan lists steps you can simply go do; curios "
            "come from random draws, so those rank separately as what a "
            "lucky pull would be worth."))
        intro.setWordWrap(True)
        v.addWidget(intro)

        self._status = QLabel()
        self._status.setWordWrap(True)
        v.addWidget(self._status)

        self._tree = QTreeWidget()
        self._tree.setColumnCount(3)
        self._tree.setHeaderLabels([tr("Source"), tr("Next step"),
                                    tr("Time saved")])
        self._tree.setRootIsDecorated(True)
        v.addWidget(self._tree, 1)

        note = QLabel(tr(
            "Bonuses the calculator does not model — combat stats, "
            "Spiritium, Abode Aura already inside your readings — are not "
            "ranked."))
        note.setWordWrap(True)
        v.addWidget(note)

        btn = QPushButton(tr("Rank again"))
        btn.clicked.connect(self.refresh)
        v.addWidget(btn)

    def showEvent(self, ev):
        super().showEvent(ev)
        self.refresh()

    def refresh(self):
        adv = rank(self._engine, self._get_inputs(), self._catalog,
                   self._get_shelf())
        self._tree.clear()
        if not adv.valid:
            self._status.setText(
                tr("Fill in the Calculator first — the advisor prices "
                   "improvements against your current projection."))
            self.refreshed.emit()
            return
        if adv.metric == "target":
            head = tr("Ranking: days until your target Stage.")
        else:
            head = tr("Ranking: days to finish the current Stage.")
        self._status.setText(
            f"{head} ({tr_duration(fmt_days(adv.baseline_days))})")
        groups = ((tr("Plan — level or learn next"), adv.plan),
                  (tr("Random draws — worth pulling for"), adv.draws))
        for title, ranked in groups:
            top = QTreeWidgetItem([title, "", ""])
            self._tree.addTopLevelItem(top)
            if not ranked:
                top.addChild(QTreeWidgetItem(
                    [tr("Nothing here helps right now."), "", ""]))
            for r in ranked:
                top.addChild(QTreeWidgetItem([
                    r.candidate.name,
                    tr(r.candidate.action) if r.candidate.action == "Own"
                    else r.candidate.action,
                    tr_duration(fmt_days(r.days_saved)),
                ]))
            top.setExpanded(True)
        for col in range(3):
            self._tree.resizeColumnToContents(col)
        self.refreshed.emit()
