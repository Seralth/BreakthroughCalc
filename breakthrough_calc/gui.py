"""Qt GUI for the Breakthrough Calculator."""

from __future__ import annotations

import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox,
    QGridLayout, QHBoxLayout, QLabel, QMainWindow, QScrollArea, QSpinBox,
    QVBoxLayout, QWidget,
)

from .engine import Engine, Inputs, fmt_days

STARS = ["0*", "1*", "2*", "3*", "4*", "5*"]


def settings_path() -> str:
    """Prefer a JSON next to the AppImage (portable/self-contained); fall back
    to ~/.config if that directory isn't writable."""
    appimage = os.environ.get("APPIMAGE")
    if appimage:
        candidate = os.path.join(os.path.dirname(appimage),
                                 os.path.basename(appimage) + ".settings.json")
        if os.access(os.path.dirname(appimage), os.W_OK):
            return candidate
    base = os.path.join(os.path.expanduser("~"), ".config", "breakthrough-calc")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "settings.json")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Donk's Breakthrough Calculator")
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
        outer = QHBoxLayout(central)

        # left column: inputs (scrollable)
        left = QWidget()
        lv = QVBoxLayout(left)

        cult = QGroupBox("Cultivation")
        f = QFormLayout(cult)
        self.stage = QComboBox(); self.stage.addItems(self.engine.stages())
        self.phase = QComboBox()
        self.grade = QComboBox()
        self.completion = QDoubleSpinBox(); self.completion.setRange(0, 100); self.completion.setSuffix(" %")
        self.speed = QDoubleSpinBox(); self.speed.setRange(0, 1e12); self.speed.setDecimals(2)
        self.absorb = QDoubleSpinBox(); self.absorb.setRange(0, 10000); self.absorb.setDecimals(3); self.absorb.setSuffix(" %")
        self.gem = QComboBox(); self.gem.addItems(list(self.engine.data["gem_bonus"].keys()))
        self.target = QComboBox(); self.target.addItem(""); self.target.addItems(self.engine.stages())
        f.addRow("Current stage", self.stage)
        f.addRow("Phase", self.phase)
        f.addRow("Grade", self.grade)
        f.addRow("Grade completion", self.completion)
        f.addRow("Cultivation speed (XP / 8s)", self.speed)
        f.addRow("Absorption ratio", self.absorb)
        f.addRow("Aura gem", self.gem)
        f.addRow("Future stage (timer)", self.target)
        lv.addWidget(cult)

        pills = QGroupBox("Pills")
        f = QFormLayout(pills)
        self.pill_rank = QComboBox(); self.pill_rank.addItems(list(self.engine.data["pill_xp"].keys()))
        self.pill_plus = QDoubleSpinBox(); self.pill_plus.setRange(0, 1000); self.pill_plus.setDecimals(2); self.pill_plus.setSuffix(" %")
        self.pill_limit = QDoubleSpinBox(); self.pill_limit.setRange(0, 1e6)
        self.gold_day = QDoubleSpinBox(); self.gold_day.setRange(0, 1e6)
        self.purple_day = QDoubleSpinBox(); self.purple_day.setRange(0, 1e6)
        self.blue_day = QDoubleSpinBox(); self.blue_day.setRange(0, 1e6)
        f.addRow("Pill rank", self.pill_rank)
        f.addRow("Cultivation pill effect", self.pill_plus)
        f.addRow("Pill limit / day", self.pill_limit)
        f.addRow("Gold used / day", self.gold_day)
        f.addRow("Purple used / day", self.purple_day)
        f.addRow("Blue used / day", self.blue_day)
        marks = QHBoxLayout()
        self.mark_blue = QDoubleSpinBox(); self.mark_purple = QDoubleSpinBox(); self.mark_gold = QDoubleSpinBox()
        for w, name in ((self.mark_blue, "Blue"), (self.mark_purple, "Purple"), (self.mark_gold, "Gold")):
            w.setRange(0, 10); w.setSingleStep(0.01); w.setDecimals(2)
            marks.addWidget(QLabel(name)); marks.addWidget(w)
        f.addRow("Star marks (+XP ratio)", marks)
        lv.addWidget(pills)

        arts = QGroupBox("Creation artifacts")
        g = QGridLayout(arts)
        g.addWidget(QLabel("<b>Artifact</b>"), 0, 0); g.addWidget(QLabel("<b>Star</b>"), 0, 2); g.addWidget(QLabel("<b>Skin</b>"), 0, 3)
        self.vase = QCheckBox("Vase"); self.vase_star = QComboBox(); self.vase_star.addItems(STARS); self.vase_skin = QCheckBox()
        self.mirror = QCheckBox("Mirror"); self.mirror_star = QComboBox(); self.mirror_star.addItems(STARS); self.mirror_skin = QCheckBox()
        self.pearl = QCheckBox("Pearl"); self.pearl_star = QComboBox(); self.pearl_star.addItems(STARS)
        self.pearl_xp10 = QDoubleSpinBox(); self.pearl_xp10.setRange(0, 1e12)
        g.addWidget(self.vase, 1, 0); g.addWidget(self.vase_star, 1, 2); g.addWidget(self.vase_skin, 1, 3)
        g.addWidget(self.mirror, 2, 0); g.addWidget(self.mirror_star, 2, 2); g.addWidget(self.mirror_skin, 2, 3)
        g.addWidget(self.pearl, 3, 0); g.addWidget(self.pearl_star, 3, 2)
        g.addWidget(QLabel("EXP per 10 energy"), 4, 0); g.addWidget(self.pearl_xp10, 4, 2, 1, 2)
        lv.addWidget(arts)

        fruit = QGroupBox("Fruit magic")
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
        f.addRow("Number of fruits", self.fruit_count)
        f.addRow("Culti level", self.lvl_culti)
        f.addRow("Quality level", self.lvl_quality)
        f.addRow("Gush level", self.lvl_gush)
        f.addRow("Extractor rarity", self.extractor)
        lv.addWidget(fruit)
        lv.addStretch(1)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(left)
        scroll.setMinimumWidth(430)
        outer.addWidget(scroll, 1)

        # right column: results
        right = QGroupBox("Results")
        rf = QFormLayout(right)
        def out() -> QLabel:
            lbl = QLabel("—"); lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            lbl.setStyleSheet("font-weight: bold;")
            return lbl
        self.o_phase = out(); self.o_stage = out(); self.o_target = out()
        self.o_abode = out(); self.o_pillxp = out(); self.o_speedup = out()
        self.o_mythic = out(); self.o_pearl = out(); self.o_fruit = out(); self.o_fruit_days = out()
        self.o_error = QLabel(""); self.o_error.setStyleSheet("color: #c04040;"); self.o_error.setWordWrap(True)
        rf.addRow("Time until phase done", self.o_phase)
        rf.addRow("Time until stage done", self.o_stage)
        rf.addRow("Time until future stage", self.o_target)
        rf.addRow("Implied abode aura", self.o_abode)
        rf.addRow("Pill XP / day", self.o_pillxp)
        rf.addRow("Speed-up (pills / gem)", self.o_speedup)
        rf.addRow("Mythic pills / day", self.o_mythic)
        rf.addRow("Pearl XP / day", self.o_pearl)
        rf.addRow("XP from fruits", self.o_fruit)
        rf.addRow("Fruit time saved", self.o_fruit_days)
        rf.addRow(self.o_error)
        outer.addWidget(right, 1)

        self.setCentralWidget(central)
        self.resize(940, 640)

    # ---- signal wiring ---------------------------------------------------
    def _wire(self):
        self.stage.currentTextChanged.connect(self._on_stage_changed)
        self.phase.currentTextChanged.connect(self._on_phase_changed)
        for w in (self.grade, self.gem, self.target, self.pill_rank, self.vase_star,
                  self.mirror_star, self.pearl_star, self.fruit_rank, self.extractor):
            w.currentTextChanged.connect(self.recalc)
        for w in (self.completion, self.speed, self.absorb, self.pill_plus, self.pill_limit,
                  self.gold_day, self.purple_day, self.blue_day, self.mark_blue,
                  self.mark_purple, self.mark_gold, self.pearl_xp10, self.fruit_count):
            w.valueChanged.connect(self.recalc)
        for w in (self.lvl_culti, self.lvl_quality, self.lvl_gush):
            w.valueChanged.connect(self.recalc)
        for w in (self.vase, self.vase_skin, self.mirror, self.mirror_skin, self.pearl, self.fruit_high):
            w.toggled.connect(self.recalc)

    def _on_stage_changed(self):
        stage = self.stage.currentText()
        self.phase.blockSignals(True)
        self.phase.clear()
        self.phase.addItems(self.engine.phases_for(stage))
        self.phase.blockSignals(False)
        self._on_phase_changed()

    def _on_phase_changed(self):
        stage, phase = self.stage.currentText(), self.phase.currentText()
        self.grade.blockSignals(True)
        self.grade.clear()
        self.grade.addItems(self.engine.grades_for(stage, phase))
        self.grade.blockSignals(False)
        self.recalc()

    # ---- calc ------------------------------------------------------------
    def _inputs(self) -> Inputs:
        return Inputs(
            stage=self.stage.currentText(), phase=self.phase.currentText(),
            grade=self.grade.currentText(), grade_completion=self.completion.value() / 100.0,
            culti_speed=self.speed.value(), absorption_ratio=self.absorb.value() / 100.0,
            aura_gem=self.gem.currentText(), target_stage=self.target.currentText(),
            pill_rank=self.pill_rank.currentText(), pill_effect=self.pill_plus.value() / 100.0,
            pill_limit=self.pill_limit.value(), gold_per_day=self.gold_day.value(),
            purple_per_day=self.purple_day.value(), blue_per_day=self.blue_day.value(),
            mark_blue=self.mark_blue.value(), mark_purple=self.mark_purple.value(),
            mark_gold=self.mark_gold.value(),
            vase=self.vase.isChecked(), vase_star=self.vase_star.currentText(),
            vase_skin=self.vase_skin.isChecked(),
            mirror=self.mirror.isChecked(), mirror_star=self.mirror_star.currentText(),
            mirror_skin=self.mirror_skin.isChecked(),
            pearl=self.pearl.isChecked(), pearl_star=self.pearl_star.currentText(),
            pearl_xp_per_10=self.pearl_xp10.value(),
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
            "gem": self.gem, "target": self.target,
            "pill_rank": self.pill_rank, "pill_effect_pct": self.pill_plus,
            "pill_limit": self.pill_limit, "gold_day": self.gold_day,
            "purple_day": self.purple_day, "blue_day": self.blue_day,
            "mark_blue": self.mark_blue, "mark_purple": self.mark_purple,
            "mark_gold": self.mark_gold,
            "vase": self.vase, "vase_star": self.vase_star, "vase_skin": self.vase_skin,
            "mirror": self.mirror, "mirror_star": self.mirror_star,
            "mirror_skin": self.mirror_skin,
            "pearl": self.pearl, "pearl_star": self.pearl_star,
            "pearl_xp10": self.pearl_xp10,
            "fruit_rank": self.fruit_rank, "fruit_high": self.fruit_high,
            "fruit_count": self.fruit_count, "lvl_culti": self.lvl_culti,
            "lvl_quality": self.lvl_quality, "lvl_gush": self.lvl_gush,
            "extractor": self.extractor,
        }

    def _save_settings(self):
        vals = {}
        for key, w in self._widget_map().items():
            if isinstance(w, QComboBox):
                vals[key] = w.currentText()
            elif isinstance(w, QCheckBox):
                vals[key] = w.isChecked()
            else:
                vals[key] = w.value()
        try:
            with open(self._settings_file, "w") as f:
                json.dump(vals, f, indent=1)
        except OSError:
            pass

    def _load_settings(self):
        try:
            with open(self._settings_file) as f:
                vals = json.load(f)
        except (OSError, ValueError):
            return
        wm = self._widget_map()
        # stage first so the phase/grade combos repopulate, then everything else
        for key in ["stage", "phase", "grade"] + [k for k in vals if k not in ("stage", "phase", "grade")]:
            w, v = wm.get(key), vals.get(key)
            if w is None or v is None:
                continue
            if isinstance(w, QComboBox):
                i = w.findText(str(v))
                if i >= 0:
                    w.setCurrentIndex(i)
            elif isinstance(w, QCheckBox):
                w.setChecked(bool(v))
            else:
                w.setValue(v)

    def closeEvent(self, event):
        self._save_settings()
        super().closeEvent(event)

    def recalc(self, *_):
        if not self._loading:
            self._save_settings()
        res = self.engine.calculate(self._inputs())
        if not res.valid:
            for o in (self.o_phase, self.o_stage, self.o_target, self.o_abode,
                      self.o_pillxp, self.o_speedup, self.o_mythic, self.o_pearl,
                      self.o_fruit, self.o_fruit_days):
                o.setText("—")
            self.o_error.setText(res.error)
            return
        self.o_error.setText(res.error)
        self.o_phase.setText(fmt_days(res.phase_days))
        self.o_stage.setText(fmt_days(res.stage_days))
        self.o_target.setText(fmt_days(res.target_days) if res.target_valid else "—")
        self.o_abode.setText(f"{res.abode_aura:,.1f}")
        self.o_pillxp.setText(f"{res.pill_xp_per_day:,.0f}")
        self.o_speedup.setText(f"+{res.pill_speedup * 100:.1f}% / +{res.gem_speedup * 100:.0f}%")
        self.o_mythic.setText(f"{res.mythic_pills_per_day:.2f}")
        self.o_pearl.setText(f"{res.pearl_xp_per_day:,.0f}")
        self.o_fruit.setText(f"{res.fruit_xp:,.0f}")
        self.o_fruit_days.setText(fmt_days(res.fruit_days_saved))


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
    sys.exit(app.exec())
