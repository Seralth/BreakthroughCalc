"""Qt GUI for the Breakthrough Calculator."""

from __future__ import annotations

import json
import os
import sys

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import (
    QAbstractSpinBox, QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QGridLayout, QHBoxLayout, QInputDialog, QLabel,
    QLineEdit, QMainWindow, QMenu, QPushButton, QScrollArea, QSpinBox, QVBoxLayout,
    QWidget,
)


class _WheelGuard(QObject):
    """Swallow wheel events on unfocused spin/combo widgets so scrolling the
    form doesn't silently change values (Qt steps them even without focus)."""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel and not obj.hasFocus():
            event.ignore()
            return True
        return super().eventFilter(obj, event)

from .engine import Engine, Inputs, fmt_days, load_pill_sources

PHASE_LABELS = {"N/A": "N/A", "EARLY": "Early", "MIDDLE": "Middle", "LATE": "Late"}
PHASE_KEYS = {v: k for k, v in PHASE_LABELS.items()}

# Display-only canonical Stage names; internal data keys (and settings) stay unchanged.
STAGE_LABELS = {"Nascent": "Nascent Soul"}
STAGE_KEYS = {v: k for k, v in STAGE_LABELS.items()}


def stage_disp(key: str) -> str:
    return STAGE_LABELS.get(key, key)


def stage_key(disp: str) -> str:
    return STAGE_KEYS.get(disp, disp)


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
        self.setWindowTitle("Breakthrough Calculator")
        self.engine = Engine()
        self._settings_file = settings_path()
        self._loading = True
        self._build_ui()
        self._wire()
        self._on_stage_changed()
        self._load_settings()
        self._loading = False
        self.recalc()

    # ---- UI construction -------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)
        root.addLayout(self._build_toolbar())
        outer = QHBoxLayout()
        root.addLayout(outer)

        # left column: inputs (scrollable)
        left = QWidget()
        lv = QVBoxLayout(left)

        cult = QGroupBox("Cultivation Base")
        f = QFormLayout(cult)
        self.stage = QComboBox(); self.stage.addItems([stage_disp(s) for s in self.engine.stages()])
        self.phase = QComboBox()
        self.grade = QComboBox()
        self.completion = QDoubleSpinBox(); self.completion.setRange(0, 100); self.completion.setSuffix(" %")
        self.speed = QDoubleSpinBox(); self.speed.setRange(0, 1e12); self.speed.setDecimals(2)
        self.absorb = QDoubleSpinBox(); self.absorb.setRange(0, 10000); self.absorb.setDecimals(3); self.absorb.setSuffix(" %")
        self.gem = QComboBox(); self.gem.addItems(list(self.engine.data["gem_bonus"].keys()))
        self.target = QComboBox(); self.target.addItem(""); self.target.addItems(self.engine.stages())
        f.addRow("Stage", self.stage)
        f.addRow("Half-step", self.phase)
        f.addRow("Grade", self.grade)
        f.addRow("Grade progress", self.completion)
        # Abode Aura, Absorption Ratio, and Cultivation Speed all come off the
        # same in-game Cultivation Bonus screen. Enter Aura + Absorption and
        # the Apply button appears to fill in Speed (= Aura × Absorption);
        # Speed stays directly editable for anyone who prefers typing it.
        self.abode_aura = QDoubleSpinBox(); self.abode_aura.setRange(0, 1e9)
        self.abode_aura.setDecimals(2)
        self.abode_aura.setToolTip(
            "Your Abode Aura as shown on the Cultivation Bonus screen. With Absorption "
            "Ratio entered, Cultivation Speed = Abode Aura × Absorption Ratio.")
        f.addRow("Abode Aura", self.abode_aura)
        f.addRow("Absorption Ratio", self.absorb)
        self.absorb_base = QLabel("")
        self.absorb_base.setStyleSheet("color: #888;")
        f.addRow("", self.absorb_base)
        self.array_out = QLabel("—"); self.array_out.setWordWrap(True)
        self.array_out.setStyleSheet("color: #888;")
        f.addRow("", self.array_out)
        self.array_apply = QPushButton("Apply to Cultivation Speed")
        self.array_apply.clicked.connect(self._apply_array_speed)
        f.addRow("", self.array_apply)
        f.addRow("Cultivation Speed (XP / Cosmoapsis)", self.speed)
        f.addRow("Aura Gem", self.gem)
        f.addRow("Target Stage", self.target)
        self.top_stage = QComboBox(); self.top_stage.addItem("")
        self.top_stage.addItems([stage_disp(s) for s in self.engine.stages()])
        self.top_stage.setToolTip(
            "Optional: your server's #1 cultivator's Stage. Models your Strive stepping DOWN as you "
            "break through toward them (estimated; assumes #1 stays put; live value is server-computed hourly). "
            "Leave blank to hold Strive constant.")
        f.addRow("Server #1's Stage (Strive)", self.top_stage)
        lv.addWidget(cult)

        pills = QGroupBox("Cultivation Pills")
        f = QFormLayout(pills)
        self.pill_rank = QComboBox(); self.pill_rank.addItems(list(self.engine.data["pill_xp"].keys()))
        self.pill_limit = QDoubleSpinBox(); self.pill_limit.setRange(0, 1e6)
        self.gold_day = QDoubleSpinBox(); self.gold_day.setRange(0, 1e6)
        self.purple_day = QDoubleSpinBox(); self.purple_day.setRange(0, 1e6)
        self.blue_day = QDoubleSpinBox(); self.blue_day.setRange(0, 1e6)
        f.addRow("Pill rank", self.pill_rank)

        # Cultivation pill effect = sum of contributions (technique books, curios,
        # etc.). Record each source once so swapping gear means editing one row.
        pe_wrap = QWidget(); pe_v = QVBoxLayout(pe_wrap); pe_v.setContentsMargins(0, 0, 0, 0)
        self.pe_rows = []
        self.pe_rows_layout = QVBoxLayout(); self.pe_rows_layout.setContentsMargins(0, 0, 0, 0)
        pe_v.addLayout(self.pe_rows_layout)
        self.pe_total = QLabel("Total: 0.00 %"); self.pe_total.setStyleSheet("color: #888;")
        add_pe = QPushButton("＋ Add source")
        add_pe.setToolTip("Add a pill-effect source (a technique book, a curio, …). Their percentages sum.")
        add_pe.clicked.connect(lambda: (self._add_pe_row(), self.recalc()))
        pe_bottom = QHBoxLayout(); pe_bottom.addWidget(self.pe_total, 1); pe_bottom.addWidget(add_pe)
        self.pe_catalog = load_pill_sources()
        if self.pe_catalog:
            cat_btn = QPushButton("＋ From catalog")
            cat_btn.setToolTip("Known pill-effect sources from the game data. Check to add "
                               "(prefilled, editable), uncheck to remove.")
            cat_menu = QMenu(cat_btn)
            cat_menu.setToolTipsVisible(True)
            for src in self.pe_catalog:
                act = cat_menu.addAction(f'{src["name"]}  {src["percent"]:g}%')
                act.setCheckable(True)
                act.setToolTip(src.get("note", ""))
                act.setData(src)
            cat_menu.aboutToShow.connect(self._sync_catalog_menu)
            cat_menu.triggered.connect(self._toggle_catalog_source)
            cat_btn.setMenu(cat_menu)
            self._cat_menu = cat_menu
            pe_bottom.addWidget(cat_btn)
        pe_v.addLayout(pe_bottom)
        f.addRow("Cultivation pill effect", pe_wrap)

        self.pill_limit.setToolTip("Shared daily attempt limit for all cultivation pills (vase red pills are exempt).")
        f.addRow("Daily pill attempts (shared)", self.pill_limit)
        f.addRow("Legendary (Gold) used / day", self.gold_day)
        f.addRow("Epic (Purple) used / day", self.purple_day)
        f.addRow("Rare (Blue) used / day", self.blue_day)
        self.pill_attempts = QLabel("")
        self.pill_attempts.setStyleSheet("color: #888;")
        f.addRow("", self.pill_attempts)
        marks = QHBoxLayout()
        self.mark_blue = QDoubleSpinBox(); self.mark_purple = QDoubleSpinBox(); self.mark_gold = QDoubleSpinBox()
        for w, name in ((self.mark_blue, "Rare"), (self.mark_purple, "Epic"), (self.mark_gold, "Legendary")):
            w.setRange(0, 10); w.setSingleStep(0.01); w.setDecimals(2)
            w.setToolTip(
                "Your in-game 'Cultivation Pill EXP Bonus' for this pill rarity (mainly from "
                "Constellation Altar Star Marks). Entered as a ratio: 0.10 = +10%.")
            marks.addWidget(QLabel(name)); marks.addWidget(w)
        f.addRow("Star Marks (+XP ratio)", marks)
        lv.addWidget(pills)

        arts = QGroupBox("Creation Artifacts")
        g = QGridLayout(arts)
        g.addWidget(QLabel("<b>Artifact</b>"), 0, 0); g.addWidget(QLabel("<b>Star</b>"), 0, 2); g.addWidget(QLabel("<b>Skin</b>"), 0, 3)
        g.addWidget(QLabel("<b>Charge</b>"), 0, 4)
        self.vase = QCheckBox("Starsea Vase"); self.vase_star = QComboBox(); self.vase_star.addItems(STARS); self.vase_skin = QCheckBox()
        self.vase_skin.setToolTip("Transmog skin: refined pills give +8% Cultivation EXP")
        self.mirror = QCheckBox("Dual-Star Mirror"); self.mirror_star = QComboBox(); self.mirror_star.addItems(STARS); self.mirror_skin = QCheckBox()
        self.mirror_skin.setToolTip("Transmog skin: Duplication consumes 10% less Energy")
        self.pearl = QCheckBox("Timereversal Pearl"); self.pearl_star = QComboBox(); self.pearl_star.addItems(STARS)
        self.pearl_skin = QCheckBox()
        self.pearl_skin.setToolTip("Transmog skin: Timereversal Pearl Energy Cost -10%")
        self.pearl_xp10 = QDoubleSpinBox(); self.pearl_xp10.setRange(0, 1e12)
        charge_tip = "Daily Energy Charge: 30 Fateum/Destium adds 100 Energy to this artifact, once per day. Check if you use it every day."
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
        self.vase_input_label = QLabel("Vase input pill")
        self.vase_input = QComboBox()
        self.vase_input.addItems(["Blue/White", "Purple (Epic)", "Gold (Legendary)"])
        self.vase_input.setToolTip(
            "Which pill quality you refine into red pills. Refines are discounted by input "
            "quality (Epic -5%, Legendary -20% Energy), so feeding gold pills yields extra "
            "red pills over time. Base cost also depends on pill rank (75-100 energy).")
        g.addWidget(self.vase_input_label, 4, 0); g.addWidget(self.vase_input, 4, 2, 1, 2)
        self.pearl_xp10_label = QLabel("EXP per 10 energy")
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

        fruit = QGroupBox("Myrimon Fruit")
        f = QFormLayout(fruit)
        self.fruit_rank = QComboBox(); self.fruit_rank.addItems(list(self.engine.data["fruit_xp"].keys()))
        self.fruit_high = QCheckBox("Highest rank (+50%)")
        self.fruit_count = QDoubleSpinBox(); self.fruit_count.setRange(0, 1e6)
        self.lvl_culti = QSpinBox(); self.lvl_quality = QSpinBox(); self.lvl_gush = QSpinBox()
        for w in (self.lvl_culti, self.lvl_quality, self.lvl_gush):
            w.setRange(0, 30)
        self.extractor = QComboBox(); self.extractor.addItems(self.engine.data["rarity_names"])
        f.addRow("Fruit rank", self.fruit_rank)
        f.addRow("", self.fruit_high)
        f.addRow("No. of Myrimon Fruits", self.fruit_count)
        f.addRow("Culti level", self.lvl_culti)
        f.addRow("Quality level", self.lvl_quality)
        f.addRow("Gush level", self.lvl_gush)
        f.addRow("Aura Extractor quality", self.extractor)
        lv.addWidget(fruit)

        note = QLabel(
            "Note: Strive (the catch-up bonus, from Nascent Soul) fades as you close the gap to "
            "your server's #1. Set \"Server #1's Stage\" above to model that drop-off (estimated); "
            "leave it blank to hold Strive constant. Low/zero-strive players are unaffected either way.")
        note.setWordWrap(True); note.setStyleSheet("color: #888; font-size: 11px;")
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
            ("Speed-up (pills / gem)", "o_speedup"),
            ("Mythic pills / day", "o_mythic"),
            ("Pearl XP / day", "o_pearl"),
            ("XP from fruits", "o_fruit"),
            ("Fruit time saved", "o_fruit_days"),
        ]

        def mklabel() -> QLabel:
            lbl = QLabel("—"); lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            lbl.setStyleSheet("font-weight: bold;")
            return lbl

        right = QGroupBox("Results (current)")
        rf = QFormLayout(right)
        for text, attr in self.RESULT_ROWS:
            lbl = mklabel(); setattr(self, attr, lbl); rf.addRow(text, lbl)
        self.o_error = QLabel(""); self.o_error.setStyleSheet("color: #c04040;"); self.o_error.setWordWrap(True)
        rf.addRow(self.o_error)
        btns = QHBoxLayout()
        self.copy_btn = QPushButton("Copy results"); self.copy_btn.clicked.connect(self._copy_results)
        self.pin_btn = QPushButton("Pin as A"); self.pin_btn.clicked.connect(self._pin_results)
        btns.addWidget(self.copy_btn); btns.addWidget(self.pin_btn)
        rf.addRow(btns)
        outer.addWidget(right, 1)

        self.pin_box = QGroupBox("Pinned A")
        pf = QFormLayout(self.pin_box)
        self.pin_labels = {}
        for text, attr in self.RESULT_ROWS:
            lbl = mklabel(); lbl.setStyleSheet("font-weight: bold; color: #4a7;"); self.pin_labels[attr] = lbl
            pf.addRow(text, lbl)
        self.unpin_btn = QPushButton("Clear A"); self.unpin_btn.clicked.connect(self._unpin_results)
        pf.addRow(self.unpin_btn)
        self.pin_box.setVisible(False)
        outer.addWidget(self.pin_box, 1)

        self.setCentralWidget(central)
        self.resize(1180, 680)

    # ---- signal wiring ---------------------------------------------------
    def _wire(self):
        self.stage.currentTextChanged.connect(self._on_stage_changed)
        self.phase.currentTextChanged.connect(self._on_phase_changed)
        for w in (self.grade, self.gem, self.target, self.top_stage, self.pill_rank, self.vase_star,
                  self.vase_input, self.mirror_star, self.pearl_star, self.fruit_rank, self.extractor):
            w.currentTextChanged.connect(self.recalc)
        for w in (self.completion, self.speed, self.absorb, self.pill_limit,
                  self.gold_day, self.purple_day, self.blue_day, self.mark_blue,
                  self.mark_purple, self.mark_gold, self.pearl_xp10, self.fruit_count):
            w.valueChanged.connect(self.recalc)
        for w in (self.lvl_culti, self.lvl_quality, self.lvl_gush, self.abode_aura):
            w.valueChanged.connect(self.recalc)
        for w in (self.vase, self.vase_skin, self.vase_charge, self.mirror, self.mirror_skin,
                  self.mirror_charge, self.pearl, self.pearl_skin, self.pearl_charge,
                  self.fruit_high):
            w.toggled.connect(self.recalc)
        self._install_wheel_guard()
        self._install_tooltips()

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
            self.gem: "Aura Gem rarity. Modeled as a flat cultivation speed-up (Donk's approximation of the storage mechanic).",
            self.target: "Optional: a future Stage to time your arrival at.",
            self.pill_limit: "Daily pill-use limit that caps Gold/Purple/Blue usage.",
            self.pearl_xp10: "Timereversal Pearl: EXP granted per 10 energy.",
            self.fruit_count: "Number of Myrimon Fruits processed through the Aura Extractor.",
        }
        for w, t in tips.items():
            w.setToolTip(t)

    def _on_stage_changed(self):
        stage = stage_key(self.stage.currentText())
        self.phase.blockSignals(True)
        self.phase.clear()
        self.phase.addItems([PHASE_LABELS.get(p, p) for p in self.engine.phases_for(stage)])
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
        stage, phase = stage_key(self.stage.currentText()), PHASE_KEYS.get(self.phase.currentText(), self.phase.currentText())
        self.grade.blockSignals(True)
        self.grade.clear()
        self.grade.addItems(self.engine.grades_for(stage, phase))
        self.grade.blockSignals(False)
        self.recalc()

    # ---- calc ------------------------------------------------------------
    def _inputs(self) -> Inputs:
        return Inputs(
            stage=stage_key(self.stage.currentText()), phase=PHASE_KEYS.get(self.phase.currentText(), self.phase.currentText()),
            grade=self.grade.currentText(), grade_completion=self.completion.value() / 100.0,
            culti_speed=self.speed.value(), absorption_ratio=self.absorb.value() / 100.0,
            aura_gem=self.gem.currentText(), target_stage=stage_key(self.target.currentText()),
            top_stage=stage_key(self.top_stage.currentText()),
            pill_rank=self.pill_rank.currentText(), pill_effect=self._pill_effect_total() / 100.0,
            pill_limit=self.pill_limit.value(), gold_per_day=self.gold_day.value(),
            purple_per_day=self.purple_day.value(), blue_per_day=self.blue_day.value(),
            mark_blue=self.mark_blue.value(), mark_purple=self.mark_purple.value(),
            mark_gold=self.mark_gold.value(),
            vase=self.vase.isChecked(), vase_star=self.vase_star.currentText(),
            vase_skin=self.vase_skin.isChecked(),
            vase_input=self.vase_input.currentText().split("/")[0].split(" ")[0],
            mirror=self.mirror.isChecked(), mirror_star=self.mirror_star.currentText(),
            mirror_skin=self.mirror_skin.isChecked(),
            pearl=self.pearl.isChecked(), pearl_star=self.pearl_star.currentText(),
            pearl_skin=self.pearl_skin.isChecked(),
            pearl_xp_per_10=self.pearl_xp10.value(),
            vase_charge=self.vase_charge.isChecked(),
            mirror_charge=self.mirror_charge.isChecked(),
            pearl_charge=self.pearl_charge.isChecked(),
            fruit_rank=self.fruit_rank.currentText(), fruit_count=self.fruit_count.value(),
            fruit_highest_rank=self.fruit_high.isChecked(),
            lvl_culti=self.lvl_culti.value(), lvl_quality=self.lvl_quality.value(),
            lvl_gush=self.lvl_gush.value(), extractor_rarity=self.extractor.currentText(),
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
            "pearl_skin": self.pearl_skin,
            "pearl_xp10": self.pearl_xp10,
            "vase_charge": self.vase_charge, "mirror_charge": self.mirror_charge,
            "pearl_charge": self.pearl_charge,
            "fruit_rank": self.fruit_rank, "fruit_high": self.fruit_high,
            "fruit_count": self.fruit_count, "lvl_culti": self.lvl_culti,
            "lvl_quality": self.lvl_quality, "lvl_gush": self.lvl_gush,
            "extractor": self.extractor, "abode_aura": self.abode_aura,
        }

    def _collect_state(self) -> dict:
        vals = {}
        for key, w in self._widget_map().items():
            if isinstance(w, QComboBox):
                vals[key] = w.currentText()
            elif isinstance(w, QCheckBox):
                vals[key] = w.isChecked()
            else:
                vals[key] = w.value()
        vals["pill_sources"] = [[le.text(), sp.value()] for le, sp, _ in self.pe_rows]
        return vals

    def _apply_state(self, vals: dict):
        prev, self._loading = self._loading, True
        # pill-effect sources (migrate old single "pill_effect_pct" to one row)
        srcs = vals.get("pill_sources")
        if srcs is None and "pill_effect_pct" in vals:
            srcs = [["", vals["pill_effect_pct"]]]
        self._set_pill_sources(srcs if srcs is not None else [])
        wm = self._widget_map()
        # stage first so the phase/grade combos repopulate, then everything else
        for key in ["stage", "phase", "grade"] + [k for k in vals if k not in ("stage", "phase", "grade")]:
            w, v = wm.get(key), vals.get(key)
            if w is None or v is None:
                continue
            if key == "phase":
                v = PHASE_LABELS.get(str(v), v)
            if key in ("stage", "target", "top_stage"):
                v = stage_disp(str(v))
            if isinstance(w, QComboBox):
                i = w.findText(str(v))
                if i >= 0:
                    w.setCurrentIndex(i)
            elif isinstance(w, QCheckBox):
                w.setChecked(bool(v))
            else:
                w.setValue(v)
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
        name, ok = QInputDialog.getText(self, "New / Save As", "Profile name:")
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
        prev, self._loading = self._loading, True
        for w in self._widget_map().values():
            if isinstance(w, QComboBox):
                w.setCurrentIndex(0)
            elif isinstance(w, QCheckBox):
                w.setChecked(False)
            else:
                w.setValue(0)
        self._set_pill_sources([])
        self._loading = prev
        self.recalc()

    def _build_toolbar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(140)
        self.profile_combo.currentTextChanged.connect(self._switch_profile)
        bar.addWidget(self.profile_combo)
        for text, slot in (("New / Save As…", self._new_profile),
                           ("Delete", self._delete_profile),
                           ("Reset", self._reset_profile)):
            b = QPushButton(text); b.clicked.connect(slot); bar.addWidget(b)
        bar.addStretch(1)
        return bar

    # ---- A/B compare -----------------------------------------------------
    def _pin_results(self):
        for _, attr in self.RESULT_ROWS:
            self.pin_labels[attr].setText(getattr(self, attr).text())
        self.pin_box.setTitle(
            f"Pinned A — {self.stage.currentText()} {self.phase.currentText()} {self.grade.currentText()}")
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
        le = QLineEdit(label); le.setPlaceholderText("source (e.g. technique book, curio)")
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
            # drop a leftover blank placeholder row
            blanks = [e for e in self.pe_rows if not e[0].text() and e[1].value() == 0]
            self._add_pe_row(src["name"], float(src["percent"]))
            for e in blanks:
                self._remove_pe_row(e)
            self.recalc()

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
        self.pe_total.setText(f"Total: {self._pill_effect_total():.2f} %")
        used = self.gold_day.value() + self.purple_day.value() + self.blue_day.value()
        limit = self.pill_limit.value()
        msg = f"Attempts used: {used:g} / {limit:g} (shared; vase red pills exempt)"
        if used > limit + 1e-9:
            msg += "  ⚠ over limit — extra pills won't count"
            self.pill_attempts.setStyleSheet("color: #c07030;")
        else:
            self.pill_attempts.setStyleSheet("color: #888;")
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
        txt = ""
        stale = False
        if bonus is not None:
            txt = f"Implied total aura bonus: {bonus * 100:.1f}%  (Abode = 130 × {1 + bonus:.3f})"
        if spd is not None:
            entered = self.speed.value()
            txt += ("\n" if txt else "") + f"Expected speed: {spd:.2f} / Cosmoapsis"
            if entered > 0:
                diff = (entered / spd - 1) * 100
                if abs(diff) > 0.5:
                    stale = True
                    txt += f"  — entered speed {entered:.2f} is {diff:+.1f}% off; one of the readings is stale"
        self.array_out.setStyleSheet("color: #d64545;" if stale else "color: #888;")
        self.array_out.setText(txt)
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
            PHASE_KEYS.get(self.phase.currentText(), self.phase.currentText()),
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
            msg = f"Base Absorption: {base:g}%  ·  Strive: {strive:.0f}%"
            if entered and entered < base - 1e-9:
                msg += "  ⚠ below base — Strive can't be negative"; warn = True
            elif strive > 120 + 1e-9:
                msg += "  ⚠ Strive over the 120% cap"; warn = True
        else:
            msg = f"Base Absorption: {base:g}%  (Strive unlocks at Nascent Soul)"
            if entered and entered < base - 1e-9:
                msg += "  ⚠ below base"; warn = True
        self.absorb_base.setStyleSheet("color: #c07030;" if warn else "color: #888;")
        self.absorb_base.setText(msg)

    def recalc(self, *_):
        if not self._loading:
            self._save_settings()
        self.copy_btn.setText("Copy results")
        self._update_absorb_base()
        self._update_array_out()
        self._update_pill_attempts()
        self._last = res = self.engine.calculate(self._inputs())
        if not res.valid:
            for _, attr in self.RESULT_ROWS:
                getattr(self, attr).setText("—")
            self.o_error.setText(res.error)
            return
        self.o_error.setText(res.error)
        self.o_phase.setText(fmt_days(res.phase_days))
        self.o_stage.setText(fmt_days(res.stage_days))
        self.o_target.setText(fmt_days(res.target_days) if res.target_valid else "—")
        self.o_abode.setText(f"{res.abode_aura:,.1f}")
        self.o_basexp.setText(f"{res.base_xp_per_day:,.0f}")
        self.o_effxp.setText(f"{res.effective_xp_per_day:,.0f}")
        self.o_pillxp.setText(f"{res.pill_xp_per_day:,.0f}")
        self.o_speedup.setText(f"+{res.pill_speedup * 100:.1f}% / +{res.gem_speedup * 100:.0f}%")
        self.o_mythic.setText(f"{res.mythic_pills_per_day:.2f}")
        self.o_pearl.setText(f"{res.pearl_xp_per_day:,.0f}")
        self.o_fruit.setText(f"{res.fruit_xp:,.0f}")
        self.o_fruit_days.setText(fmt_days(res.fruit_days_saved))

    def _copy_results(self):
        rows = [
            ("Stage", self.stage.currentText()), ("Half-step", self.phase.currentText()),
            ("Grade", self.grade.currentText()),
            ("Half-step breakthrough in", self.o_phase.text()),
            ("Stage breakthrough in", self.o_stage.text()),
            ("Target Stage reached in", self.o_target.text()),
            ("Abode Aura (implied)", self.o_abode.text()),
            ("Cultivation XP / day", self.o_basexp.text()),
            ("Effective XP / day", self.o_effxp.text()),
            ("Pill XP / day", self.o_pillxp.text()),
            ("Mythic pills / day", self.o_mythic.text()),
            ("XP from fruits", self.o_fruit.text()),
            ("Fruit time saved", self.o_fruit_days.text()),
        ]
        text = "\n".join(f"{k}: {v}" for k, v in rows)
        QApplication.clipboard().setText(text)
        self.copy_btn.setText("Copied ✓")


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
    win.show()
    win.raise_()
    win.activateWindow()
    sys.exit(app.exec())
