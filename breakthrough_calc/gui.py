"""Qt GUI for the Breakthrough Calculator."""

from __future__ import annotations

import json
import os
import sys

from PySide6.QtCore import QEvent, QObject, Qt, QUrl
from PySide6.QtGui import QGuiApplication, QWheelEvent
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from . import DONATE_RID, DONATE_URL, REPO, __version__
from PySide6.QtWidgets import (
    QAbstractSpinBox, QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QGridLayout, QHBoxLayout,
    QInputDialog, QLabel,
    QLineEdit, QMainWindow, QMenu, QPushButton, QScrollArea, QSpinBox, QTabWidget,
    QTextBrowser, QVBoxLayout,
    QWidget,
)


def _version_tuple(s: str):
    """'v2.7' -> (2, 7, 0); None if unparseable. Prerelease suffixes ignored."""
    s = s.strip().lstrip("vV").split("-")[0].split("+")[0]
    parts = s.split(".")
    try:
        nums = [int(p) for p in parts if p != ""]
    except ValueError:
        return None
    if not nums:
        return None
    return tuple((nums + [0, 0, 0])[:3])


class _WheelGuard(QObject):
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

from . import theme, i18n
from .i18n import tr, tr_duration
from .engine import Engine, Inputs, fmt_days, load_pill_sources, load_respira_sources

PHASE_LABELS = {"N/A": "N/A", "EARLY": "Early", "MIDDLE": "Middle", "LATE": "Late"}
PHASE_KEYS = {v: k for k, v in PHASE_LABELS.items()}

# Display-only canonical Stage names; internal data keys stay unchanged.
# Settings persist the INTERNAL keys; legacy files that stored display names
# (in any language) are migrated via i18n.reverse + the reverse maps below.
STAGE_LABELS = {"Nascent": "Nascent Soul"}
STAGE_KEYS = {v: k for k, v in STAGE_LABELS.items()}

# Vase input pill: internal key -> English display item.
VASE_INPUT_LABELS = {"Blue": "Blue/White", "Purple": "Purple (Epic)",
                     "Gold": "Gold (Legendary)"}
VASE_INPUT_KEYS = {v: k for k, v in VASE_INPUT_LABELS.items()}


def stage_disp(key: str) -> str:
    return tr(STAGE_LABELS.get(key, key))


def stage_key(disp: str) -> str:
    """Displayed (localized) stage name, legacy English display name, or an
    internal key -> internal key."""
    return STAGE_KEYS.get(i18n.reverse(disp), i18n.reverse(disp))


def phase_disp(key: str) -> str:
    return tr(PHASE_LABELS.get(key, key))


def phase_key(disp: str) -> str:
    return PHASE_KEYS.get(i18n.reverse(disp), i18n.reverse(disp))


def vase_input_disp(key: str) -> str:
    return tr(VASE_INPUT_LABELS.get(key, key))


def vase_input_key(disp: str) -> str:
    return VASE_INPUT_KEYS.get(i18n.reverse(disp), i18n.reverse(disp))


STARS = ["0*", "1*", "2*", "3*", "4*", "5*"]

# Energy Array: base energy is a known constant only for these Stages (wiki).
BASE_ENERGY = 130.0
BASE_ENERGY_STAGES = {"Connection", "Foundation", "Virtuoso", "Nascent", "Incarnation"}

# Strive (the catch-up absorption multiplier) unlocks at Nascent Soul.
STRIVE_STAGES = {"Nascent", "Incarnation", "Voidbreak", "Wholeness", "Perfection",
                 "Nirvana", "Celestial", "Eternal", "Supreme"}


def settings_path() -> str:
    """Prefer a JSON next to the executable (portable/self-contained); fall back
    to a per-OS user config location if that directory isn't writable.

    - Linux AppImage: next to the .AppImage (via the APPIMAGE env var).
    - Windows onefile .exe: next to the .exe, else %APPDATA%\\BreakthroughCalc.
    - Otherwise: next to a frozen executable, else ~/.config/breakthrough-calc.
    """
    # Portable location next to the executable.
    exe_dir = None
    appimage = os.environ.get("APPIMAGE")
    if appimage:
        exe_dir = os.path.dirname(appimage)
        name = os.path.basename(appimage) + ".settings.json"
    elif getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        name = "settings.json"
    if exe_dir and os.access(exe_dir, os.W_OK):
        return os.path.join(exe_dir, name)

    # Per-OS user config fallback.
    if sys.platform == "win32":
        base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                            "BreakthroughCalc")
    else:
        base = os.path.join(os.path.expanduser("~"), ".config", "breakthrough-calc")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "settings.json")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = Engine()
        self._settings_file = settings_path()
        self._loading = True
        store = self._read_store()
        self._theme = store.get("theme", "Seralth")
        if self._theme not in theme.THEMES:  # unknown persisted name -> default
            self._theme = "Seralth"
        i18n.set_lang(store.get("lang", "en"))
        self._acc = theme.accents(self._theme)
        self._build_ui()
        self._wire()
        self._on_stage_changed()
        self._defaults = self._collect_state()  # canonical construction defaults
        self._load_settings()
        self._loading = False
        self.recalc()
        self._nam = QNetworkAccessManager(self)
        self._check_updates()  # async; silent no-op offline

    # ---- UI construction -------------------------------------------------
    def _build_ui(self):
        self.setWindowTitle(tr("Breakthrough Calculator"))
        self._muted_labels = []
        central = QWidget()
        root = QVBoxLayout(central)
        root.addLayout(self._build_toolbar())
        outer = QHBoxLayout()
        root.addLayout(outer)

        # left column: inputs (scrollable)
        left = QWidget()
        lv = QVBoxLayout(left)

        cult = QGroupBox(tr("Cultivation Base"))
        f = QFormLayout(cult)
        self.stage = QComboBox(); self.stage.addItems([stage_disp(s) for s in self.engine.stages()])
        self.phase = QComboBox()
        self.grade = QComboBox()
        self.completion = QDoubleSpinBox(); self.completion.setRange(0, 100); self.completion.setSuffix(" %")
        self.speed = QDoubleSpinBox(); self.speed.setRange(0, 1e12); self.speed.setDecimals(2)
        self.absorb = QDoubleSpinBox(); self.absorb.setRange(0, 10000); self.absorb.setDecimals(3); self.absorb.setSuffix(" %")
        self.gem = QComboBox(); self.gem.addItems([tr(k) for k in self.engine.data["gem_bonus"]])
        self.target = QComboBox(); self.target.addItem(""); self.target.addItems([stage_disp(s) for s in self.engine.stages()])
        f.addRow(tr("Stage"), self.stage)
        f.addRow(tr("Half-step"), self.phase)
        f.addRow(tr("Grade"), self.grade)
        f.addRow(tr("Grade progress"), self.completion)
        # Abode Aura, Absorption Ratio, and Cultivation Speed all come off the
        # same in-game Cultivation Bonus screen. Enter Aura + Absorption and
        # the Apply button appears to fill in Speed (= Aura × Absorption);
        # Speed stays directly editable for anyone who prefers typing it.
        self.abode_aura = QDoubleSpinBox(); self.abode_aura.setRange(0, 1e9)
        self.abode_aura.setDecimals(2)
        self.abode_aura.setToolTip(tr(
            "Your Abode Aura as shown on the Cultivation Bonus screen. With Absorption "
            "Ratio entered, Cultivation Speed = Abode Aura × Absorption Ratio."))
        f.addRow(tr("Abode Aura"), self.abode_aura)
        f.addRow(tr("Absorption Ratio"), self.absorb)
        self.absorb_base = QLabel("")
        self.absorb_base.setStyleSheet(f"color: {self._acc['muted']};"); self._muted_labels.append(self.absorb_base)
        f.addRow("", self.absorb_base)
        self.array_out = QLabel("—"); self.array_out.setWordWrap(True)
        self.array_out.setStyleSheet(f"color: {self._acc['muted']};"); self._muted_labels.append(self.array_out)
        f.addRow("", self.array_out)
        self.array_apply = QPushButton(tr("Apply to Cultivation Speed"))
        self.array_apply.clicked.connect(self._apply_array_speed)
        f.addRow("", self.array_apply)
        f.addRow(tr("Cultivation Speed (XP / Cosmoapsis)"), self.speed)
        f.addRow(tr("Aura Gem"), self.gem)
        f.addRow(tr("Target Stage"), self.target)
        self.top_stage = QComboBox(); self.top_stage.addItem("")
        self.top_stage.addItems([stage_disp(s) for s in self.engine.stages()])
        self.top_stage.setToolTip(tr(
            "Optional: your server's #1 cultivator's Stage. Models your Strive stepping DOWN as you "
            "break through toward them (estimated; assumes #1 stays put; live value is server-computed hourly). "
            "Leave blank to hold Strive constant."))
        f.addRow(tr("Server #1's Stage (Strive)"), self.top_stage)
        self.mature_server = QCheckBox(tr("Mature server (world level 30+)"))
        self.mature_server.setChecked(True)
        self.mature_server.setToolTip(tr(
            "Server age changes how Strive is computed. Mature servers (world level 30+, "
            "the common case) use finer level-gap tiers plus a realm-gap bonus (cap ~120%); "
            "young servers use the plain realm-gap table (cap 70%). Only used when "
            "Server #1's Stage is set."))
        f.addRow("", self.mature_server)
        lv.addWidget(cult)

        pills = QGroupBox(tr("Cultivation Pills"))
        f = QFormLayout(pills)
        self.pill_rank = QComboBox(); self.pill_rank.addItems(list(self.engine.data["pill_xp"].keys()))
        self.pill_limit = QDoubleSpinBox(); self.pill_limit.setRange(0, 1e6)
        self.gold_day = QDoubleSpinBox(); self.gold_day.setRange(0, 1e6)
        self.purple_day = QDoubleSpinBox(); self.purple_day.setRange(0, 1e6)
        self.blue_day = QDoubleSpinBox(); self.blue_day.setRange(0, 1e6)
        f.addRow(tr("Pill rank"), self.pill_rank)

        # Cultivation pill effect = sum of contributions (technique books, curios,
        # etc.). Record each source once so swapping gear means editing one row.
        pe_wrap = QWidget(); pe_v = QVBoxLayout(pe_wrap); pe_v.setContentsMargins(0, 0, 0, 0)
        self.pe_rows = []
        self.pe_rows_layout = QVBoxLayout(); self.pe_rows_layout.setContentsMargins(0, 0, 0, 0)
        pe_v.addLayout(self.pe_rows_layout)
        self.pe_total = QLabel(tr("Total: {} %").format("0.00")); self.pe_total.setStyleSheet(f"color: {self._acc['muted']};"); self._muted_labels.append(self.pe_total)
        add_pe = QPushButton(tr("＋ Add source"))
        add_pe.setToolTip(tr("Add a pill-effect source (a technique book, a curio, …). Their percentages sum."))
        add_pe.clicked.connect(lambda: (self._add_pe_row(), self.recalc()))
        pe_bottom = QHBoxLayout(); pe_bottom.addWidget(self.pe_total, 1); pe_bottom.addWidget(add_pe)
        self.pe_catalog = load_pill_sources()
        if self.pe_catalog:
            cat_btn = QPushButton(tr("＋ From catalog"))
            cat_btn.setToolTip(tr("Known pill-effect sources from the game data. Check to add "
                                  "(prefilled, editable), uncheck to remove."))
            cat_menu = QMenu(cat_btn)
            cat_menu.setToolTipsVisible(True)
            for src in self.pe_catalog:
                pct = f'{src["percent"]:g}%' if src.get("percent") else tr("varies")
                act = cat_menu.addAction(f'{src["name"]}  ({pct})')
                act.setCheckable(True)
                act.setToolTip(src.get("note", ""))
                act.setData(src)
            cat_menu.aboutToShow.connect(self._sync_catalog_menu)
            cat_menu.triggered.connect(self._toggle_catalog_source)
            cat_btn.setMenu(cat_menu)
            self._cat_menu = cat_menu
            pe_bottom.addWidget(cat_btn)
        pe_v.addLayout(pe_bottom)
        f.addRow(tr("Cultivation pill effect"), pe_wrap)

        self.pill_limit.setToolTip(tr("Shared daily attempt limit for all cultivation pills (vase red pills are exempt)."))
        f.addRow(tr("Daily pill attempts (shared)"), self.pill_limit)
        f.addRow(tr("Legendary (Gold) used / day"), self.gold_day)
        f.addRow(tr("Epic (Purple) used / day"), self.purple_day)
        f.addRow(tr("Rare (Blue) used / day"), self.blue_day)
        self.pill_attempts = QLabel("")
        self.pill_attempts.setStyleSheet(f"color: {self._acc['muted']};"); self._muted_labels.append(self.pill_attempts)
        f.addRow("", self.pill_attempts)
        self.dailies_done = QCheckBox(tr("Already used today's pills/respira"))
        self.dailies_done.setToolTip(tr(
            "Check if you've already taken today's daily pills and Respira. The "
            "projection then defers that boost to the next daily reset (today runs "
            "at base speed). Mainly affects short estimates."))
        f.addRow("", self.dailies_done)
        self.reset_in = QDoubleSpinBox()
        self.reset_in.setRange(0, 24); self.reset_in.setValue(24); self.reset_in.setSingleStep(0.5)
        self.reset_in.setToolTip(tr(
            "Hours until the game's daily reset. Only used when the box above is "
            "checked: the projection runs the window until the reset without the "
            "daily pill/Respira XP (and defers event Respira to the reset), then "
            "resumes the normal daily routine."))
        self.reset_in.setEnabled(self.dailies_done.isChecked())
        self.dailies_done.toggled.connect(self.reset_in.setEnabled)
        f.addRow(tr("Reset in (h)"), self.reset_in)
        marks = QHBoxLayout()
        self.mark_blue = QDoubleSpinBox(); self.mark_purple = QDoubleSpinBox(); self.mark_gold = QDoubleSpinBox()
        for w, name in ((self.mark_blue, "Rare"), (self.mark_purple, "Epic"), (self.mark_gold, "Legendary")):
            w.setRange(0, 10); w.setSingleStep(0.01); w.setDecimals(2)
            w.setToolTip(tr(
                "Your in-game 'Cultivation Pill EXP Bonus' for this pill rarity (mainly from "
                "Constellation Altar Star Marks). Entered as a ratio: 0.10 = +10%."))
            marks.addWidget(QLabel(tr(name))); marks.addWidget(w)
        f.addRow(tr("Star Marks (+XP ratio)"), marks)
        lv.addWidget(pills)

        arts = QGroupBox(tr("Creation Artifacts"))
        g = QGridLayout(arts)
        g.addWidget(QLabel(f"<b>{tr('Artifact')}</b>"), 0, 0); g.addWidget(QLabel(f"<b>{tr('Star')}</b>"), 0, 2); g.addWidget(QLabel(f"<b>{tr('Skin')}</b>"), 0, 3)
        g.addWidget(QLabel(f"<b>{tr('Charge')}</b>"), 0, 4)
        self.vase = QCheckBox(tr("Starsea Vase")); self.vase_star = QComboBox(); self.vase_star.addItems(STARS); self.vase_skin = QCheckBox()
        self.vase_skin.setToolTip(tr("Transmog skin: refined pills give +8% Cultivation EXP"))
        self.mirror = QCheckBox(tr("Dual-Star Mirror")); self.mirror_star = QComboBox(); self.mirror_star.addItems(STARS); self.mirror_skin = QCheckBox()
        self.mirror_skin.setToolTip(tr("Transmog skin: Duplication consumes 10% less Energy"))
        self.pearl = QCheckBox(tr("Timereversal Pearl")); self.pearl_star = QComboBox(); self.pearl_star.addItems(STARS)
        self.pearl_skin = QCheckBox()
        self.pearl_skin.setToolTip(tr("Transmog skin: Timereversal Pearl Energy Cost -10%"))
        self.pearl_xp10 = QDoubleSpinBox(); self.pearl_xp10.setRange(0, 1e12)
        charge_tip = tr("Daily Energy Charge: 30 Fateum/Destium adds 100 Energy to this artifact, once per day. Check if you use it every day.")
        self.vase_charge = QCheckBox(); self.mirror_charge = QCheckBox(); self.pearl_charge = QCheckBox()
        for w in (self.vase_charge, self.mirror_charge, self.pearl_charge):
            w.setChecked(True)
            w.setToolTip(charge_tip)
        g.addWidget(self.vase, 1, 0); g.addWidget(self.vase_star, 1, 2); g.addWidget(self.vase_skin, 1, 3)
        g.addWidget(self.vase_charge, 1, 4)
        g.addWidget(self.mirror, 2, 0); g.addWidget(self.mirror_star, 2, 2); g.addWidget(self.mirror_skin, 2, 3)
        g.addWidget(self.mirror_charge, 2, 4)
        g.addWidget(self.pearl, 3, 0); g.addWidget(self.pearl_star, 3, 2); g.addWidget(self.pearl_skin, 3, 3)
        g.addWidget(self.pearl_charge, 3, 4)
        self.vase_input_label = QLabel(tr("Vase input pill"))
        self.vase_input = QComboBox()
        self.vase_input.addItems([vase_input_disp(k) for k in VASE_INPUT_LABELS])
        self.vase_input.setToolTip(tr(
            "Which pill quality you refine into red pills. Refines are discounted by input "
            "quality (Epic -5%, Legendary -20% Energy), so feeding gold pills yields extra "
            "red pills over time. Base cost also depends on pill rank (75-100 energy)."))
        g.addWidget(self.vase_input_label, 4, 0); g.addWidget(self.vase_input, 4, 2, 1, 2)
        self.pearl_xp10_label = QLabel(tr("EXP per 10 energy"))
        g.addWidget(self.pearl_xp10_label, 5, 0); g.addWidget(self.pearl_xp10, 5, 2, 1, 2)
        # Grey out each artifact's controls while it is unchecked, so it is
        # obvious the inputs only count once the artifact is enabled.
        def _link(box, *widgets):
            def apply(on):
                for w in widgets:
                    w.setEnabled(on)
            box.toggled.connect(apply)
            apply(box.isChecked())
        _link(self.vase, self.vase_star, self.vase_skin, self.vase_charge,
              self.vase_input, self.vase_input_label)
        _link(self.mirror, self.mirror_star, self.mirror_skin, self.mirror_charge)
        _link(self.pearl, self.pearl_star, self.pearl_skin, self.pearl_charge,
              self.pearl_xp10, self.pearl_xp10_label)
        lv.addWidget(arts)

        respira = QGroupBox(tr("Respira"))
        rf = QFormLayout(respira)
        self.respira_per_day = QDoubleSpinBox(); self.respira_per_day.setRange(0, 1e5)
        self.respira_per_day.setToolTip(tr(
            "Your daily Respira attempt limit as shown in-game (base + permanent "
            "bonus attempts). Leave out temporary event attempts."))
        self.respira_event = QDoubleSpinBox(); self.respira_event.setRange(0, 1e5)
        self.respira_event.setToolTip(tr(
            "One-off extra Respira attempts available today only (event/item). "
            "Credited once, not as a daily rate."))
        self.respira_exp = QDoubleSpinBox(); self.respira_exp.setRange(0, 1e12)
        self.respira_exp.setToolTip(tr(
            "The base (non-crit) Cultivation EXP from one Respira attempt — see the "
            "note below the field."))
        self._respira_checked = getattr(self, "_respira_checked", set())
        self.respira_catalog = load_respira_sources()
        if self.respira_catalog:
            rp_wrap = QWidget(); rp_h = QHBoxLayout(rp_wrap); rp_h.setContentsMargins(0, 0, 0, 0)
            rp_h.addWidget(self.respira_per_day, 1)
            rsp_btn = QPushButton(tr("Sources…"))
            rsp_btn.setToolTip(tr(
                "Known Respira bonus sources. Checkable entries add/remove daily "
                "attempts from the field. Greyed entries are informational only: "
                "Respira EXP bonuses are already inside your in-game EXP tooltip, "
                "and pill-attempt bonuses belong in the Daily pill attempts input."))
            rsp_menu = QMenu(rsp_btn)
            rsp_menu.setToolTipsVisible(True)
            for src in self.respira_catalog:
                if src.get("kind") == "attempt":
                    act = rsp_menu.addAction(f'{src["name"]}  (+{src["value"]:g}/day)')
                    act.setCheckable(True)
                    act.setData(src)
                else:
                    label = tr("info") if src.get("kind") == "exp_pct" else tr("pill limit")
                    act = rsp_menu.addAction(f'{src["name"]}  ({label})')
                    act.setEnabled(False)
                act.setToolTip(src.get("note", ""))
            rsp_menu.aboutToShow.connect(self._sync_respira_menu)
            rsp_menu.triggered.connect(self._toggle_respira_source)
            rsp_btn.setMenu(rsp_menu)
            self._respira_menu = rsp_menu
            rp_h.addWidget(rsp_btn)
            rf.addRow(tr("Attempts / day"), rp_wrap)
        else:
            rf.addRow(tr("Attempts / day"), self.respira_per_day)
        rf.addRow(tr("Extra attempts today"), self.respira_event)
        rf.addRow(tr("Base EXP / attempt"), self.respira_exp)
        respira_hint = QLabel(tr(
            "Do a few Respira: most give the same small EXP (the base — enter that); "
            "some give 2×/5×/10× (crits — ignore, handled automatically)."))
        respira_hint.setWordWrap(True)
        respira_hint.setStyleSheet(f"color: {self._acc['muted']};")
        self._muted_labels.append(respira_hint)
        rf.addRow("", respira_hint)
        lv.addWidget(respira)

        fruit = QGroupBox(tr("Myrimon Fruit"))
        f = QFormLayout(fruit)
        self.fruit_rank = QComboBox(); self.fruit_rank.addItems(list(self.engine.data["fruit_xp"].keys()))
        self.fruit_high = QCheckBox(tr("Highest rank (+50%)"))
        self.fruit_count = QDoubleSpinBox(); self.fruit_count.setRange(0, 1e6)
        self.lvl_culti = QSpinBox(); self.lvl_quality = QSpinBox(); self.lvl_gush = QSpinBox()
        for w in (self.lvl_culti, self.lvl_quality, self.lvl_gush):
            w.setRange(0, 30)
        self.extractor = QComboBox(); self.extractor.addItems([tr(r) for r in self.engine.data["rarity_names"]])
        f.addRow(tr("Fruit rank"), self.fruit_rank)
        f.addRow("", self.fruit_high)
        f.addRow(tr("No. of Myrimon Fruits"), self.fruit_count)
        f.addRow(tr("Culti level"), self.lvl_culti)
        f.addRow(tr("Quality level"), self.lvl_quality)
        f.addRow(tr("Gush level"), self.lvl_gush)
        f.addRow(tr("Aura Extractor quality"), self.extractor)
        lv.addWidget(fruit)

        note = QLabel(tr(
            "Note: Strive (the catch-up bonus, from Nascent Soul) fades as you close the gap to "
            "your server's #1. Set \"Server #1's Stage\" above to model that drop-off (estimated); "
            "leave it blank to hold Strive constant. Low/zero-strive players are unaffected either way."))
        note.setWordWrap(True); note.setStyleSheet(f"color: {self._acc['muted']}; font-size: 11px;"); self._muted_labels.append(note)
        lv.addWidget(note)
        lv.addStretch(1)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(left)
        scroll.setMinimumWidth(430)
        outer.addWidget(scroll, 1)

        # right column: live results + a pinnable "A" snapshot for A/B compare
        self.RESULT_ROWS = [
            ("Half-step breakthrough in", "o_phase"),
            ("Stage breakthrough in", "o_stage"),
            ("Target Stage reached in", "o_target"),
            ("Abode Aura (implied)", "o_abode"),
            ("Cultivation XP / day", "o_basexp"),
            ("Effective XP / day", "o_effxp"),
            ("Pill XP / day", "o_pillxp"),
            ("Daily XP share (pills+Respira / gem)", "o_speedup"),
            ("Mythic pills / day", "o_mythic"),
            ("Pearl XP / day", "o_pearl"),
            ("Respira XP / day", "o_respira"),
            ("XP from fruits", "o_fruit"),
            ("Fruit time saved", "o_fruit_days"),
        ]

        def mklabel() -> QLabel:
            lbl = QLabel("—"); lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            fnt = lbl.font(); fnt.setBold(True); lbl.setFont(fnt)
            return lbl

        right = QGroupBox(tr("Results (current)"))
        rf = QFormLayout(right)
        for text, attr in self.RESULT_ROWS:
            lbl = mklabel(); setattr(self, attr, lbl); rf.addRow(tr(text), lbl)
        self.o_error = QLabel(""); self.o_error.setStyleSheet(f"color: {self._acc['bad']};"); self.o_error.setWordWrap(True)
        rf.addRow(self.o_error)
        btns = QHBoxLayout()
        self.copy_btn = QPushButton(tr("Copy results")); self.copy_btn.clicked.connect(self._copy_results)
        self.pin_btn = QPushButton(tr("Pin as A")); self.pin_btn.clicked.connect(self._pin_results)
        btns.addWidget(self.copy_btn); btns.addWidget(self.pin_btn)
        rf.addRow(btns)
        outer.addWidget(right, 1)

        self.pin_box = QGroupBox(tr("Pinned A"))
        pf = QFormLayout(self.pin_box)
        self.pin_labels = {}
        for text, attr in self.RESULT_ROWS:
            lbl = mklabel(); lbl.setStyleSheet(f"font-weight: bold; color: {self._acc['good']};"); self.pin_labels[attr] = lbl
            pf.addRow(tr(text), lbl)
        self.unpin_btn = QPushButton(tr("Clear A")); self.unpin_btn.clicked.connect(self._unpin_results)
        pf.addRow(self.unpin_btn)
        self.pin_box.setVisible(False)
        outer.addWidget(self.pin_box, 1)

        tabs = QTabWidget()
        tabs.addTab(central, tr("Calculator"))
        self._tabs = tabs
        tabs.addTab(self._build_info_tab(), tr("Reference"))
        tabs.addTab(self._build_guide_tab(), tr("Guide"))
        self.setCentralWidget(tabs)

    def _rebuild_info_tab(self):
        # Rebuild the Reference and Guide tabs (all sub-tab browsers) so accent
        # colors baked into the HTML follow theme changes; keep the sub-tabs.
        sub = self._ref_tabs.currentIndex() if getattr(self, "_ref_tabs", None) else 0
        gsub = self._guide_tabs.currentIndex() if getattr(self, "_guide_tabs", None) else 0
        self._tabs.removeTab(2)
        self._tabs.removeTab(1)
        self._tabs.insertTab(1, self._build_info_tab(), tr("Reference"))
        self._tabs.insertTab(2, self._build_guide_tab(), tr("Guide"))
        self._ref_tabs.setCurrentIndex(sub)
        self._guide_tabs.setCurrentIndex(gsub)
        self.resize(1180, 680)

    def _build_info_tab(self) -> QWidget:
        """Read-only reference, split into topic sub-tabs. Tables render from
        the same data the engine uses so they can't drift from the calculations."""
        d = self.engine.data
        muted = self._acc["muted"]

        def table(title, headers, rows, note=""):
            h = f"<h3>{title}</h3><table cellpadding='4' cellspacing='0' border='1' style='border-collapse:collapse'>"
            h += "<tr>" + "".join(f"<th>{c}</th>" for c in headers) + "</tr>"
            for r in rows:
                h += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
            h += "</table>"
            if note:
                h += f"<p style='color:{muted}'>{note}</p>"
            return h

        def page(html: str) -> QTextBrowser:
            b = QTextBrowser()
            b.setOpenExternalLinks(True)
            b.setHtml(html)
            return b


        # ---- Basics --------------------------------------------------------
        basics = "<h2>Basics</h2>"
        basics += (
            "<h3>How cultivation works</h3>"
            "<p>Your character gains cultivation EXP automatically, one tick every "
            "<b>8 seconds</b> (a \"Cosmoapsis\"). The EXP per tick is your <b>Cultivation "
            "Speed</b>, and everything about progression speed hangs off this one number:</p>"
            "<p style='margin-left:16px'><b>Cultivation Speed = Abode Aura × Absorption Ratio</b></p>"
            "<p><b>Abode Aura</b> is your abode's output: a base energy (130 for Connection "
            "through Incarnation) multiplied by your total aura bonus — the sum of your "
            "Energy Array level, aura curios, sect level bonus, and similar. <b>Absorption "
            "Ratio</b> is how much of that aura you absorb: each Stage/Grade has a base "
            "band that rises as you progress, plus bonuses from gear and Strive. All three "
            "numbers are shown together on the in-game <b>Cultivation Bonus</b> screen, "
            "which is where the calculator's inputs come from.</p>"
            "<p>Progression is Stage → Half-step (Early/Middle/Late) → Grade. Each grade "
            "requires a fixed amount of EXP; the calculator sums the remaining EXP through "
            "your target and divides by your projected speed at each future grade.</p>"
            "<h3>Strive (the catch-up mechanic)</h3>"
            "<p>From Nascent Soul onward, <b>Strive</b> multiplies your absorption: "
            "Absorption = stage base × (1 + Strive). It's a catch-up bonus that GROWS the "
            "further you are behind your server's #1 cultivator and fades to zero as you "
            "close the gap — so long-term projections made at a high Strive are optimistic. "
            "Set \"Server #1's Stage\" in the calculator to model the drop-off. "
            "Counter-intuitively, Strive does not change your projected time at your "
            "current position — it cancels out of the math — it only matters for how speed "
            "evolves as you climb.</p>")
        basics += ("<h3>Core formulas</h3><ul>"
                   "<li>Cultivation Speed = Abode Aura × Absorption Ratio</li>"
                   "<li>Abode Aura = 130 × (1 + total aura bonus) — base 130 holds for "
                   "Connection through Incarnation</li>"
                   "<li>Cultivation ticks every 8 seconds (one Cosmoapsis)</li>"
                   "<li>Absorption = stage base × (1 + Strive); Strive unlocks at Nascent Soul "
                   "and fades as you approach your server's #1</li>"
                   "<li>Pill EXP = base × (1 + pill effect + quality star mark [+ Vase star/skin "
                   "for reds])</li></ul>"
                   "<h3>Crit variance (best / worst)</h3>"
                   "<p>Respira crits and fruit gushes are random, so the breakthrough estimate "
                   "carries a range. The app shows a <b>best / worst</b> band (a ~90% likely "
                   "interval, not literal extremes). Because these are sums of many independent "
                   "rolls, luck averages out: the band is widest on short estimates and tightens "
                   "as the horizon grows — the opposite of runaway long-term drift. Fruit gushes "
                   "also have a pity floor (every 6th fruit is a guaranteed gush), which further "
                   "narrows the fruit side of the band.</p>"
                   "<h3>Tips for using the calculator</h3>"
                   "<ul><li>Fill in Abode Aura and Absorption Ratio from the Cultivation Bonus "
                   "screen and press Apply — that guarantees a current speed. A red warning "
                   "means one of your readings is stale.</li>"
                   "<li>Re-read your numbers after any upgrade that touches aura (Energy Array, "
                   "curios, sect level) — bonuses creep constantly and quietly.</li>"
                   "<li>Percentages in this game stack additively almost everywhere (pill "
                   "effect sources, artifact star + skin bonuses, energy discounts). When in "
                   "doubt, add percentage points; don't multiply.</li>"
                   "<li>Save a profile per character/scenario from the toolbar; each profile "
                   "keeps its own inputs.</li>"
                   "<li>Projections assume instant first-try breakthroughs and today's daily "
                   "routine held constant — treat long-range estimates (with high Strive "
                   "especially) as optimistic bounds.</li></ul>"
                   "<p>Realm timegates pace whole-server progression; Myrimon fruits (see the "
                   "Myrimon &amp; Extractor tab) are the main F2P tool for meeting them.</p>")

        # ---- Pills & Respira -------------------------------------------------
        pills = "<h2>Pills &amp; Respira</h2>"
        pills += (
            "<h3>Daily pills</h3>"
            "<p>Cultivation pills are the main controllable EXP income. All colors share "
            "ONE daily attempt pool (the \"Daily pill attempts\" input) — using a blue "
            "costs the same attempt a gold would, so always consume your highest color "
            "first. Red (Mythic) pills refined by the Starsea Vase are exempt from the "
            "limit. A pill's tooltip shows its total EXP with your bonus in parentheses; "
            "the calculator works with base values (total − bonus).</p>")
        pills += table(
            "Cultivation Pill base EXP (per rank)",
            ["Rank", "Rare (Blue)", "Epic (Purple)", "Legendary (Gold)", "Mythic (Red)"],
            [[rk, f"{b:,}", f"{p:,}", f"{g:,}", f"{m:,}"]
             for rk, (g, p, b, m) in d["pill_xp"].items()],
            "Base values before bonuses; confirmed against in-game tooltips (tooltip shows "
            "total with the bonus in parentheses: base = total − bonus). All pill-effect "
            "bonuses add as percentage points and multiply the base once.")
        pills += table(
            "Cultivation Pill Effect sources",
            ["Source", "Bonus"],
            [[s["name"], f"{s['percent']:g}%" if s.get("percent") else "varies (see tooltip)"]
             for s in (self.pe_catalog or [])],
            "All sources stack additively. In-game these appear as technique completion "
            "bonuses (labeled by rank, e.g. R4 Golden Core +5%) and curio effects. Other "
            "technique ranks and Dao Ancestor treasures grant it too — read the % from "
            "the tooltip and add it as a custom source. Quality-specific bonuses (Star "
            "Marks, Daozu treasures, Lotus Throne) apply only to pills of that color — "
            "enter those in the Star Marks fields.")

        # ---- Artifacts & Gems ----------------------------------------------
        artifacts = "<h2>Artifacts &amp; Gems</h2>"
        artifacts += (
            "<h3>Creation Artifacts</h3>"
            "<p>Three artifacts convert a shared resource — <b>Artifact Energy</b> (each "
            "artifact has its own pool) — into extra cultivation EXP:</p>"
            "<ul><li><b>Starsea Vase</b>: refines any cultivation pill into a Mythic (red) "
            "pill worth far more EXP. Reds don't count against the daily attempt pool, so "
            "the Vase is effectively free extra pills every day — keep it fed.</li>"
            "<li><b>Dual-Star Mirror</b>: duplicates owned items, including your red pills "
            "(only reds whose EXP bonus matches your Vase's unlocked tiers). Its copies "
            "stack on top of Vase production.</li>"
            "<li><b>Timereversal Pearl</b>: converts energy into auxiliary-path EXP. Its "
            "per-use EXP scales with your own cultivation speed bonuses, so re-read its "
            "tooltip after aura upgrades.</li></ul>"
            "<p>Energy regenerates over time and stops at the cap, so idle energy above "
            "cap is wasted — spend before it fills. The paid daily charge (30 "
            "Fateum/Destium for +100) is usually the cheapest EXP a payer can buy; the "
            "calculator has a per-artifact checkbox for whether you use it.</p>")
        artifacts += table(
            "Creation Artifact energy",
            ["Property", "Value"],
            [["Regeneration", "1 energy / 15 min at 0★ (faster per star)"],
             ["Cap", "200 at 0★ (rises with stars); regen stops at cap"],
             ["Daily charge", "+100 energy for 30 Fateum/Destium, once per day per artifact"],
             ["Mirror copy cost", "200 base; −5% (1★), −10% (3★), −10% skin — discounts add together"],
             ["Mirror 5★", "15% chance of an extra copy per Duplication"],
             ["Pearl use cost", "10 energy; star/skin discounts add (skin −10%)"],
             ["Pearl EXP bonus", "+20% from 1★ (does not grow at higher stars)"]])
        artifacts += table(
            "Starsea Vase — refine energy cost (per pill rank)",
            ["Rank", "Standard Energy"],
            [[rk, d["vase_energy_cost"].get(rk, 100)] for rk in d["pill_xp"]],
            "Refining an Epic pill costs −5% energy, a Legendary −20%. Star effects: "
            "+10% EXP on refined pills (1★), +20% (3★), 15% chance to consume no energy (5★). "
            "Skin: +8% EXP. Refined reds don't count toward daily pill attempts.")
        artifacts += (
            "<h3>Aura Gems</h3>"
            "<p>An equipped Aura Gem stores aura while you're away and releases it, acting "
            "as a flat percentage speed-up on cultivation. The calculator (following "
            "Donk's sheet) models it as a constant parallel bonus by rarity:</p>")
        artifacts += table(
            "Aura Gem speed bonus",
            ["Rarity", "Bonus"],
            [[k, f"+{v * 100:.0f}%"] for k, v in d["gem_bonus"].items() if k != "None"])
        artifacts += (
            "<p><b>The Aura Gem is claimable storage</b>: it accrues gem% of your "
            "cultivation speed up to a cap (18-32 hours' worth depending on rarity). "
            "Claim before it caps or the excess is lost; the calculator assumes you "
            "always claim in time.</p>")

        pills += (
            "<h3>Respira</h3>"
            "<p>Respira (the daily cultivation exercise) grants a burst of Cultivation "
            "EXP from a limited number of daily attempts, resetting on Stage/half-step "
            "breakthrough. Each attempt rolls a crit multiplier — <b>×1 / ×2 / ×5 / ×10</b> "
            "at 60% / 30% / 8% / 2% — averaging <b>×1.8</b> (from the client config). Enter "
            "your daily attempt limit and the base (non-crit) EXP per attempt; the ×1.8 "
            "average is applied for you, so daily Respira EXP ≈ attempts × base × 1.8. "
            "Temporary event attempts go in the separate one-off field.</p>"
            "<p><b>How to read the base EXP per attempt:</b> perform several Respira and "
            "watch the Cultivation EXP each one grants. Most attempts give the same "
            "smaller number — that is the <b>base</b> (non-crit) value to enter. Now and "
            "then an attempt gives 2×, 5×, or 10× that (a crit) — ignore those; the app "
            "already accounts for crits via the ×1.8 average. So enter the smallest / "
            "most common EXP you see, not a big crit result.</p>")
        if self.respira_catalog:
            pills += table(
                "Respira bonus sources",
                ["Source", "Effect"],
                [[s["name"],
                  f'+{s["value"]:g} attempts/day' if s.get("kind") == "attempt"
                  else ("EXP % — already inside your in-game EXP tooltip"
                        if s.get("kind") == "exp_pct"
                        else "pill attempts — enter under Daily pill attempts")]
                 for s in self.respira_catalog],
                "Attempt sources can be checked from the Sources… menu next to the "
                "Attempts / day field; the greyed entries are informational only.")
        pills += (
            "<h3>Flat EXP — why pills matter less each grade</h3>"
            "<p><b>Pills and Respira grant flat EXP.</b> The percentage shown on the pill "
            "panel is relative to your current grade's EXP, so the same pills matter less "
            "as grades grow — pill-heavy accounts slow down more than naive projections "
            "suggest.</p>"
            "<p><b>Daily pills and Respira reset</b> on a major breakthrough/ascension — "
            "spend them before breaking through.</p>")

        # ---- Myrimon & Extractor ---------------------------------------------
        myrimon = "<h2>Myrimon &amp; Extractor</h2>"
        myrimon += (
            "<h3>Myrimon Fruits</h3>"
            "<p>Fruits processed through the Aura Extractor grant a one-time EXP payout "
            "(the calculator credits it against the earliest remaining EXP). Payout scales "
            "with fruit rank, your Culti/Quality/Gush levels, and extractor rarity — higher "
            "quality rolls multiply the base substantially, so extractor upgrades compound.</p>"
            "<p><b style='color:" + self._acc['bad'] + "'>Advisory</b> — tiering the extractor up requires "
            "consuming a number of fruits, so <b>spend only the minimum needed for each "
            "tier-up and stockpile everything else until the extractor is maxed</b>. Every "
            "fruit eaten early forfeits the better quality/EXP multipliers it would have "
            "received at higher extractor tiers — the same hoard is worth substantially "
            "more processed at max rarity. Note also that the extractor resets on a main-Stage "
            "breakthrough (see Verified mechanics below), so burn the stockpile before "
            "breaking through, and only after the extractor is upgraded.</p>"
            "<p>Fruits also lose 50% of their EXP once the realm's <b>timegate</b> passes — "
            "eat the stockpile before the timegate, not merely before your own breakthrough. "
            "Extractor leveling priority: Quality → "
            "Cultivation → Gush → High Rank, taking High Rank only after the others are "
            "maxed. Myrimon unlocks at Virtuoso; Virtuoso through Incarnation share one "
            "fruit/extractor tier, and each major realm afterwards gets its own. Myrimon "
            "uses stack (after the first week's event) — save them for Sunday or until you "
            "cross the next BR requirement.</p>"
            "<h3>Verified mechanics (v2.7)</h3><ul>"
            "<li><b>Fruit ranks map to realm bands</b> (R3 covers Nascent-Voidbreak; R6 "
            "starts the Spiritual world; R12 the Immortal world) — R4/R5 don't exist.</li>"
            "<li><b>Extractor tracks</b>: Quality raises the quality-roll odds, the "
            "Cultivation Bonus track gives +4% orb EXP per level, and the Gush track "
            "raises the gush multiplier.</li>"
            "<li><b>Extractor rarity</b>: each rarity rank unlocks +20% orb EXP for its "
            "tier (Uncommon through Mythic); when the extractor's rank matches your Stage "
            "(server's highest), base fruit EXP +50%.</li>"
            "<li><b>Gush</b>: base multiplier 150%, raised by the Gush track; every 6th "
            "identical fruit is a guaranteed gush, on top of the displayed random rate.</li>"
            "<li><b>Aura Extractor resets</b> to Common quality / bonus level 0 when you "
            "break through a main Stage, and leftover fruits of the previous Stage are "
            "auto-consumed at the pre-upgrade rates — finish upgrading the extractor "
            "<b>before</b> burning a stockpile, and burn the stockpile before a main-Stage "
            "breakthrough.</li></ul>")

        # ---- Combat & Gear ---------------------------------------------------
        # Sourced from decompiled client config tables (attrib, equipment,
        # equip_ten_lv_affix, affix_mark_rank, equip_suit, level_equip).
        # Combat itself is resolved server-side; these are the client-visible rules.
        combat = "<h2>Combat Stats &amp; Gear</h2>"
        combat += (
            "<p>This page is about fighting, not cultivating — nothing here changes "
            "your breakthrough time. It's a plain-language tour of what your stats "
            "mean and what all the gear upgrade buttons actually do.</p>"

            "<h3>Your stats, in short</h3>"
            "<p>Everything starts from five <b>base stats</b>. Each point you gain "
            "quietly converts into the combat numbers you see on your sheet:</p>")
        combat += table(
            "What each base stat gives you",
            ["Base stat", "Each point gives"],
            [("Physique", "+4 Physical ATK, +2 Physical DEF"),
             ("Psyche", "+4 Magical ATK, +2 Magical DEF"),
             ("STR", "+1000 Max HP, +3 Physical DEF"),
             ("CON", "+1000 Max MP, +3 Magical DEF"),
             ("Agility", "+3 Dodge, +3 Hit Rate (helps both damage types)")])
        combat += (
            "<p>Notice the pattern: every combat stat has a <b>physical</b> and a "
            "<b>magical</b> version. Your path fights with one or the other, so "
            "Physique-type stats matter to a body cultivator the way Psyche-type "
            "stats matter to a mage — the other half mostly just pads your defense.</p>"
            "<p>You'll also see PvP-only lines like \"DMG dealt to Taoists +x%\" — "
            "those don't come from base stats at all; they come from the gear "
            "systems below.</p>"

            "<h3>How crit works</h3>"
            "<p><b>Crit Chance</b> is shown as a flat number, not a percent. The "
            "game converts it to a real chance <i>relative to your realm</i> — the "
            "same flat crit that felt great at Foundation is worth a smaller "
            "percentage by Nascent Soul. To see your actual percentage, tap the "
            "crit stat in-game: its tooltip shows your current crit rate for your "
            "realm. (The exact conversion curve lives on the server, so no formula "
            "here — the tooltip is the source of truth.)</p>"
            "<p>The rest of the crit family, confirmed from game data:</p>"
            "<ul>"
            "<li><b>Crit DMG</b>: a crit deals <b>150%</b> damage baseline "
            "(rounded down); Crit DMG bonuses raise that multiplier.</li>"
            "<li><b>Crit Defense</b>: each +1% cuts an attacker's crit multiplier "
            "by 1% against you.</li>"
            "<li><b>Crit Resistance</b>: lowers the <i>chance</i> of being crit "
            "in the first place.</li>"
            "</ul>"

            "<h3>Gear in one paragraph</h3>"
            "<p>You wear a weapon, armor and an accessory, plus <b>Relics</b> as "
            "their own separate category. Rarity climbs white → green → blue → "
            "purple → yellow. When an item is forged its stats roll within a "
            "range — so two copies of the same item can differ, and a well-rolled "
            "piece is worth keeping.</p>"

            "<h3>Leveling gear (Augmentation)</h3>"
            "<p>Pouring materials into a piece does three things:</p>"
            "<ul>"
            "<li><b>Every level:</b> its base stats grow a little. Steady, nothing "
            "to time.</li>"
            "<li><b>Every 10th level:</b> it unlocks an extra bonus line. Which "
            "line is fixed per item — one weapon always grows a Crit DMG line, "
            "another an ATK line.</li>"
            "<li><b>Resonance:</b> a bonus across your whole equipped set that "
            "looks at the level of your <i>lowest</i> piece. Push everything past "
            "the next threshold together and you unlock PvP bonuses like \"Relic "
            "DMG to Taoists +x%\".</li>"
            "</ul>"
            "<p><b>Practical takeaway:</b> level your gear evenly. One maxed sword "
            "does less for you than eight pieces raised together, because "
            "Resonance only counts your weakest piece.</p>"

            "<h3>Carvings (the enchant lines)</h3>"
            "<p>From Foundation on, gear can hold <b>Carvings</b> — bonus stat "
            "lines you level separately by feeding them Carving EXP items. Slots "
            "unlock as the item's augment level rises, and a carving that keeps "
            "leveling steps up through its own rarity colors, getting stronger at "
            "each step. Carvings have their own Resonance too, again counted "
            "across everything you're wearing.</p>"

            "<h3>Gear sets</h3>"
            "<p>Each realm has a gear set: wear enough current-realm pieces and "
            "the set bonus turns on, granting those PvP damage/reduction lines "
            "and raising caps like how far carvings can go. The catch: <b>when "
            "you break through to a new realm, the old set bonus switches off</b> "
            "— you build it back up with the new realm's gear. Budget for that "
            "rather than being surprised by it.</p>"

            "<h3>Immortactic gear</h3>"
            "<p>A separate side-track of equipment with its own levels and stars. "
            "Its stats grow in 2-level steps, with a Crit DMG boost every 20th "
            "level.</p>"

            "<h3>About the missing numbers</h3>"
            "<p>The rules and thresholds above are confirmed from game data. The "
            "exact <i>values</i> — what a given 10-level bonus or resonance rank "
            "grants — are decided server-side and vary by item and realm, so this "
            "page doesn't guess at them. Where a number isn't listed, read it as "
            "\"unknown\", not \"zero\". For the exact per-point math the game does "
            "expose, see the Advanced tab.</p>")

        # ---- Combat & Gear: Advanced ---------------------------------------
        # Expert-level internals recovered from the client's own stat
        # definitions and tooltip text; only mechanics the game states
        # explicitly are listed with numbers.
        advanced = "<h2>Cultivation Internals (Advanced)</h2>"
        advanced += (
            "<p>The exact numbers behind the calculator's model, for readers who "
            "want to check the math.</p>"
            "<h3>Respira crit distribution</h3>")
        advanced += table(
            "Per-attempt crit roll (from client config)",
            ["Multiplier", "Chance"],
            [("×1", "60%"), ("×2", "30%"), ("×5", "8%"), ("×10", "2%")],
            "Mean multiplier 1.8 (the calculator's expected value), variance 2.56 "
            "per attempt — the main driver of the best/worst band on short "
            "horizons.")
        advanced += (
            "<h3>Fruit gush pity</h3>"
            "<p>Every 6th identical fruit is a guaranteed gush, on top of the "
            "displayed random rate. The variance model treats that 1-in-6 as "
            "deterministic — only the other 5/6 of fruits carry Bernoulli "
            "variance at the displayed gush chance — which narrows the fruit "
            "side of the band.</p>"
            "<h3>Strive tier tables</h3>"
            "<p>Recovered from client config; the live value is recomputed "
            "hourly on the server, so the calculator uses these only for the "
            "<i>shape</i> of the drop-off, anchored to your real Strive.</p>"
            "<ul>"
            "<li><b>Young servers</b> (world level &lt; 30): by major-realm gap "
            "to server #1 — 15% / 20% / 30% / 40% / 50% / 60% / 70% for gaps "
            "1–7.</li>"
            "<li><b>Mature servers</b> (world level ≥ 30): by minor-<i>level</i> "
            "gap — 70% at ≥60 levels, 30% at ≥50, 20% at ≥40 — plus an additive "
            "major-realm bonus of 30% (1 realm) or 50% (2+ realms). The 70% + "
            "50% sum is the ~120% cap seen on aged servers.</li>"
            "</ul>"
            "<h3>How the best/worst band is built</h3>"
            "<p>The band is a ~90% central interval (P5–P95): the calculator "
            "sums the variance of every random roll over the horizon (Respira "
            "crits, non-pity gushes) and takes ±1.645 standard deviations "
            "around the mean. Because variance grows with the square root of "
            "the number of rolls, the band is widest in relative terms on "
            "short projections and tightens as the horizon grows.</p>"

            "<h2>Combat Internals (Advanced)</h2>"
            "<p>Exact mechanics recovered from the game's own stat definitions "
            "and tooltip text. Everything numbered here is stated by the client; "
            "damage resolution itself runs on the server, so treat this as the "
            "rulebook rather than a full damage calculator.</p>"

            "<h3>Flat stats and realm normalization</h3>"
            "<p>Crit Chance, Crit Resistance, Hit Rate and Dodge are stored as "
            "flat values and converted to effective percentages against a "
            "<i>realm-dependent standard</i>. This is why the game's own tooltip "
            "reports your \"crit rate at your current realm\": the flat number "
            "keeps its value, but each realm raises the standard it's measured "
            "against, deflating the percentage. The normalization curve is "
            "server-side; the in-game tooltip is the only exact readout.</p>"

            "<h3>Per-point mechanics (client-stated)</h3>")
        advanced += table(
            "Per-point coefficients and caps",
            ["Stat", "Effect per point", "Cap"],
            [("Penetration (phys/spell)", "−0.1% target defense when your "
              "penetration exceeds the target's defense stat", "—"),
             ("Block (phys/spell)", "30% proc chance; each point −0.1% damage "
              "when your block exceeds the attacker's attack", "—"),
             ("Stun duration enhance", "+0.5% stun duration", "+25%"),
             ("Stun duration resist", "−0.5% stun duration taken", "−50%"),
             ("Stun chance enhance", "+0.2% stun proc chance", "+100%"),
             ("Stun chance resist", "−0.2% stun proc chance", "−50%"),
             ("Elemental Rule level", "+0.05% damage per level of advantage "
              "over the target", "—")])
        advanced += (
            "<h3>Crit internals</h3>"
            "<ul>"
            "<li>Base crit multiplier is <b>150%</b>, and crit damage is rounded "
            "<i>down</i>. Crit DMG% bonuses raise this multiplier.</li>"
            "<li>Soul-bound Talismans crit at a separate <b>120%</b> base.</li>"
            "<li><b>Crit Additive DMG</b> is a flat amount added on top of a "
            "crit (base 0) — it scales independently of the multiplier.</li>"
            "<li><b>Crit Block</b> trades 1:1 — each 1% removes 1% from the "
            "attacker's crit multiplier against you.</li>"
            "<li><b>Crit Resistance</b> reduces the <i>chance</i> of being crit; "
            "like Crit Chance it's flat and realm-normalized.</li>"
            "</ul>"

            "<h3>Sustain</h3>"
            "<p>Out of combat you regenerate <b>2% of max HP and MP per "
            "second</b>; regen stats raise this. Shields come in three kinds — "
            "standard (absorbs a fixed capacity), MP-fed (drains Max MP instead "
            "of a capacity pool) and HP-fed blood shields — plus statuses that "
            "boost shield strength or add damage while a shield holds.</p>"

            "<h3>The gear stat formula</h3>"
            "<p>An item's visible stat line is computed as:</p>"
            "<p style='margin-left:16px'><code>floor( base[rank][affix] × "
            "roll × rarity_scale )</code></p>"
            "<ul>"
            "<li><code>base[rank][affix]</code> — a lookup keyed by the item's "
            "level requirement and which affix the line is; this table is "
            "server-side.</li>"
            "<li><code>roll</code> — the forge-time quality roll, interpolated "
            "linearly between the affix's min and max range (a 0–100 score).</li>"
            "<li><code>rarity_scale</code> — a flat multiplier per rarity color; "
            "higher rarity scales every line on the item.</li>"
            "</ul>"
            "<p>Carving lines use the same base lookup times a per-carving-level "
            "multiplier, which is why a carving's value jumps when its rarity "
            "tier steps up. Augment levels multiply the item's base stats by a "
            "smooth per-level curve on top of all of this.</p>"

            "<h3>Damage families</h3>"
            "<p>Offense and defense are tracked separately per <i>source</i>: "
            "Abilities, Relics and Immortactic arts each have their own attack, "
            "defense and crit lines, and PvP (\"vs Taoists\") and PvE (\"vs "
            "monsters\") are independent trees on top of that. Two consequences "
            "worth knowing: a \"Relic DMG +x%\" line does nothing for your "
            "Ability damage, and PvE reduction does nothing in duels. There are "
            "also path-split modifiers — damage vs Immortal-path and vs "
            "Demon-path cultivators are separate stats.</p>"

            "<h3>How Battle Rating is put together</h3>"
            "<p>The total is computed server-side, but the client defines the "
            "structure: every stat carries a BR weight, and your BR is the "
            "weighted sum of everything you have, plus pre-scored blocks for "
            "gear. The in-game BR breakdown panel groups it into: character "
            "level &amp; realm, inner skill, gear (base + affixes + augment "
            "levels + carvings), Relics (same sub-parts), Abilities and their "
            "training, Curios (base + active + set), pets (level, skills, "
            "growth), plus talismans, celebrity cards and the rest.</p>"
            "<p>Two useful things fall out of the client weights:</p>"
            "<ul>"
            "<li><b>Defense is weighted ~2.1× attack per point</b> (and HP/MP "
            "pool points are weighted far below either) — the game \"prices\" a "
            "point of defense as worth about twice a point of attack.</li>"
            "<li><b>Each gear piece and Relic arrives with its BR pre-computed</b> "
            "(a base score, and for Relics a realm-corrected score that only "
            "applies once your realm meets the item's requirement — an "
            "under-realm Relic shows its uncorrected, lower BR).</li>"
            "</ul>"
            "<p>The exact weight constants exist in client data but the "
            "server's final assembly (level factors, rounding) isn't visible, "
            "so per-stat BR predictions from these weights are approximate.</p>")

        self._ref_tabs = ref = QTabWidget()
        for title, html in (("Basics", basics),
                            ("Pills & Respira", pills),
                            ("Myrimon & Extractor", myrimon),
                            ("Artifacts & Gems", artifacts),
                            ("Combat & Gear", combat),
                            ("Advanced", advanced)):
            ref.addTab(page(html), title)
        return ref

    def _build_guide_tab(self) -> QWidget:
        """Stage-by-stage cultivation guide, one sub-tab per realm band."""
        def page(html: str) -> QTextBrowser:
            b = QTextBrowser()
            b.setOpenExternalLinks(True)
            b.setHtml(html)
            return b

        novice = (
            "<h2>Novice – Foundation (your first day)</h2>"
            "<p>These first realms go by in hours. The goal is simple: keep the "
            "cultivation bar filling and break through the moment you can — the "
            "<b>Breakthrough</b> button appears on the main cultivation screen "
            "when the bar is full.</p><ul>"
            "<li><b>Break through to Connection immediately.</b> Nothing in Novice "
            "is worth lingering for.</li>"
            "<li><b>Pills</b> are the bottles on the bottom row of the cultivation "
            "screen — each grants instant cultivation EXP and you have a daily "
            "attempt limit. Early on, use only <b>blue</b> pills and don't max out "
            "your daily attempts until you've claimed the pill bag from the early "
            "quests. Save 5-10 attempts for Foundation 10, and spend pills mainly "
            "when they push you over a stage breakthrough. (What each pill is "
            "worth: Reference → Pills &amp; Respira.)</li>"
            "<li><b>Alchemy:</b> save your blue and purple pill materials for "
            "F9-F10 rather than crafting them the moment you get them.</li>"
            "<li><b>Respira</b> is the daily breathing exercise on the cultivation "
            "screen (the \"Today's Attempts\" counter). Before breaking through to "
            "Foundation, open <b>Techniques</b> and max <b>Longevity</b> — it "
            "permanently adds +1 daily Respira attempt and is cheapest now.</li>"
            "<li>In Foundation, unlock the <b>Energy Unification</b> technique "
            "before spending your Respira attempts, and hold your pill attempts "
            "until Foundation Late with the <b>Rejuvenation</b> technique at T3 "
            "(techniques boost how much each attempt is worth).</li>"
            "<li><b>Energy Array</b> materials come from the world-map realms: "
            "56 violetite from <b>Violet Streams</b>, then 110 frostite from "
            "<b>Lake Blackwater</b>. The array permanently raises your Abode "
            "Aura, which is the base of your cultivation speed (Reference → "
            "Basics explains the speed formula).</li></ul>")

        virtuoso = (
            "<h2>Virtuoso (usually end of day 1)</h2>"
            "<ul><li><b>Myrimon unlocks here</b> — it appears as the <b>Aura "
            "Extractor</b> lotus next to your character on the cultivation "
            "screen, fed by fruits from the weekly Myrimon dungeon runs. This "
            "becomes your single biggest free source of cultivation EXP, so read "
            "Reference → Myrimon &amp; Extractor before spending anything.</li>"
            "<li>During the first week of the Myrimon event your daily runs "
            "<b>don't accumulate</b> — use them every day, at the highest realm "
            "you can clear. After that first week they stack, so you can bank "
            "them for Sunday or until you can clear a higher-requirement "
            "dungeon.</li>"
            "<li>Work through <b>Realm Abyss</b> and <b>Cultivation Ruins</b> "
            "(in the realm/world-map menus) for all three Virtuoso realms — "
            "they hand out one-time cultivation rewards.</li>"
            "<li>Check the events panel for realm exploration events; the curio "
            "rewards are worth the detour.</li>"
            "<li>Free equipment upgrade materials: open the <b>Library of No "
            "Bound → Encyclopedia Tales</b> and go through the lore chronicles. "
            "Each chronicle has a comment section with notes from game NPCs — "
            "the <b>first like you give in each chronicle's comments</b> awards "
            "equipment upgrade material. Worth sweeping once while pushing "
            "through Virtuoso.</li></ul>")

        nascent = (
            "<h2>Nascent Soul (~day 3 for F2P)</h2>"
            "<ul><li>Pacing: expect ~3 days to reach Nascent Late and ~3 more to "
            "Incarnation. Spenders arrive faster; don't panic if you're a day "
            "behind these numbers.</li>"
            "<li><b>Strive unlocks here.</b> It's a catch-up bonus that raises "
            "your absorption while you're behind your server's #1 cultivator — "
            "you'll see your absorption ratio exceed the stage's base. In this "
            "calculator it appears as the implied Strive readout under the "
            "Absorption Ratio input, and the \"Server #1's Stage\" input starts "
            "to matter for long-range estimates. (Reference → Basics covers how "
            "Strive enters the math.)</li>"
            "<li>Keep the <b>story</b>, <b>Demon Spire</b>, and <b>realms</b> "
            "pushed as far as they'll go at every cultivation stage — several "
            "systems gate on them.</li></ul>")

        incarnation = (
            "<h2>Incarnation</h2>"
            "<ul><li>This is the extractor endgame for the mortal world. Open "
            "the <b>Aura Extractor → Boost</b> screen and max its tracks — "
            "<b>Quality first</b>, then Cultivation, then Gush (High Rank last, "
            "only after the rest). Keep <b>stockpiling fruits</b> instead of "
            "eating them: every extractor level makes each fruit worth more, and "
            "at Mortal World rank the extractor adds <b>+50% base fruit EXP</b> "
            "while you're at the server's highest Stage.</li>"
            "<li><b>Eat the stockpile before the realm timegate</b> — fruits "
            "lose 50% of their EXP once the next realm's timegate passes — or on "
            "the last day before your own breakthrough, whichever comes first. "
            "(Timegates and the full fruit math: Reference → Myrimon &amp; "
            "Extractor.)</li>"
            "<li>Before breaking through to Voidbreak: <b>spend all pills and "
            "Respira attempts</b> (they reset on the breakthrough), <b>don't</b> "
            "claim daily pill bags until after ascension, and spend your "
            "<b>Fatevillon</b> shop tokens beforehand — that shop resets on "
            "breakthroughs too.</li></ul>")

        voidbreak = (
            "<h2>Voidbreak and beyond</h2>"
            "<ul><li>Dailies and pill bags <b>reset on ascension</b> — same rule "
            "as the Incarnation checklist: spend before you break through.</li>"
            "<li>Each major realm from here has its <b>own Myrimon tier</b> — a "
            "new fruit rank (R6+) and a fresh extractor that starts back at "
            "Common quality and bonus level 0. The stockpile-then-eat rhythm "
            "repeats every realm.</li>"
            "<li><b>Strive above 120% is normal here.</b> The 120% cap belongs "
            "to the mortal world; later realms allow overcapping (for example by "
            "keeping your aux path a minor realm behind your main). The "
            "calculator only warns about >120% readings in mortal-world "
            "stages.</li></ul>")

        pets = (
            "<h2>Pets</h2>"
            "<p>Pets are combat companions — they raise your battle rating and "
            "fight beside you in PvE and PvP. They do <b>not</b> affect "
            "cultivation speed or breakthrough timing, which is why this "
            "calculator has no pet inputs.</p><ul>"
            "<li><b>Upgrade one pet only.</b> Upgrades get very expensive, and "
            "a second half-built pet is worth far less than one strong one.</li>"
            "<li>Which one: <b>Blazelion</b> for physical-damage paths "
            "(Corporia, Swordia); <b>Babeox</b> for magical paths (Magicka, "
            "Ghostia, Literatia).</li>"
            "<li>Pet skills come from <b>Demonroot</b> — buy it in the market "
            "when you see it.</li>"
            "<li>Pets are a low spending priority: heavy pet investment is "
            "whale territory, and free players get most of the value from just "
            "leveling their one pet steadily.</li>"
            "<li>The pet system hands out speed-up items — <b>save them for "
            "law fruits</b> in your garden rather than spending them on the "
            "pet itself (they're part of the standard pre-Voidbreak prep).</li>"
            "</ul>")

        aux = (
            "<h2>Aux Paths (dual pathing)</h2>"
            "<p>Your auxiliary path is a second cultivation class alongside "
            "your main. A good aux adds real fighting power (stats, mana, "
            "shields, crowd control); a bad one adds only small stats. Common "
            "picks:</p><ul>"
            "<li><b>Corporia</b> main → Magicka aux (extra MP and shields for "
            "survivability). Most things work; Literatia is not recommended.</li>"
            "<li><b>Magicka</b> main → Ghostia aux (MP for shields, extra "
            "crowd control, and a ghost that helps monster farming).</li>"
            "<li><b>Swordia</b> main → Magicka aux for sustained damage "
            "(MP + shields); Corporia aux for burst builds.</li>"
            "<li><b>Ghostia</b> main → Corporia aux (survivability and a "
            "strong ultimate that doesn't eat the mana your ghost needs); "
            "Magicka as the alternative.</li>"
            "<li><b>Literatia</b> main → Magicka for F2P/low spenders; "
            "Corporia or Ghostia for committed dual-pathers.</li></ul>"
            "<p><b>Aux paths and cultivation:</b> from Voidbreak through "
            "Wholeness, the aux path enables the Strive overcap play: reach "
            "half-step in Voidbreak, then at Wholeness hold your main path at "
            "Middle G1 and pump the aux at Early G20 until absorption overcaps "
            "(~404% at Wholeness completion), then level the main normally "
            "keeping the aux a minor realm behind. It works because an Early "
            "path always counts below a Middle path for Strive, so the bonus "
            "keeps applying. This is why the calculator's 120% Strive warning "
            "only applies to mortal-world stages.</p>"
            "<p>The calculator models one path at a time — enter the numbers "
            "for whichever path you're actively cultivating.</p>")

        self._guide_tabs = guide = QTabWidget()
        for title, html in (("Novice–Foundation", novice),
                            ("Virtuoso", virtuoso),
                            ("Nascent Soul", nascent),
                            ("Incarnation", incarnation),
                            ("Voidbreak+", voidbreak),
                            ("Pets", pets),
                            ("Aux Paths", aux)):
            guide.addTab(page(html), title)
        return guide

    # ---- signal wiring ---------------------------------------------------
    def _wire(self):
        self.stage.currentTextChanged.connect(self._on_stage_changed)
        self.phase.currentTextChanged.connect(self._on_phase_changed)
        for w in (self.grade, self.gem, self.target, self.top_stage, self.pill_rank, self.vase_star,
                  self.vase_input, self.mirror_star, self.pearl_star, self.fruit_rank, self.extractor):
            w.currentTextChanged.connect(self.recalc)
        for w in (self.completion, self.speed, self.absorb, self.pill_limit,
                  self.gold_day, self.purple_day, self.blue_day, self.mark_blue,
                  self.mark_purple, self.mark_gold, self.pearl_xp10,
                  self.respira_per_day, self.respira_event, self.respira_exp, self.fruit_count, self.reset_in):
            w.valueChanged.connect(self.recalc)
        for w in (self.lvl_culti, self.lvl_quality, self.lvl_gush, self.abode_aura):
            w.valueChanged.connect(self.recalc)
        for w in (self.vase, self.vase_skin, self.vase_charge, self.mirror, self.mirror_skin,
                  self.mirror_charge, self.pearl, self.pearl_skin, self.pearl_charge,
                  self.mature_server, self.dailies_done, self.fruit_high):
            w.toggled.connect(self.recalc)
        self._install_wheel_guard()
        self._install_tooltips()
        hints = QGuiApplication.styleHints()
        if hasattr(hints, "colorSchemeChanged"):  # Qt >= 6.5
            hints.colorSchemeChanged.connect(self._on_color_scheme_changed)

    def _install_wheel_guard(self):
        self._wheel_guard = _WheelGuard(self)
        for cls in (QAbstractSpinBox, QComboBox):
            for w in self.findChildren(cls):
                w.setFocusPolicy(Qt.StrongFocus)
                w.installEventFilter(self._wheel_guard)

    def _install_tooltips(self):
        tips = {
            self.speed: "The in-game Cultivation Speed: XP gained per 8-second Cosmoapsis tick.",
            self.absorb: "Your Absorption Ratio as a percent (e.g. 27.5). Shown below is the Stage's base for the selected Grade.",
            self.completion: "How far into the current Grade you are, as a percent.",
            self.gem: "Aura Gem rarity. In-game it's claimable storage that accrues gem% of your cultivation speed "
                      "(up to 18-32h per claim); modeled as a continuous speed multiplier on cultivation only — "
                      "pills/Respira are flat XP and are NOT boosted by the gem.",
            self.target: "Optional: a future Stage to time your arrival at.",
            self.pill_limit: "Daily pill-use limit that caps Gold/Purple/Blue usage.",
            self.pearl_xp10: "Timereversal Pearl: EXP granted per 10 energy.",
            self.fruit_count: "Number of Myrimon Fruits processed through the Aura Extractor.",
        }
        for w, t in tips.items():
            w.setToolTip(tr(t))

    def _on_stage_changed(self):
        stage = stage_key(self.stage.currentText())
        self.phase.blockSignals(True)
        self.phase.clear()
        self.phase.addItems([phase_disp(p) for p in self.engine.phases_for(stage)])
        self.phase.blockSignals(False)
        # Target dropdown: only Stages strictly after the current one.
        stages = self.engine.stages()
        future = stages[stages.index(stage) + 1:] if stage in stages else []
        prev = self.target.currentText()
        self.target.blockSignals(True)
        self.target.clear()
        self.target.addItem("")
        self.target.addItems([stage_disp(s) for s in future])
        i = self.target.findText(prev)
        self.target.setCurrentIndex(i if i >= 0 else 0)
        self.target.blockSignals(False)
        self._on_phase_changed()

    def _on_phase_changed(self):
        stage, phase = stage_key(self.stage.currentText()), phase_key(self.phase.currentText())
        self.grade.blockSignals(True)
        self.grade.clear()
        self.grade.addItems(self.engine.grades_for(stage, phase))
        self.grade.blockSignals(False)
        self.recalc()

    # ---- calc ------------------------------------------------------------
    def _inputs(self) -> Inputs:
        return Inputs(
            stage=stage_key(self.stage.currentText()), phase=phase_key(self.phase.currentText()),
            grade=self.grade.currentText(), grade_completion=self.completion.value() / 100.0,
            culti_speed=self.speed.value(), absorption_ratio=self.absorb.value() / 100.0,
            aura_gem=i18n.reverse(self.gem.currentText()), target_stage=stage_key(self.target.currentText()),
            top_stage=stage_key(self.top_stage.currentText()),
            pill_rank=self.pill_rank.currentText(), pill_effect=self._pill_effect_total() / 100.0,
            pill_limit=self.pill_limit.value(), gold_per_day=self.gold_day.value(),
            purple_per_day=self.purple_day.value(), blue_per_day=self.blue_day.value(),
            mark_blue=self.mark_blue.value(), mark_purple=self.mark_purple.value(),
            mark_gold=self.mark_gold.value(),
            vase=self.vase.isChecked(), vase_star=self.vase_star.currentText(),
            vase_skin=self.vase_skin.isChecked(),
            vase_input=vase_input_key(self.vase_input.currentText()),
            mirror=self.mirror.isChecked(), mirror_star=self.mirror_star.currentText(),
            mirror_skin=self.mirror_skin.isChecked(),
            pearl=self.pearl.isChecked(), pearl_star=self.pearl_star.currentText(),
            pearl_skin=self.pearl_skin.isChecked(),
            pearl_xp_per_10=self.pearl_xp10.value(),
            mature_server=self.mature_server.isChecked(),
            dailies_done=self.dailies_done.isChecked(),
            reset_in_hours=self.reset_in.value(),
            respira_per_day=self.respira_per_day.value(),
            respira_event=self.respira_event.value(),
            respira_exp=self.respira_exp.value(),
            vase_charge=self.vase_charge.isChecked(),
            mirror_charge=self.mirror_charge.isChecked(),
            pearl_charge=self.pearl_charge.isChecked(),
            fruit_rank=self.fruit_rank.currentText(), fruit_count=self.fruit_count.value(),
            fruit_highest_rank=self.fruit_high.isChecked(),
            lvl_culti=self.lvl_culti.value(), lvl_quality=self.lvl_quality.value(),
            lvl_gush=self.lvl_gush.value(), extractor_rarity=i18n.reverse(self.extractor.currentText()),
        )

    # ---- persistence -----------------------------------------------------
    def _widget_map(self) -> dict:
        return {
            "stage": self.stage, "phase": self.phase, "grade": self.grade,
            "completion": self.completion, "speed": self.speed, "absorb": self.absorb,
            "gem": self.gem, "target": self.target, "top_stage": self.top_stage,
            "pill_rank": self.pill_rank,
            "pill_limit": self.pill_limit, "gold_day": self.gold_day,
            "purple_day": self.purple_day, "blue_day": self.blue_day,
            "mark_blue": self.mark_blue, "mark_purple": self.mark_purple,
            "mark_gold": self.mark_gold,
            "vase": self.vase, "vase_star": self.vase_star, "vase_skin": self.vase_skin,
            "vase_input": self.vase_input,
            "mirror": self.mirror, "mirror_star": self.mirror_star,
            "mirror_skin": self.mirror_skin,
            "pearl": self.pearl, "pearl_star": self.pearl_star,
            "pearl_skin": self.pearl_skin, "mature_server": self.mature_server,
            "dailies_done": self.dailies_done,
            "reset_in_hours": self.reset_in,
            "respira_per_day": self.respira_per_day, "respira_event": self.respira_event,
            "respira_exp": self.respira_exp,
            "pearl_xp10": self.pearl_xp10,
            "vase_charge": self.vase_charge, "mirror_charge": self.mirror_charge,
            "pearl_charge": self.pearl_charge,
            "fruit_rank": self.fruit_rank, "fruit_high": self.fruit_high,
            "fruit_count": self.fruit_count, "lvl_culti": self.lvl_culti,
            "lvl_quality": self.lvl_quality, "lvl_gush": self.lvl_gush,
            "extractor": self.extractor, "abode_aura": self.abode_aura,
        }

    # Combo values are persisted as INTERNAL keys (language-independent);
    # these two maps convert display text <-> internal key per widget key.
    _COMBO_TO_KEY = {
        "stage": stage_key, "target": stage_key, "top_stage": stage_key,
        "phase": phase_key, "gem": i18n.reverse, "extractor": i18n.reverse,
        "vase_input": vase_input_key,
    }
    _KEY_TO_COMBO = {
        "stage": stage_disp, "target": stage_disp, "top_stage": stage_disp,
        "phase": phase_disp, "gem": tr, "extractor": tr,
        "vase_input": vase_input_disp,
    }

    def _collect_state(self) -> dict:
        vals = {}
        for key, w in self._widget_map().items():
            if isinstance(w, QComboBox):
                conv = self._COMBO_TO_KEY.get(key)
                vals[key] = conv(w.currentText()) if conv else w.currentText()
            elif isinstance(w, QCheckBox):
                vals[key] = w.isChecked()
            else:
                vals[key] = w.value()
        vals["pill_sources"] = [[le.text(), sp.value()] for le, sp, _ in self.pe_rows]
        vals["respira_sources"] = sorted(self._respira_checked)
        return vals

    def _apply_state(self, vals: dict):
        prev, self._loading = self._loading, True
        # pill-effect sources (migrate old single "pill_effect_pct" to one row)
        srcs = vals.get("pill_sources")
        if srcs is None and "pill_effect_pct" in vals:
            srcs = [["", vals["pill_effect_pct"]]]
        self._set_pill_sources(srcs if srcs is not None else [])
        # checked respira catalog sources; the attempts value itself is stored
        # in respira_per_day, so only the checkmarks need restoring
        rs = vals.get("respira_sources")
        self._respira_checked = set(rs) if rs else set()
        # fill in construction defaults for any keys the profile doesn't set,
        # so switching profiles never carries over the previous profile's values
        vals = {**self._defaults, **{k: v for k, v in vals.items() if v is not None}}
        wm = self._widget_map()
        # stage first so the phase/grade combos repopulate, then everything else
        for key in ["stage", "phase", "grade"] + [k for k in vals if k not in ("stage", "phase", "grade")]:
            w, v = wm.get(key), vals.get(key)
            if w is None or v is None:
                continue
            disp = self._KEY_TO_COMBO.get(key)
            if disp is not None and v is not None:
                # accept internal keys (current format) and legacy display
                # names saved in any language (convert to key, then display)
                to_key = self._COMBO_TO_KEY[key]
                v = disp(to_key(str(v)))
            try:
                if isinstance(w, QComboBox):
                    i = w.findText(str(v))
                    if i >= 0:
                        w.setCurrentIndex(i)
                elif isinstance(w, QCheckBox):
                    w.setChecked(bool(v))
                else:
                    w.setValue(v)
            except (TypeError, ValueError):
                pass  # tolerate hand-edited settings with wrong value types
        self._loading = prev

    # ---- profile store (JSON: {version, current, profiles: {name: state}}) ----
    def _read_store(self) -> dict:
        try:
            with open(self._settings_file) as f:
                obj = json.load(f)
        except (OSError, ValueError):
            obj = None
        if isinstance(obj, dict) and "profiles" in obj:
            return obj
        # migrate a flat v1 settings dict into a single "Default" profile
        flat = obj if isinstance(obj, dict) else {}
        return {"version": 2, "current": "Default", "profiles": {"Default": flat}}

    def _write_store(self, obj: dict):
        try:
            with open(self._settings_file, "w") as f:
                json.dump(obj, f, indent=1)
        except OSError:
            pass

    def _save_settings(self):
        obj = self._read_store()
        cur = obj.get("current", "Default")
        obj.setdefault("profiles", {})[cur] = self._collect_state()
        obj["current"] = cur
        self._write_store(obj)

    def _load_settings(self):
        obj = self._read_store()
        profs = obj.get("profiles", {})
        cur = obj.get("current", "Default")
        if cur not in profs and profs:
            cur = next(iter(profs))
        self._apply_state(profs.get(cur, {}))
        self._refresh_profile_combo(cur)

    def _refresh_profile_combo(self, current: str):
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for name in self._read_store().get("profiles", {}):
            self.profile_combo.addItem(name)
        i = self.profile_combo.findText(current)
        if i >= 0:
            self.profile_combo.setCurrentIndex(i)
        self.profile_combo.blockSignals(False)

    def _switch_profile(self, name: str):
        if self._loading or not name:
            return
        obj = self._read_store()
        obj["current"] = name
        self._write_store(obj)
        self._apply_state(obj.get("profiles", {}).get(name, {}))
        self.recalc()

    def _new_profile(self):
        name, ok = QInputDialog.getText(self, tr("New / Save As"), tr("Profile name:"))
        name = (name or "").strip()
        if not ok or not name:
            return
        obj = self._read_store()
        obj.setdefault("profiles", {})[name] = self._collect_state()
        obj["current"] = name
        self._write_store(obj)
        self._refresh_profile_combo(name)

    def _delete_profile(self):
        obj = self._read_store()
        profs = obj.get("profiles", {})
        if len(profs) <= 1:
            return  # always keep at least one profile
        profs.pop(obj.get("current"), None)
        newcur = next(iter(profs))
        obj["current"] = newcur
        self._write_store(obj)
        self._apply_state(profs.get(newcur, {}))
        self._refresh_profile_combo(newcur)
        self.recalc()

    def _reset_profile(self):
        self._apply_state(self._defaults)
        self.recalc()

    def _build_toolbar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.addWidget(QLabel(tr("Profile:")))
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(140)
        self.profile_combo.currentTextChanged.connect(self._switch_profile)
        bar.addWidget(self.profile_combo)
        for text, slot in ((tr("New / Save As…"), self._new_profile),
                           (tr("Delete"), self._delete_profile),
                           (tr("Reset"), self._reset_profile)):
            b = QPushButton(text); b.clicked.connect(slot); bar.addWidget(b)
        bar.addStretch(1)
        # Update notice: hidden until a newer GitHub release is found.
        self.update_label = QLabel()
        self.update_label.setOpenExternalLinks(True)
        self.update_label.setVisible(False)
        bar.addWidget(self.update_label)
        b = QPushButton(tr("Check for updates"))
        b.setFlat(True)
        b.setToolTip(tr("Installed: v{}. Checks the latest GitHub release.").format(__version__))
        b.clicked.connect(lambda: self._check_updates(manual=True))
        bar.addWidget(b)
        d = QPushButton(tr("Donate ♥"))
        d.setFlat(True)
        d.setToolTip(tr("Support development by gifting in-game vouchers."))
        d.clicked.connect(self._show_donate)
        bar.addWidget(d)
        bar.addWidget(QLabel(tr("Theme:")))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(theme.THEMES)
        self.theme_combo.setCurrentText(self._theme)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        bar.addWidget(self.theme_combo)
        bar.addWidget(QLabel(tr("Language:")))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(list(i18n.LANGS.values()))
        self.lang_combo.setCurrentText(i18n.LANGS[i18n.get_lang()])
        self.lang_combo.currentTextChanged.connect(self._on_lang_changed)
        bar.addWidget(self.lang_combo)
        return bar

    def _on_lang_changed(self, disp: str):
        code = next((k for k, v in i18n.LANGS.items() if v == disp), "en")
        if code == i18n.get_lang():
            return
        # Pragmatic full rebuild (mirrors the theme approach): capture the
        # inputs as internal keys, switch language, rebuild the UI, re-apply.
        state = self._collect_state()
        prev, self._loading = self._loading, True
        i18n.set_lang(code)
        obj = self._read_store(); obj["lang"] = code; self._write_store(obj)
        self._build_ui()
        self._wire()
        self._on_stage_changed()
        self._refresh_profile_combo(self._read_store().get("current", "Default"))
        self._apply_state(state)
        self._loading = prev
        self.recalc()

    # ---- donate ------------------------------------------------------------
    def _show_donate(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(tr("Support the calculator"))
        v = QVBoxLayout(dlg)
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
        bb.rejected.connect(dlg.reject)
        bb.clicked.connect(dlg.accept)
        v.addWidget(bb)
        dlg.exec()

    # ---- update check ----------------------------------------------------
    def _check_updates(self, manual: bool = False):
        req = QNetworkRequest(QUrl(f"https://api.github.com/repos/{REPO}/releases/latest"))
        req.setHeader(QNetworkRequest.UserAgentHeader, f"BreakthroughCalc/{__version__}")
        req.setTransferTimeout(5000)
        reply = self._nam.get(req)
        reply.finished.connect(lambda: self._on_update_reply(reply, manual))

    def _on_update_reply(self, reply: QNetworkReply, manual: bool):
        reply.deleteLater()
        latest, url = None, f"https://github.com/{REPO}/releases/latest"
        if reply.error() == QNetworkReply.NoError:
            try:
                data = json.loads(bytes(reply.readAll()).decode("utf-8"))
                latest = _version_tuple(data.get("tag_name", ""))
                url = data.get("html_url") or url
            except ValueError:
                latest = None
        if latest is None:
            if manual:
                self.update_label.setText(tr("Update check failed"))
                self.update_label.setVisible(True)
            return
        if latest > _version_tuple(__version__):
            tag = ".".join(str(x) for x in latest)
            self.update_label.setText(f'<a href="{url}">{tr("Update available: v{}").format(tag)}</a>')
            self.update_label.setVisible(True)
        elif manual:
            self.update_label.setText(tr("Up to date (v{})").format(__version__))
            self.update_label.setVisible(True)

    def _on_theme_changed(self, name: str):
        self._theme = name
        self._acc = theme.accents(name)
        theme.apply(QApplication.instance(), name)
        for lbl in self._muted_labels:
            lbl.setStyleSheet(f"color: {self._acc['muted']};")
        for lbl in self.pin_labels.values():
            lbl.setStyleSheet(f"font-weight: bold; color: {self._acc['good']};")
        self.o_error.setStyleSheet(f"color: {self._acc['bad']};")
        self._rebuild_info_tab()
        self.recalc()
        obj = self._read_store(); obj["theme"] = name; self._write_store(obj)

    def _on_color_scheme_changed(self, *_):
        # Re-apply only when tracking the OS scheme; explicit themes are static.
        if self._theme == "System":
            self._on_theme_changed("System")

    # ---- A/B compare -----------------------------------------------------
    def _pin_results(self):
        for _, attr in self.RESULT_ROWS:
            self.pin_labels[attr].setText(getattr(self, attr).text())
        self.pin_box.setTitle(
            f"{tr('Pinned A')} — {self.stage.currentText()} {self.phase.currentText()} {self.grade.currentText()}")
        self.pin_box.setVisible(True)

    def _unpin_results(self):
        self.pin_box.setVisible(False)

    # ---- Cultivation Bonus helper ----------------------------------------
    def _array_expected(self):
        """(abode_aura, implied_bonus_or_None, expected_speed) or None if no aura entered."""
        abode = self.abode_aura.value()
        if abode <= 0:
            return None
        bonus = None
        if stage_key(self.stage.currentText()) in BASE_ENERGY_STAGES:
            bonus = abode / BASE_ENERGY - 1
        absorb = self.absorb.value() / 100.0
        spd = abode * absorb if absorb > 0 else None
        return abode, bonus, spd

    # ---- pill-effect sources (technique books, curios, …) ----------------
    def _add_pe_row(self, label: str = "", value: float = 0.0):
        row = QWidget(); h = QHBoxLayout(row); h.setContentsMargins(0, 0, 0, 0)
        le = QLineEdit(label); le.setPlaceholderText(tr("source (e.g. technique book, curio)"))
        sp = QDoubleSpinBox(); sp.setRange(0, 500); sp.setDecimals(2); sp.setSuffix(" %"); sp.setValue(value)
        rm = QPushButton("✕"); rm.setFixedWidth(28)
        h.addWidget(le, 1); h.addWidget(sp); h.addWidget(rm)
        self.pe_rows_layout.addWidget(row)
        entry = (le, sp, row)
        self.pe_rows.append(entry)
        le.textChanged.connect(self.recalc)
        sp.valueChanged.connect(self.recalc)
        rm.clicked.connect(lambda: self._remove_pe_row(entry))
        return entry

    def _remove_pe_row(self, entry):
        if entry in self.pe_rows:
            self.pe_rows.remove(entry)
        entry[2].setParent(None)
        if not self.pe_rows:            # keep at least one row
            self._add_pe_row()
        self.recalc()

    def _sync_catalog_menu(self):
        labels = {le.text() for le, _, _ in self.pe_rows}
        for act in self._cat_menu.actions():
            act.setChecked(act.data()["name"] in labels)

    def _toggle_catalog_source(self, act):
        src = act.data()
        existing = [e for e in self.pe_rows if e[0].text() == src["name"]]
        if existing:
            for e in existing:
                self._remove_pe_row(e)
        else:
            if src.get("prompt", {}).get("kind") == "star_upgrade":
                picked = self._ask_star_upgrade(src)
                if picked is None:        # user cancelled
                    return
                value = picked
            else:
                value = float(src["percent"]) if src.get("percent") else 0.0
            # drop a leftover blank placeholder row
            blanks = [e for e in self.pe_rows if not e[0].text() and e[1].value() == 0]
            self._add_pe_row(src["name"], value)
            for e in blanks:
                self._remove_pe_row(e)
            self.recalc()

    def _sync_respira_menu(self):
        for act in self._respira_menu.actions():
            src = act.data()
            if src:
                act.setChecked(src["name"] in self._respira_checked)

    def _toggle_respira_source(self, act):
        src = act.data()
        if not src:
            return
        if act.isChecked():
            self._respira_checked.add(src["name"])
            self.respira_per_day.setValue(self.respira_per_day.value() + float(src["value"]))
        else:
            self._respira_checked.discard(src["name"])
            self.respira_per_day.setValue(max(0.0, self.respira_per_day.value() - float(src["value"])))
        self.recalc()

    def _ask_star_upgrade(self, src) -> float | None:
        """Small dialog matching the in-game curio upgrade screen: pick star and
        upgrade level, return the computed pill-effect %."""
        p = src["prompt"]

        def value_for(star, upgrade):
            return p["base"] + p["per_upgrade"] * upgrade + p["star_add"][star - 1]

        dlg = QDialog(self)
        dlg.setWindowTitle(src["name"])
        lay = QFormLayout(dlg)
        star = QComboBox(); star.addItems([f"{i}★" for i in range(1, p["stars"] + 1)])
        upg = QComboBox(); upg.addItems([str(i) for i in range(p["max_upgrade"] + 1)])
        out = QLabel()
        out.setStyleSheet(f"color: {self._acc['muted']};")

        def refresh():
            out.setText(tr("Cultivation Pill Effect: {}%").format(
                f"{value_for(star.currentIndex() + 1, upg.currentIndex()):.1f}"))
        star.currentIndexChanged.connect(refresh)
        upg.currentIndexChanged.connect(refresh)
        refresh()
        lay.addRow(tr("Star"), star)
        lay.addRow(tr("Upgrade level"), upg)
        lay.addRow("", out)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        lay.addRow(buttons)
        if dlg.exec() != QDialog.Accepted:
            return None
        return round(value_for(star.currentIndex() + 1, upg.currentIndex()), 1)

    def _pill_effect_total(self) -> float:
        return sum(sp.value() for _, sp, _ in self.pe_rows)

    def _set_pill_sources(self, sources):
        for _, _, row in list(self.pe_rows):
            row.setParent(None)
        self.pe_rows.clear()
        for lbl, val in sources:
            self._add_pe_row(str(lbl), float(val))
        if not self.pe_rows:
            self._add_pe_row()

    def _update_pill_attempts(self):
        self.pe_total.setText(tr("Total: {} %").format(f"{self._pill_effect_total():.2f}"))
        used = self.gold_day.value() + self.purple_day.value() + self.blue_day.value()
        limit = self.pill_limit.value()
        msg = tr("Attempts used: {} / {} (shared; vase red pills exempt)").format(f"{used:g}", f"{limit:g}")
        if used > limit + 1e-9:
            msg += tr("  ⚠ over limit — extra pills won't count")
            self.pill_attempts.setStyleSheet(f"color: {self._acc['warn']};")
        else:
            self.pill_attempts.setStyleSheet(f"color: {self._acc['muted']};")
        self.pill_attempts.setText(msg)

    def _update_array_out(self):
        r = self._array_expected()
        if r is None:
            self.array_out.setVisible(False)
            self.array_apply.setVisible(False)
            return
        self.array_out.setVisible(True)
        self.array_apply.setVisible(True)
        abode, bonus, spd = r
        # Rich text so only the stale-speed warning is highlighted red.
        parts = []
        if bonus is not None:
            parts.append(tr("Implied total aura bonus: {}%  (Abode = 130 × {})").format(
                f"{bonus * 100:.1f}", f"{1 + bonus:.3f}"))
        if spd is not None:
            line = tr("Expected speed: {} / Cosmoapsis").format(f"{spd:.2f}")
            entered = self.speed.value()
            if entered > 0:
                diff = (entered / spd - 1) * 100
                if abs(diff) > 0.5:
                    line += (f"<span style='color:{self._acc['bad']}'>"
                             + tr("  — entered speed {} is {}% off; one of the readings is stale").format(
                                 f"{entered:.2f}", f"{diff:+.1f}")
                             + "</span>")
            parts.append(line)
        self.array_out.setText("<br>".join(parts))
        self.array_apply.setEnabled(spd is not None)

    def _apply_array_speed(self):
        r = self._array_expected()
        if r and r[2] is not None:
            self.speed.setValue(r[2])

    def closeEvent(self, event):
        self._save_settings()
        super().closeEvent(event)

    def _update_absorb_base(self):
        """Show the selected Grade's base Absorption Ratio, and warn on under-entry."""
        idx = self.engine.row_index(
            stage_key(self.stage.currentText()),
            phase_key(self.phase.currentText()),
            self.grade.currentText(),
        )
        if idx < 0:
            self.absorb_base.setText("")
            return
        base = self.engine.rows[idx]["low"] * 100
        entered = self.absorb.value()
        warn = False
        if stage_key(self.stage.currentText()) in STRIVE_STAGES:
            strive = (entered / base - 1) * 100 if base > 0 else 0.0
            if abs(strive) < 1e-6:
                strive = 0.0
            msg = tr("Base Absorption: {}%  ·  Strive: {}%").format(f"{base:g}", f"{strive:.0f}")
            stages = self.engine.stages()
            cur = stage_key(self.stage.currentText())
            mortal = cur in stages and stages.index(cur) <= stages.index("Incarnation")
            if entered and entered < base - 1e-9:
                msg += tr("  ⚠ below base — Strive can't be negative"); warn = True
            elif strive > 120 + 1e-9:
                if mortal:
                    msg += tr("  ⚠ Strive over the 120% cap"); warn = True
                else:
                    msg += tr("  · Strive above 120% — normal in later realms (overcap); "
                              "cap tables beyond the mortal world aren't modeled.")
        else:
            msg = tr("Base Absorption: {}%  (Strive unlocks at Nascent Soul)").format(f"{base:g}")
            if entered and entered < base - 1e-9:
                msg += tr("  ⚠ below base"); warn = True
        self.absorb_base.setStyleSheet(f"color: {self._acc['warn'] if warn else self._acc['muted']};")
        self.absorb_base.setText(msg)

    def _fmt_band(self, d: float, band: tuple) -> str:
        lo, hi = band
        point = tr_duration(fmt_days(d))
        if hi - lo < 1e-9 or d <= 0 or fmt_days(lo) == fmt_days(hi):
            return point
        return (f"{point}  <span style='color:{self._acc['muted']}'>"
                + tr("(best {} / worst {})").format(
                    tr_duration(fmt_days(lo)), tr_duration(fmt_days(hi)))
                + "</span>")

    def recalc(self, *_):
        if not self._loading:
            self._save_settings()
        self.copy_btn.setText(tr("Copy results"))
        self._update_absorb_base()
        self._update_array_out()
        self._update_pill_attempts()
        self._last = res = self.engine.calculate(self._inputs())
        if not res.valid:
            for _, attr in self.RESULT_ROWS:
                getattr(self, attr).setText("—")
            self.o_error.setText(tr(res.error))
            return
        self.o_error.setText(tr(res.error))
        self.o_phase.setText(self._fmt_band(res.phase_days, res.phase_band))
        self.o_stage.setText(self._fmt_band(res.stage_days, res.stage_band))
        self.o_target.setText(self._fmt_band(res.target_days, res.target_band)
                              if res.target_valid else "—")
        self.o_abode.setText(f"{res.abode_aura:,.1f}")
        self.o_basexp.setText(f"{res.base_xp_per_day:,.0f}")
        self.o_effxp.setText(f"{res.effective_xp_per_day:,.0f}")
        self.o_pillxp.setText(f"{res.pill_xp_per_day:,.0f}")
        flat_share = ((res.pill_xp_per_day + res.respira_xp_per_day)
                      / res.effective_xp_per_day * 100
                      if res.effective_xp_per_day else 0.0)
        self.o_speedup.setText(tr("{}% of daily XP / +{}% speed").format(
            f"{flat_share:.1f}", f"{res.gem_speedup * 100:.0f}"))
        self.o_speedup.setToolTip(tr(
            "Share of your effective daily XP that comes from flat sources "
            "(pills + Respira), and the Aura Gem's speed bonus on cultivation. "
            "Flat XP does not scale with grade EXP, so a high share means slower "
            "progress at higher grades than raw speed suggests."))
        self.o_mythic.setText(f"{res.mythic_pills_per_day:.2f}")
        self.o_pearl.setText(f"{res.pearl_xp_per_day:,.0f}")
        self.o_respira.setText(f"{res.respira_xp_per_day:,.0f}")
        self.o_fruit.setText(f"{res.fruit_xp:,.0f}")
        self.o_fruit_days.setText(tr_duration(fmt_days(res.fruit_days_saved)))

    def _copy_results(self):
        import re
        plain = lambda s: re.sub(r"<[^>]+>", "", s)
        rows = [
            (tr("Stage"), self.stage.currentText()), (tr("Half-step"), self.phase.currentText()),
            (tr("Grade"), self.grade.currentText()),
        ]
        rows += [(tr(text), plain(getattr(self, attr).text())) for text, attr in self.RESULT_ROWS]
        text = "\n".join(f"{k}: {v}" for k, v in rows)
        QApplication.clipboard().setText(text)
        self.copy_btn.setText(tr("Copied ✓"))


def _icon_path() -> str:
    import sys
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for p in (os.path.join(base, "breakthrough-calc.png"),
              os.path.join(base, "packaging", "breakthrough-calc.png")):
        if os.path.exists(p):
            return p
    return ""


def main():
    import sys
    from PySide6.QtGui import QIcon
    app = QApplication(sys.argv)
    icon = _icon_path()
    if icon:
        app.setWindowIcon(QIcon(icon))
    win = MainWindow()
    theme.apply(app, win._theme)
    win.show()
    win.raise_()
    win.activateWindow()
    sys.exit(app.exec())
