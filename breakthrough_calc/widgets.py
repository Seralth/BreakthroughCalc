"""Reusable Qt widgets and small UI helpers for the desktop GUI."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Signal
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMenu, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from . import DONATE_RID, DONATE_URL
from .i18n import tr


class WheelGuard(QObject):
    """Swallow wheel events on unfocused spin/combo widgets so scrolling the
    form doesn't silently change values (Qt steps them even without focus).

    The event is re-dispatched to the enclosing QScrollArea's viewport so the
    page still scrolls while the cursor is over one of the many spinboxes.
    The viewport itself has no filter installed, so this cannot recurse."""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel and not obj.hasFocus():
            event.ignore()
            self._forward_to_scroll_area(obj, event)
            return True
        return super().eventFilter(obj, event)

    @staticmethod
    def _forward_to_scroll_area(obj, event):
        parent = obj.parent()
        while parent is not None and not isinstance(parent, QScrollArea):
            parent = parent.parent()
        if parent is None:
            return
        viewport = parent.viewport()
        clone = QWheelEvent(
            viewport.mapFromGlobal(event.globalPosition()),
            event.globalPosition(),
            event.pixelDelta(),
            event.angleDelta(),
            event.buttons(),
            event.modifiers(),
            event.phase(),
            event.inverted(),
            event.source(),
        )
        QApplication.sendEvent(viewport, clone)


def link_enabled(box, *widgets):
    """Grey out widgets while the checkbox is unchecked, so it is obvious the
    inputs only count once the feature is enabled."""
    def apply(on):
        for w in widgets:
            w.setEnabled(on)
    box.toggled.connect(apply)
    apply(box.isChecked())


# ---- accent-colored labels ------------------------------------------------
# One registration point replaces the hand-maintained _muted_labels list plus
# the special-cased pin/o_error re-styling: style_accent() styles the label
# AND records (label, role, template) so restyle_all() re-applies every
# registered style on a theme change. clear_accents() must be called when the
# whole UI is rebuilt (language switch) so dead labels are dropped.
_ACCENTED: list = []


def style_accent(label, role: str, acc: dict, template: str = "color: {};"):
    label.setStyleSheet(template.format(acc[role]))
    _ACCENTED.append((label, role, template))


def restyle_all(acc: dict):
    for label, role, template in _ACCENTED:
        label.setStyleSheet(template.format(acc[role]))


def clear_accents():
    _ACCENTED.clear()


class PillEffectRows(QWidget):
    """The 'Cultivation pill effect' input: read-only rows the Vault manages
    plus free-typed rows whose percentages sum. Emits changed on any edit;
    the accents provider keeps styling on the current theme."""

    changed = Signal()

    def __init__(self, accents, parent=None):
        super().__init__(parent)
        self._accents = accents  # callable -> current accent dict
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        self.rows = []
        self._auto_rows = []      # (name, level_label, value) from the shelf
        self._auto_widgets = []
        self._auto_layout = QVBoxLayout()
        self._auto_layout.setContentsMargins(0, 0, 0, 0)
        v.addLayout(self._auto_layout)
        self._rows_layout = QVBoxLayout()
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        v.addLayout(self._rows_layout)
        self.total_label = QLabel(tr("Total: {} %").format("0.00"))
        style_accent(self.total_label, "muted", accents())
        add_pe = QPushButton(tr("＋ Add source"))
        add_pe.setToolTip(tr("Add a pill-effect source (a technique book, a curio, …). Their percentages sum."))
        add_pe.clicked.connect(lambda: (self.add_row(), self.changed.emit()))
        bottom = QHBoxLayout()
        bottom.addWidget(self.total_label, 1)
        bottom.addWidget(add_pe)
        v.addLayout(bottom)

    def add_row(self, label: str = "", value: float = 0.0):
        row = QWidget(); h = QHBoxLayout(row); h.setContentsMargins(0, 0, 0, 0)
        le = QLineEdit(label); le.setPlaceholderText(tr("source (e.g. technique book, curio)"))
        sp = QDoubleSpinBox(); sp.setRange(0, 500); sp.setDecimals(2); sp.setSuffix(" %"); sp.setValue(value)
        rm = QPushButton("✕"); rm.setFixedWidth(28)
        h.addWidget(le, 1); h.addWidget(sp); h.addWidget(rm)
        self._rows_layout.addWidget(row)
        entry = (le, sp, row)
        self.rows.append(entry)
        le.textChanged.connect(self.changed)
        sp.valueChanged.connect(self.changed)
        rm.clicked.connect(lambda: self.remove_row(entry))
        return entry

    def remove_row(self, entry):
        if entry in self.rows:
            self.rows.remove(entry)
        entry[2].setParent(None)
        if not self.rows:            # keep at least one row
            self.add_row()
        self.changed.emit()

    def total(self) -> float:
        return (sum(sp.value() for _, sp, _ in self.rows)
                + sum(v for _, _, v in self._auto_rows))

    def set_auto_rows(self, contribs):
        """Read-only rows managed by the Sources Shelf; they join the
        total but are edited on the Shelf, not here."""
        for w in self._auto_widgets:
            w.setParent(None)
        self._auto_widgets = []
        self._auto_rows = [(c.name, c.level_label, c.value) for c in contribs]
        for name, lvl, value in self._auto_rows:
            row = QWidget(); h = QHBoxLayout(row); h.setContentsMargins(0, 0, 0, 0)
            text = f"{name} ({lvl})" if lvl else name
            lab = QLabel(text); lab.setEnabled(False)
            val = QLabel(f"+{value:g} %"); val.setEnabled(False)
            tag = QLabel(tr("shelf")); tag.setEnabled(False)
            h.addWidget(lab, 1); h.addWidget(val); h.addWidget(tag)
            self._auto_layout.addWidget(row)
            self._auto_widgets.append(row)
        self.update_total()

    def sources(self) -> list:
        """[[label, value], ...] for persistence."""
        return [[le.text(), sp.value()] for le, sp, _ in self.rows]

    def set_sources(self, sources):
        for _, _, row in list(self.rows):
            row.setParent(None)
        self.rows.clear()
        for lbl, val in sources:
            self.add_row(str(lbl), float(val))
        if not self.rows:
            self.add_row()

    def update_total(self):
        self.total_label.setText(tr("Total: {} %").format(f"{self.total():.2f}"))

class DonateDialog(QDialog):
    """SEAGM in-game voucher gifting instructions (no URL prefill supported,
    so the RID is shown for manual entry)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Support the calculator"))
        v = QVBoxLayout(self)
        intro = QLabel(tr(
            "If the calculator saves you time, you can support development by "
            "gifting in-game vouchers:<ol>"
            "<li>Open <a href='{}'>SEAGM — OverMortal vouchers</a></li>"
            "<li>Pick any voucher amount</li>"
            "<li>Paste the RID below into the site's <b>RID</b> field</li></ol>").format(DONATE_URL))
        intro.setOpenExternalLinks(True)
        intro.setWordWrap(True)
        v.addWidget(intro)
        row = QHBoxLayout()
        rid = QLineEdit(DONATE_RID)
        rid.setReadOnly(True)
        row.addWidget(rid)
        copy = QPushButton(tr("Copy RID"))
        copy.clicked.connect(
            lambda: QApplication.clipboard().setText(DONATE_RID))
        row.addWidget(copy)
        v.addLayout(row)
        bb = QDialogButtonBox(QDialogButtonBox.Close)
        bb.rejected.connect(self.reject)
        bb.clicked.connect(self.accept)
        v.addWidget(bb)
