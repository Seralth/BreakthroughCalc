"""Qt GUI for the Breakthrough Calculator."""

from __future__ import annotations

import os
import re
import sys
import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QAbstractSpinBox, QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QGridLayout, QHBoxLayout,
    QInputDialog, QLabel,
    QMainWindow, QMessageBox, QPushButton, QScrollArea, QSpinBox, QTabWidget,
    QTextBrowser, QVBoxLayout,
    QWidget,
)

from . import __version__, theme, i18n
from .data_io import resource_path
from .doc_nav import DocController
from .docs import build_guide_pages, build_reference_pages
from .engine import (
    BASE_ENERGY, STRIVE_CAP_MORTAL, Engine, Inputs, fmt_days,
)
from .fields import FIELDS, FIELD_BY_KEY
from .i18n import tr, tr_duration
from .labels import (
    VASE_INPUT_LABELS, phase_disp, phase_key, stage_disp, stage_key,
    vase_input_disp,
)
from .pets import load_pets
from .advisor_ui import AdvisorPage
from .pets_ui import PetsPage
from .profiles import ProfileStore, settings_path
from .shelf import derive as shelf_derive, load_sources, migrate_legacy
from .shelf_ui import ProvenanceChip, ShelfPage
from .update_check import UpdateChecker
from .widgets import (
    DonateDialog, PillEffectRows, WheelGuard, clear_accents, link_enabled,
    restyle_all, style_accent,
)

STARS = ["0*", "1*", "2*", "3*", "4*", "5*"]

# Live-results / pinned-A rows: (row label, output-label attribute).
RESULT_ROWS = [
    ("Half-step breakthrough in", "o_phase"),
    ("Stage breakthrough in", "o_stage"),
    ("Target Stage reached in", "o_target"),
    ("Prestock for target (overcap)", "o_prestock"),
    ("At timegate", "o_gate"),
    ("Abode Aura (implied)", "o_abode"),
    ("Cultivation XP / day", "o_basexp"),
    ("Effective XP / day", "o_effxp"),
    ("Pill XP / day", "o_pillxp"),
    ("Daily XP share (daily flat XP / gem)", "o_speedup"),
    ("Mythic pills / day", "o_mythic"),
    ("Pearl XP / day", "o_pearl"),
    ("Respira XP / day", "o_respira"),
    ("Elixir XP / day", "o_elixir"),
    ("XP from fruits", "o_fruit"),
    ("Fruit time saved", "o_fruit_days"),
]


def _result_label() -> QLabel:
    lbl = QLabel("—"); lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
    fnt = lbl.font(); fnt.setBold(True); lbl.setFont(fnt)
    return lbl


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = Engine()
        self._store = ProfileStore(settings_path())
        self._loading = True
        # Non-widget UI state, initialized once: _respira_checked survives the
        # language-switch full rebuild. Doc-nav state lives in self._doc (a
        # DocController), recreated by _build_ui with the doc widgets it indexes.
        self._respira_checked = set()
        self._respira_exp_auto = None       # last self-filled Base EXP
        self._respira_attempts_auto = None  # last self-filled Attempts/day
        self._shelf_catalog = load_sources()
        self._shelf = {"owned": {}, "bases": {}, "auto": []}
        self._pets_catalog = load_pets()
        self._pets = {"owned": {}, "essences": {}}
        store = self._store.read()
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
        self._updates = UpdateChecker(self)
        self._updates.result.connect(self._on_update_result)
        self._updates.check()  # async; silent no-op offline
        # Delayed so it only ever fires in a running event loop (never in
        # the Qt smoke tests, which construct the window without exec()).
        QTimer.singleShot(1500, self._maybe_donation_nag)

    # ---- UI construction -------------------------------------------------
    def _build_ui(self):
        self.setWindowTitle(tr("Breakthrough Calculator"))
        clear_accents()  # full rebuild: drop stale accent-label registrations
        self._chips = {}
        central = QWidget()
        root = QVBoxLayout(central)
        root.addLayout(self._build_toolbar())
        outer = QHBoxLayout()
        root.addLayout(outer)

        # left column: inputs (scrollable)
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.addWidget(self._build_cultivation_group())
        lv.addWidget(self._build_pills_group())
        lv.addWidget(self._build_artifacts_group())
        lv.addWidget(self._build_respira_group())
        lv.addWidget(self._build_elixir_group())
        lv.addWidget(self._build_fruit_group())
        note = QLabel(tr(
            "Note: Strive (the catch-up bonus, from Nascent Soul) fades as you close the gap to "
            "your server's #1. Set \"Server #1's Stage\" above to model that drop-off (estimated); "
            "leave it blank to hold Strive constant. Low/zero-strive players are unaffected either way."))
        note.setWordWrap(True)
        style_accent(note, "muted", self._acc)
        # initial style also pins the font size; theme changes re-apply the
        # color only (mirrors the old _muted_labels restyle, which dropped it)
        note.setStyleSheet(f"color: {self._acc['muted']}; font-size: 11px;")
        lv.addWidget(note)
        lv.addStretch(1)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(left)
        scroll.setMinimumWidth(430)
        outer.addWidget(scroll, 1)

        # right column: live results + a pinnable "A" snapshot for A/B compare
        outer.addWidget(self._build_results_panel(), 1)
        outer.addWidget(self._build_pin_panel(), 1)

        tabs = QTabWidget()
        tabs.addTab(central, tr("Calculator"))
        tabs.addTab(self._build_shelf_tab(), tr("Vault"))
        self.advisor_page = AdvisorPage(
            self.engine, self._shelf_catalog, self._inputs,
            lambda: self._shelf)
        tabs.addTab(self.advisor_page, tr("Advisor"))
        tabs.addTab(self._build_pets_tab(), tr("Pets"))
        self._tabs = tabs
        # Doc-tree navigation (history, cross-links, back button) lives in the
        # DocController; a fresh one per _build_ui starts with an empty history
        # and re-registers the doc widgets built just below. Each tree's
        # top-level index is captured before its tab is inserted.
        self._doc = DocController(tabs)
        ref_idx = tabs.count()
        tabs.addTab(self._build_reference_tab(ref_idx), tr("Reference"))
        guide_idx = tabs.count()
        tabs.addTab(self._build_guide_tab(guide_idx), tr("Guide"))
        self.setCentralWidget(tabs)

    def _build_cultivation_group(self) -> QGroupBox:
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
        self.target_phase = QComboBox(); self.target_phase.addItem("")
        self.target_grade = QComboBox(); self.target_grade.addItem("")
        self.timegate = QDoubleSpinBox(); self.timegate.setRange(0, 1000); self.timegate.setDecimals(1); self.timegate.setSuffix(tr(" days"))
        f.addRow(tr("Stage"), self.stage)
        f.addRow(tr("Half-step"), self.phase)
        f.addRow(tr("Grade"), self.grade)
        f.addRow(tr("Grade progress"), self.completion)
        # Abode Aura, Absorption Ratio, and Cultivation Speed all come off the
        # same in-game Cultivation Bonus screen. Speed = Aura × Absorption is
        # kept in sync live (either direction), matching mobile; every field
        # stays directly editable.
        self.abode_aura = QDoubleSpinBox(); self.abode_aura.setRange(0, 1e9)
        self.abode_aura.setDecimals(2)
        f.addRow(tr("Abode Aura"), self.abode_aura)
        f.addRow(tr("Absorption Ratio"), self.absorb)
        self.absorb_base = QLabel("")
        style_accent(self.absorb_base, "muted", self._acc)
        f.addRow("", self.absorb_base)
        # Ascension Virya is cultivation progression (its tiers are gated on
        # your primary/secondary stages), so its selector lives here with the
        # rest of the character state; it drives the blessing fields below
        # through the same shelf derivation the Vault uses.
        self.virya = QComboBox()
        self.virya.addItem("—")
        for label in self._virya_labels():
            self.virya.addItem(label)
        self.virya.currentIndexChanged.connect(self._on_virya_changed)
        f.addRow("Ascension Virya", self.virya)  # official name, untranslated
        self.bless_pp = QDoubleSpinBox(); self.bless_pp.setRange(0, 1000)
        self.bless_pp.setDecimals(1); self.bless_pp.setSuffix(" %")
        self.bless_window = QDoubleSpinBox(); self.bless_window.setRange(0, 1000)
        self.bless_window.setDecimals(1); self.bless_window.setSuffix(" %")
        f.addRow(tr("Ascension blessing"),
                 self._with_chip(self.bless_pp, "bless_pp"))
        f.addRow(tr("Blessing before Voidbreak Middle"),
                 self._with_chip(self.bless_window, "bless_window"))
        self.array_out = QLabel("—"); self.array_out.setWordWrap(True)
        style_accent(self.array_out, "muted", self._acc)
        f.addRow("", self.array_out)
        f.addRow(tr("Cultivation Speed (XP / Cosmoapsis)"), self.speed)
        f.addRow(tr("Aura Gem"), self.gem)
        f.addRow(tr("Target Stage"), self.target)
        f.addRow(tr("Target half-step"), self.target_phase)
        f.addRow(tr("Target grade"), self.target_grade)
        f.addRow(tr("Timegate lifts in"), self.timegate)
        self.top_stage = QComboBox(); self.top_stage.addItem("")
        self.top_stage.addItems([stage_disp(s) for s in self.engine.stages()])
        f.addRow(tr("Server #1's Stage (Strive)"), self.top_stage)
        self.mature_server = QCheckBox(tr("Mature server (world level 30+)"))
        self.mature_server.setChecked(True)
        f.addRow("", self.mature_server)
        return cult

    def _build_pills_group(self) -> QGroupBox:
        pills = QGroupBox(tr("Cultivation Pills"))
        f = QFormLayout(pills)
        self.pill_rank = QComboBox(); self.pill_rank.addItems(list(self.engine.data["pill_xp"].keys()))
        self.pill_limit = QDoubleSpinBox(); self.pill_limit.setRange(0, 1e6)
        self.gold_day = QDoubleSpinBox(); self.gold_day.setRange(0, 1e6)
        self.purple_day = QDoubleSpinBox(); self.purple_day.setRange(0, 1e6)
        self.blue_day = QDoubleSpinBox(); self.blue_day.setRange(0, 1e6)
        f.addRow(tr("Pill rank"), self.pill_rank)

        # Cultivation pill effect = Vault-managed rows plus free-typed extras
        # for bonuses the catalog does not carry (event buffs, Daozu treasures).
        self.pe_rows = PillEffectRows(lambda: self._acc)
        self.pe_rows.changed.connect(self.recalc)
        f.addRow(tr("Cultivation pill effect"), self.pe_rows)

        f.addRow(tr("Daily pill attempts (shared)"),
                 self._with_chip(self.pill_limit, "pill_limit"))
        f.addRow(tr("Legendary (Gold) used / day"), self.gold_day)
        f.addRow(tr("Epic (Purple) used / day"), self.purple_day)
        f.addRow(tr("Rare (Blue) used / day"), self.blue_day)
        self.pill_attempts = QLabel("")
        style_accent(self.pill_attempts, "muted", self._acc)
        f.addRow("", self.pill_attempts)
        self.dailies_done = QCheckBox(tr("Already used today's pills/respira"))
        f.addRow("", self.dailies_done)
        self.reset_in = QDoubleSpinBox()
        self.reset_in.setRange(0, 24); self.reset_in.setValue(24); self.reset_in.setSingleStep(0.5)
        self.reset_in.setEnabled(self.dailies_done.isChecked())
        self.dailies_done.toggled.connect(self.reset_in.setEnabled)
        f.addRow(tr("Reset in (h)"), self.reset_in)
        marks = QHBoxLayout()
        self.mark_blue = QDoubleSpinBox(); self.mark_purple = QDoubleSpinBox(); self.mark_gold = QDoubleSpinBox()
        for w, name in ((self.mark_blue, "Rare"), (self.mark_purple, "Epic"), (self.mark_gold, "Legendary")):
            w.setRange(0, 10); w.setSingleStep(0.01); w.setDecimals(2)
            marks.addWidget(QLabel(tr(name))); marks.addWidget(w)
        f.addRow(tr("Star Marks (+XP ratio)"), marks)
        return pills

    def _build_artifacts_group(self) -> QGroupBox:
        arts = QGroupBox(tr("Creation Artifacts"))
        g = QGridLayout(arts)
        g.addWidget(QLabel(f"<b>{tr('Artifact')}</b>"), 0, 0); g.addWidget(QLabel(f"<b>{tr('Star')}</b>"), 0, 2); g.addWidget(QLabel(f"<b>{tr('Skin')}</b>"), 0, 3)
        g.addWidget(QLabel(f"<b>{tr('Charge')}</b>"), 0, 4)
        self.vase = QCheckBox(tr("Starsea Vase")); self.vase_star = QComboBox(); self.vase_star.addItems(STARS); self.vase_skin = QCheckBox()
        self.mirror = QCheckBox(tr("Dual-Star Mirror")); self.mirror_star = QComboBox(); self.mirror_star.addItems(STARS); self.mirror_skin = QCheckBox()
        self.pearl = QCheckBox(tr("Timereversal Pearl")); self.pearl_star = QComboBox(); self.pearl_star.addItems(STARS)
        self.pearl_skin = QCheckBox()
        self.pearl_xp10 = QDoubleSpinBox(); self.pearl_xp10.setRange(0, 1e12)
        self.vase_charge = QCheckBox(); self.mirror_charge = QCheckBox(); self.pearl_charge = QCheckBox()
        for w in (self.vase_charge, self.mirror_charge, self.pearl_charge):
            w.setChecked(True)
        g.addWidget(self.vase, 1, 0); g.addWidget(self.vase_star, 1, 2); g.addWidget(self.vase_skin, 1, 3)
        g.addWidget(self.vase_charge, 1, 4)
        g.addWidget(self.mirror, 2, 0); g.addWidget(self.mirror_star, 2, 2); g.addWidget(self.mirror_skin, 2, 3)
        g.addWidget(self.mirror_charge, 2, 4)
        g.addWidget(self.pearl, 3, 0); g.addWidget(self.pearl_star, 3, 2); g.addWidget(self.pearl_skin, 3, 3)
        g.addWidget(self.pearl_charge, 3, 4)
        self.vase_input_label = QLabel(tr("Vase input pill"))
        self.vase_input = QComboBox()
        self.vase_input.addItems([vase_input_disp(k) for k in VASE_INPUT_LABELS])
        g.addWidget(self.vase_input_label, 4, 0); g.addWidget(self.vase_input, 4, 2, 1, 2)
        self.pearl_xp10_label = QLabel(tr("EXP per 10 energy"))
        g.addWidget(self.pearl_xp10_label, 5, 0); g.addWidget(self.pearl_xp10, 5, 2, 1, 2)
        # Grey out each artifact's controls while it is unchecked, so it is
        # obvious the inputs only count once the artifact is enabled.
        link_enabled(self.vase, self.vase_star, self.vase_skin, self.vase_charge,
                     self.vase_input, self.vase_input_label)
        link_enabled(self.mirror, self.mirror_star, self.mirror_skin, self.mirror_charge)
        link_enabled(self.pearl, self.pearl_star, self.pearl_skin, self.pearl_charge,
                     self.pearl_xp10, self.pearl_xp10_label)
        return arts

    def _build_respira_group(self) -> QGroupBox:
        respira = QGroupBox(tr("Respira"))
        rf = QFormLayout(respira)
        self.respira_per_day = QDoubleSpinBox(); self.respira_per_day.setRange(0, 1e5)
        self.respira_event = QDoubleSpinBox(); self.respira_event.setRange(0, 1e5)
        self.respira_exp = QDoubleSpinBox(); self.respira_exp.setRange(0, 1e12)
        rf.addRow(tr("Attempts / day"),
                  self._with_chip(self.respira_per_day, "respira_per_day"))
        rf.addRow(tr("Extra attempts today"), self.respira_event)
        rf.addRow(tr("Base EXP / attempt"), self.respira_exp)
        respira_hint = QLabel(tr(
            "Attempts and Base EXP fill themselves — attempts from the "
            "game's base 10 plus your Vault bonuses, Base EXP from your "
            "Stage estimate times your Vault's book bonuses. Overwrite "
            "either with your in-game reading (clear a field to go back to "
            "the estimate). Most Respira give the same small EXP — that is "
            "the base; 2×/5×/10× crits are handled automatically."))
        respira_hint.setWordWrap(True)
        style_accent(respira_hint, "muted", self._acc)
        rf.addRow("", respira_hint)
        return respira

    def _build_elixir_group(self) -> QGroupBox:
        elixirs = QGroupBox(tr("Elixirs"))
        ef = QFormLayout(elixirs)
        self.elixir_per_day = QDoubleSpinBox(); self.elixir_per_day.setRange(0, 1e5)
        self.elixir_exp = QDoubleSpinBox(); self.elixir_exp.setRange(0, 1e12)
        self.elixir_exp.setDecimals(2)
        self.elixir_effect = QDoubleSpinBox(); self.elixir_effect.setRange(0, 1000)
        self.elixir_effect.setDecimals(1); self.elixir_effect.setSuffix(" %")
        self.elixir_effect.setValue(100)
        ef.addRow(tr("XP elixirs / day"), self.elixir_per_day)
        ef.addRow(tr("EXP per elixir"), self.elixir_exp)
        ef.addRow(tr("Elixir effectiveness"), self.elixir_effect)
        return elixirs

    def _build_fruit_group(self) -> QGroupBox:
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
        return fruit

    def _build_results_panel(self) -> QGroupBox:
        right = QGroupBox(tr("Results (current)"))
        rf = QFormLayout(right)
        for text, attr in RESULT_ROWS:
            lbl = _result_label(); setattr(self, attr, lbl); rf.addRow(tr(text), lbl)
        self.o_error = QLabel(""); style_accent(self.o_error, "bad", self._acc); self.o_error.setWordWrap(True)
        rf.addRow(self.o_error)
        btns = QHBoxLayout()
        self.copy_btn = QPushButton(tr("Copy results")); self.copy_btn.clicked.connect(self._copy_results)
        self.pin_btn = QPushButton(tr("Pin as A")); self.pin_btn.clicked.connect(self._pin_results)
        btns.addWidget(self.copy_btn); btns.addWidget(self.pin_btn)
        rf.addRow(btns)
        return right

    def _build_pin_panel(self) -> QGroupBox:
        self.pin_box = QGroupBox(tr("Pinned A"))
        pf = QFormLayout(self.pin_box)
        self.pin_labels = {}
        for text, attr in RESULT_ROWS:
            lbl = _result_label(); style_accent(lbl, "good", self._acc, "font-weight: bold; color: {};"); self.pin_labels[attr] = lbl
            pf.addRow(tr(text), lbl)
        self.unpin_btn = QPushButton(tr("Clear A")); self.unpin_btn.clicked.connect(self._unpin_results)
        pf.addRow(self.unpin_btn)
        self.pin_box.setVisible(False)
        return self.pin_box

    # ---- doc trees (navigation state/logic lives in DocController) --------
    def _rebuild_doc_tabs(self):
        # Rebuild the Reference and Guide tabs (all sub-tab browsers) so accent
        # colors baked into the HTML follow theme changes; keep the sub-tabs.
        sub = self._doc.sub_index("ref")
        gsub = self._doc.sub_index("guide")
        ref_idx = self._doc.tab_index["ref"]
        guide_idx = self._doc.tab_index["guide"]
        self._tabs.removeTab(guide_idx)
        self._tabs.removeTab(ref_idx)
        self._tabs.insertTab(ref_idx, self._build_reference_tab(ref_idx), tr("Reference"))
        self._tabs.insertTab(guide_idx, self._build_guide_tab(guide_idx), tr("Guide"))
        self._doc.set_sub_index("ref", sub)
        self._doc.set_sub_index("guide", gsub)
        self._doc.update_back_buttons()
        self.resize(1180, 680)  # note: re-triggers on every theme change

    def _build_doc_tab(self, pages) -> QTabWidget:
        """Wrap ordered (slug, title, html) pages in QTextBrowser sub-tabs
        with the app:// link wiring and a Back corner button."""
        tabs = QTabWidget()
        for _slug, title, html in pages:
            b = QTextBrowser()
            b.setOpenLinks(False)
            b.anchorClicked.connect(self._doc.open_link)
            b.setHtml(html)
            # Escape & so QTabWidget doesn't eat it as a mnemonic marker
            tabs.addTab(b, title.replace("&", "&&"))
        back = QPushButton(tr("← Back"))
        back.clicked.connect(self._doc.go_back)
        back.setVisible(False)
        tabs.setCornerWidget(back)
        return tabs

    def _build_reference_tab(self, top_index: int) -> QWidget:
        pages = build_reference_pages(self._acc, self.engine.data,
                                      self._shelf_catalog)
        slugs = {slug: i for i, (slug, _, _) in enumerate(pages)}
        tabs = self._build_doc_tab(pages)
        self._doc.register_tree("ref", top_index, tabs, slugs)
        return tabs

    def _build_guide_tab(self, top_index: int) -> QWidget:
        pages = build_guide_pages(self._acc)
        slugs = {slug: i for i, (slug, _, _) in enumerate(pages)}
        tabs = self._build_doc_tab(pages)
        self._doc.register_tree("guide", top_index, tabs, slugs)
        return tabs

    # ---- signal wiring ---------------------------------------------------
    def _wire(self):
        # Registry-driven: every field re-runs recalc on change, except the
        # nav combos whose specs name a repopulation handler (which recalcs).
        for spec in FIELDS:
            w = getattr(self, spec.widget_attr)
            handler = getattr(self, spec.on_change) if spec.on_change else self.recalc
            if spec.kind == "combo":
                w.currentTextChanged.connect(handler)
            elif spec.kind == "check":
                w.toggled.connect(handler)
            else:
                w.valueChanged.connect(handler)
        # Live speed sync (mirrors mobile): editing Aura or Absorption
        # recomputes Speed; editing Speed back-solves Aura. The guard stops
        # the two handlers from ping-ponging.
        self._syncing_speed = False
        self.abode_aura.valueChanged.connect(self._sync_speed_from_parts)
        self.absorb.valueChanged.connect(self._sync_speed_from_parts)
        self.speed.valueChanged.connect(self._sync_aura_from_speed)
        self._install_wheel_guard()
        self._install_tooltips()
        hints = QGuiApplication.styleHints()
        if hasattr(hints, "colorSchemeChanged"):  # Qt >= 6.5
            hints.colorSchemeChanged.connect(self._on_color_scheme_changed)

    def _install_wheel_guard(self):
        self._wheel_guard = WheelGuard(self)
        for cls in (QAbstractSpinBox, QComboBox):
            for w in self.findChildren(cls):
                w.setFocusPolicy(Qt.StrongFocus)
                w.installEventFilter(self._wheel_guard)

    def _install_tooltips(self):
        # Input-field tooltips live in the field registry; output labels are
        # not registry fields, so their tooltips stay here.
        for spec in FIELDS:
            if spec.tooltip:
                getattr(self, spec.widget_attr).setToolTip(tr(spec.tooltip))
        tips = {
            self.o_prestock: "Overcap needed for the target, in the game's own display convention (XP since the "
                             "start of the final half-step ÷ that half-step's total), and the time to stock it. "
                             "While timegated you stay parked at the Stage cap, so XP accrues at your CURRENT "
                             "speed — no future-grade speedups. Slower than the ungated 'Target reached in'.",
            self.o_gate: "Whether your stocked XP reaches the target before the timegate lifts.",
        }
        for w, t in tips.items():
            w.setToolTip(tr(t))

    def _on_stage_changed(self):
        stage = stage_key(self.stage.currentText())
        self.phase.blockSignals(True)
        self.phase.clear()
        self.phase.addItems([phase_disp(p) for p in self.engine.phases_for(stage)])
        self.phase.blockSignals(False)
        # Target dropdown: current Stage (for later half-steps/grades) onward.
        stages = self.engine.stages()
        future = stages[stages.index(stage):] if stage in stages else []
        prev = self.target.currentText()
        self.target.blockSignals(True)
        self.target.clear()
        self.target.addItem("")
        self.target.addItems([stage_disp(s) for s in future])
        i = self.target.findText(prev)
        self.target.setCurrentIndex(i if i >= 0 else 0)
        self.target.blockSignals(False)
        if i < 0:
            self._on_target_stage_changed()
        self._on_phase_changed()

    def _on_target_stage_changed(self):
        # Repopulate the optional half-step (and grade) combos; blank means
        # "start of the stage / half-step".
        tstage = stage_key(self.target.currentText())
        prev = self.target_phase.currentText()
        self.target_phase.blockSignals(True)
        self.target_phase.clear()
        self.target_phase.addItem("")
        if tstage:
            self.target_phase.addItems([phase_disp(p) for p in self.engine.phases_for(tstage)])
        i = self.target_phase.findText(prev)
        self.target_phase.setCurrentIndex(i if i >= 0 else 0)
        self.target_phase.blockSignals(False)
        self._on_target_phase_changed()

    def _on_target_phase_changed(self):
        tstage = stage_key(self.target.currentText())
        tphase = phase_key(self.target_phase.currentText())
        prev = self.target_grade.currentText()
        self.target_grade.blockSignals(True)
        self.target_grade.clear()
        self.target_grade.addItem("")
        if tstage and tphase:
            self.target_grade.addItems(self.engine.grades_for(tstage, tphase))
        i = self.target_grade.findText(prev)
        self.target_grade.setCurrentIndex(i if i >= 0 else 0)
        self.target_grade.blockSignals(False)
        self.recalc()

    def _on_phase_changed(self):
        stage, phase = stage_key(self.stage.currentText()), phase_key(self.phase.currentText())
        self.grade.blockSignals(True)
        self.grade.clear()
        self.grade.addItems(self.engine.grades_for(stage, phase))
        self.grade.blockSignals(False)
        self.recalc()

    # ---- calc ------------------------------------------------------------
    def _inputs(self) -> Inputs:
        # Registry-driven: every FieldSpec with an inputs_attr feeds the
        # engine (combo converters and percent scaling from the spec);
        # pill_effect is the one non-registry input (sum of the source rows).
        kw = {}
        for spec in FIELDS:
            if spec.inputs_attr is None:
                continue
            w = getattr(self, spec.widget_attr)
            if spec.kind == "combo":
                v = spec.to_key(w.currentText()) if spec.to_key else w.currentText()
            elif spec.kind == "check":
                v = w.isChecked()
            else:
                v = w.value()
                if spec.scale:
                    v = v / spec.scale
            kw[spec.inputs_attr] = v
        kw["pill_effect"] = self.pe_rows.total() / 100.0
        return Inputs(**kw)

    # ---- persistence -----------------------------------------------------
    # Combo values are persisted as INTERNAL keys (language-independent);
    # each FieldSpec's to_key/to_disp convert display text <-> internal key.
    def _widget_map(self) -> dict:
        return {spec.key: getattr(self, spec.widget_attr) for spec in FIELDS}

    def _collect_state(self) -> dict:
        vals = {}
        for spec in FIELDS:
            w = getattr(self, spec.widget_attr)
            if spec.kind == "combo":
                vals[spec.key] = spec.to_key(w.currentText()) if spec.to_key else w.currentText()
            elif spec.kind == "check":
                vals[spec.key] = w.isChecked()
            else:
                vals[spec.key] = w.value()
        vals["pill_sources"] = self.pe_rows.sources()
        vals["respira_sources"] = sorted(self._respira_checked)
        vals["shelf"] = {"owned": dict(self._shelf.get("owned", {})),
                         "bases": dict(self._shelf.get("bases", {})),
                         "auto": list(self._shelf.get("auto", []))}
        vals["pets"] = {"owned": dict(self._pets.get("owned", {})),
                        "essences": dict(self._pets.get("essences", {}))}
        return vals

    def _apply_state(self, vals: dict):
        prev, self._loading = self._loading, True
        # Read the shelf BEFORE the defaults merge below injects the (empty)
        # construction default — a missing key here means a legacy profile
        # that needs the one-time migration.
        shelf_state = vals.get("shelf")
        # pill-effect sources (migrate old single "pill_effect_pct" to one row)
        srcs = vals.get("pill_sources")
        if srcs is None and "pill_effect_pct" in vals:
            srcs = [["", vals["pill_effect_pct"]]]
        self.pe_rows.set_sources(srcs if srcs is not None else [])
        # checked respira catalog sources; the attempts value itself is stored
        # in respira_per_day, so only the checkmarks need restoring
        rs = vals.get("respira_sources")
        self._respira_checked = set(rs) if rs else set()
        # fill in construction defaults for any keys the profile doesn't set,
        # so switching profiles never carries over the previous profile's values
        vals = {**self._defaults, **{k: v for k, v in vals.items() if v is not None}}
        # stage first so the phase/grade combos repopulate, then everything else
        for key in ["stage", "phase", "grade"] + [k for k in vals if k not in ("stage", "phase", "grade")]:
            spec, v = FIELD_BY_KEY.get(key), vals.get(key)
            if spec is None or v is None:
                continue
            w = getattr(self, spec.widget_attr)
            if spec.to_disp is not None:
                # accept internal keys (current format) and legacy display
                # names saved in any language (convert to key, then display)
                v = spec.to_disp(spec.to_key(str(v)))
            try:
                if spec.kind == "combo":
                    i = w.findText(str(v))
                    if i >= 0:
                        w.setCurrentIndex(i)
                elif spec.kind == "check":
                    w.setChecked(bool(v))
                else:
                    w.setValue(v)
            except (TypeError, ValueError):
                pass  # tolerate hand-edited settings with wrong value types
        sh = shelf_state
        if sh is not None:
            self._shelf = {"owned": dict(sh.get("owned", {})),
                           "bases": dict(sh.get("bases", {})),
                           "auto": list(sh.get("auto", []))}
        else:
            # One-time migration: fold the old catalogs' checked entries into
            # shelf ownership. Matched pill-effect rows become read-only auto
            # rows (same values, so the total is unchanged); attempt sources
            # rebase into "base + shelf" with identical field values.
            owned, _custom, _notes = migrate_legacy(
                self.pe_rows.sources(), sorted(self._respira_checked),
                self._shelf_catalog)
            migrated_pe = {a["name"]
                           for src in self._shelf_catalog.get("sources", [])
                           for a in src.get("legacy", [])
                           if a["catalog"] == "pe" and not a.get("parametric")
                           and src["id"] in owned}
            if migrated_pe:
                self.pe_rows.set_sources(
                    [[l, v] for l, v in self.pe_rows.sources()
                     if l not in migrated_pe])
            self._shelf = {"owned": owned, "bases": {}, "auto": []}
            d = shelf_derive(self._shelf_catalog, self._shelf)
            ra = d.get("respira_attempts")
            pa = d.get("pill_attempts")
            # An empty attempts field means "never entered", not "base 0" —
            # the game grants 10 Respira/day by default.
            entered = self.respira_per_day.value()
            self._shelf["bases"] = {
                "respira_attempts": (max(0.0, entered - (ra.total if ra else 0.0))
                                     if entered > 0 else 10.0),
                "pill_attempts": max(0.0, self.pill_limit.value()
                                     - (pa.total if pa else 0.0)),
            }
            if owned:
                self._shelf["auto"] = ["pill_limit", "respira_per_day"]
        self.shelf_page.set_state(self._shelf.get("owned", {}),
                                  self._shelf.get("bases", {}))
        pt = vals.get("pets") or {}
        self._pets = {"owned": dict(pt.get("owned", {})),
                      "essences": dict(pt.get("essences", {}))}
        self.pets_page.set_state(self._pets)
        self._sync_virya_combo()
        self._apply_shelf(recalc=False)
        self._loading = prev

    # ---- profiles (widget<->state bridge over profiles.ProfileStore) ------
    def _save_settings(self):
        # save into whatever the file says is current (no first-profile
        # fallback here — mirrors the store's historical write path)
        cur = self._store.read().get("current", "Default")
        self._store.set(cur, self._collect_state())

    def _load_settings(self):
        cur = self._store.current
        self._apply_state(self._store.get(cur))
        self._refresh_profile_combo(cur)

    def _refresh_profile_combo(self, current: str):
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for name in self._store.names():
            self.profile_combo.addItem(name)
        i = self.profile_combo.findText(current)
        if i >= 0:
            self.profile_combo.setCurrentIndex(i)
        self.profile_combo.blockSignals(False)

    def _switch_profile(self, name: str):
        if self._loading or not name:
            return
        self._store.current = name
        self._apply_state(self._store.get(name))
        self.recalc()

    def _new_profile(self):
        name, ok = QInputDialog.getText(self, tr("New / Save As"), tr("Profile name:"))
        name = (name or "").strip()
        if not ok or not name:
            return
        self._store.set(name, self._collect_state())
        self._refresh_profile_combo(name)

    def _delete_profile(self):
        newcur = self._store.delete(self._store.read().get("current"))
        if newcur is None:
            return  # always keep at least one profile
        self._apply_state(self._store.get(newcur))
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
        b.clicked.connect(lambda: self._updates.check(manual=True))
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
        obj = self._store.read(); obj["lang"] = code; self._store.write(obj)
        self._build_ui()
        self._wire()
        self._on_stage_changed()
        self._refresh_profile_combo(self._store.read().get("current", "Default"))
        self._apply_state(state)
        self._loading = prev
        self.recalc()

    # ---- donate ------------------------------------------------------------
    def _show_donate(self):
        DonateDialog(self).exec()

    def _maybe_donation_nag(self):
        # One reminder after 10 launches; "Maybe later" (or closing the
        # dialog) re-asks in 60 days, Donate / "Don't ask again" never
        # again. Twin of maybeShowDonationNag in mobile update_banner.dart.
        obj = self._store.read()
        if obj.get("donate_nag") == "never":
            return
        launches = int(obj.get("launch_count", 0)) + 1
        obj["launch_count"] = launches
        now = int(time.time())
        due_ok = (obj.get("donate_nag") != "later"
                  or now >= int(obj.get("donate_nag_due", 0)))
        show = launches >= 10 and due_ok
        if show:
            obj["donate_nag"] = "later"
            obj["donate_nag_due"] = now + 60 * 86400
        self._store.write(obj)
        if not show:
            return
        box = QMessageBox(self)
        box.setWindowTitle(tr("Enjoying the calculator?"))
        box.setText(tr(
            "This app is free and always will be. If it has been useful, "
            "you can support development with a donation — sent as an "
            "in-game voucher gift."))
        donate = box.addButton(tr("Donate"), QMessageBox.AcceptRole)
        box.addButton(tr("Maybe later"), QMessageBox.RejectRole)
        never = box.addButton(
            tr("Don't ask again"), QMessageBox.DestructiveRole)
        box.exec()
        if box.clickedButton() in (donate, never):
            obj = self._store.read()
            obj["donate_nag"] = "never"
            self._store.write(obj)
            if box.clickedButton() is donate:
                self._show_donate()

    # ---- update check (logic in update_check.UpdateChecker) ---------------
    def _on_update_result(self, text: str, visible: bool):
        self.update_label.setText(text)
        self.update_label.setVisible(visible)

    def _on_theme_changed(self, name: str):
        self._theme = name
        self._acc = theme.accents(name)
        theme.apply(QApplication.instance(), name)
        restyle_all(self._acc)
        self._rebuild_doc_tabs()
        self.recalc()
        obj = self._store.read(); obj["theme"] = name; self._store.write(obj)

    def _on_color_scheme_changed(self, *_):
        # Re-apply only when tracking the OS scheme; explicit themes are static.
        if self._theme == "System":
            self._on_theme_changed("System")

    # ---- A/B compare -----------------------------------------------------
    def _pin_results(self):
        for _, attr in RESULT_ROWS:
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
        if self.engine.base_energy_known(stage_key(self.stage.currentText())):
            bonus = abode / BASE_ENERGY - 1
        absorb = self.absorb.value() / 100.0
        spd = abode * absorb if absorb > 0 else None
        return abode, bonus, spd

    def _update_pill_attempts(self):
        self.pe_rows.update_total()
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
        if r is None or r[1] is None:
            self.array_out.setVisible(False)
            return
        self.array_out.setVisible(True)
        bonus = r[1]
        self.array_out.setText(
            tr("Implied total aura bonus: {}%  (Abode = 130 × {})").format(
                f"{bonus * 100:.1f}", f"{1 + bonus:.3f}"))

    def _sync_speed_from_parts(self, *_):
        if self._loading or self._syncing_speed:
            return
        aura, absorb = self.abode_aura.value(), self.absorb.value() / 100.0
        if aura > 0 and absorb > 0:
            self._syncing_speed = True
            try:
                self.speed.setValue(aura * absorb)
            finally:
                self._syncing_speed = False

    def _sync_aura_from_speed(self, *_):
        if self._loading or self._syncing_speed:
            return
        absorb = self.absorb.value() / 100.0
        if absorb > 0:
            self._syncing_speed = True
            try:
                self.abode_aura.setValue(self.speed.value() / absorb)
            finally:
                self._syncing_speed = False

    def closeEvent(self, event):
        self._save_settings()
        super().closeEvent(event)

    def _auto_respira_exp(self):
        """Keep the Respira fields prefilled while the user has not
        overridden them: Attempts = game base + Vault bonuses, Base EXP =
        Stage estimate × (1 + the Vault's Respira Effect books %). Both
        fill when empty and refresh after stage/Vault changes while still
        holding the previous estimate; a manual entry sticks; clearing a
        field returns to the estimate."""
        derived = shelf_derive(self._shelf_catalog, self._shelf)
        if "respira_per_day" not in set(self._shelf.get("auto", [])):
            att = derived.get("respira_attempts")
            base_att = float(self._shelf.get("bases", {})
                             .get("respira_attempts", 10.0))
            est_att = base_att + (att.total if att else 0.0)
            cur = self.respira_per_day.value()
            if cur == 0 or cur == self._respira_attempts_auto or cur == est_att:
                self.respira_per_day.blockSignals(True)
                self.respira_per_day.setValue(est_att)
                self.respira_per_day.blockSignals(False)
                self._respira_attempts_auto = est_att
        stage = stage_key(self.stage.currentText())
        base = self.engine.respira_base_estimate(stage)
        if base is None:
            return
        eff = derived.get("respira_effect")
        books = eff.total if eff else 0.0
        est = float(round(base * (1 + books / 100.0)))
        cur = self.respira_exp.value()
        if cur == 0 or cur == self._respira_exp_auto or cur == est:
            self.respira_exp.blockSignals(True)
            self.respira_exp.setValue(est)
            self.respira_exp.blockSignals(False)
            self._respira_exp_auto = est

    # ---- Sources Shelf -----------------------------------------------------
    def _build_shelf_tab(self) -> QWidget:
        self.shelf_page = ShelfPage(self._shelf_catalog)
        self.shelf_page.set_state(self._shelf.get("owned", {}),
                                  self._shelf.get("bases", {}))
        self.shelf_page.changed.connect(self._on_shelf_changed)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setWidget(self.shelf_page)
        return scroll  # Library scrolls itself; outer scroll covers the rest

    # ---- Pets ---------------------------------------------------------------
    def _build_pets_tab(self) -> QWidget:
        self.pets_page = PetsPage(self._pets_catalog)
        self.pets_page.set_state(self._pets)
        self.pets_page.changed.connect(self._on_pets_changed)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setWidget(self.pets_page)
        return scroll

    def _on_pets_changed(self, *_):
        self._pets = self.pets_page.state()

    def _shelf_chip(self, field_key: str) -> ProvenanceChip:
        chip = ProvenanceChip()
        chip.toggled_auto.connect(
            lambda auto, k=field_key: self._set_shelf_auto(k, auto))
        self._chips[field_key] = chip
        return chip

    def _with_chip(self, widget, field_key: str) -> QWidget:
        wrap = QWidget(); h = QHBoxLayout(wrap); h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(widget, 1)
        h.addWidget(self._shelf_chip(field_key))
        return wrap

    def _virya_labels(self) -> list:
        for s in self._shelf_catalog.get("sources", []):
            if s["id"] == "ascension_virya":
                return list(s["levels"]["labels"])
        return []

    def _on_virya_changed(self, index: int):
        if self._loading:
            return
        if index > 0:
            self._shelf["owned"]["ascension_virya"] = index
        else:
            self._shelf["owned"].pop("ascension_virya", None)
        self._apply_shelf()

    def _sync_virya_combo(self):
        owned = self._shelf.get("owned", {}).get("ascension_virya")
        self.virya.blockSignals(True)
        self.virya.setCurrentIndex(int(owned) if owned else 0)
        self.virya.blockSignals(False)

    def _on_shelf_changed(self, *_):
        owned = self.shelf_page.owned()
        # The Vault no longer shows Virya; preserve its calculator-owned state.
        if "ascension_virya" in self._shelf.get("owned", {}):
            owned["ascension_virya"] = self._shelf["owned"]["ascension_virya"]
        self._shelf["owned"] = owned
        self._apply_shelf()

    def _set_shelf_auto(self, field_key: str, auto: bool):
        cur = set(self._shelf.get("auto", []))
        if auto and field_key not in cur:
            # Going auto keeps the field value: whatever the user's entry
            # holds beyond the shelf's contributions becomes the invisible
            # untracked remainder (game base, event perks, ...).
            spec = FIELD_BY_KEY.get(field_key)
            t = spec.shelf_target if spec else None
            tinfo = self._shelf_catalog.get("targets", {}).get(t, {})
            if tinfo.get("base") == "user":
                d = shelf_derive(self._shelf_catalog, self._shelf).get(t)
                w = getattr(self, spec.widget_attr)
                self._shelf.setdefault("bases", {})[t] = max(
                    0.0, w.value() - (d.total if d else 0.0))
        (cur.add if auto else cur.discard)(field_key)
        self._shelf["auto"] = sorted(cur)
        self._apply_shelf()

    def _apply_shelf(self, recalc: bool = True):
        """Push shelf-derived values into the input widgets: auto fields are
        written and locked; manual fields keep the user's value while their
        chip previews the shelf total. Pill effect renders as read-only auto
        rows inside the existing rows widget."""
        derived = shelf_derive(self._shelf_catalog, self._shelf)
        targets = self._shelf_catalog.get("targets", {})
        auto = set(self._shelf.get("auto", []))
        bases = self._shelf.get("bases", {})
        prev, self._loading = self._loading, True
        for spec in FIELDS:
            t = spec.shelf_target
            if t is None:
                continue
            d = derived.get(t)
            tinfo = targets.get(t, {})
            total = d.total if d else 0.0
            if tinfo.get("unit") == "fraction_pp" and spec.scale:
                total *= spec.scale
            base = bases.get(t, 0.0) if tinfo.get("base") == "user" else 0.0
            w = getattr(self, spec.widget_attr)
            is_auto = spec.key in auto
            if is_auto:
                w.setValue(base + total)
            w.setReadOnly(is_auto)
            chip = self._chips.get(spec.key)
            if chip is not None:
                chip.update_view(d, is_auto, display_total=total)
        pe = derived.get("pill_effect")
        self.pe_rows.set_auto_rows(pe.contributions if pe else ())
        self._loading = prev
        if recalc and not self._loading:
            self.recalc()

    def _update_absorb_base(self, res):
        """Show the selected Grade's base Absorption Ratio, and warn on under-entry."""
        stage = stage_key(self.stage.currentText())
        phase = phase_key(self.phase.currentText())
        grade = self.grade.currentText()
        low = self.engine.base_low(stage, phase, grade)
        if low is None:
            self.absorb_base.setText("")
            return
        # Blessing pp join the base BEFORE the Strive multiplier (official
        # composition), so the readout compares against the blessed base.
        bless = self.bless_pp.value()
        if self.engine.blessing_applies(stage, phase, grade):
            bless += self.bless_window.value()
        base = low * 100 + bless
        entered = self.absorb.value()
        warn = False
        if self.engine.has_strive(stage):
            # res.strive is the engine's implied Strive for these same inputs;
            # when the engine couldn't run (e.g. speed still 0) fall back to
            # the widget-implied value so the readout behaves as before.
            frac = res.strive if res.valid else (
                entered / base - 1 if base > 0 else None)
            strive = (frac if frac is not None else 0.0) * 100
            if abs(strive) < 1e-6:
                strive = 0.0
            msg = tr("Base Absorption: {}%  ·  Strive: {}%").format(f"{base:g}", f"{strive:.0f}")
            stages = self.engine.stages()
            mortal = stage in stages and stages.index(stage) <= stages.index("Incarnation")
            if entered and entered < base - 1e-9:
                msg += tr("  ⚠ below base — Strive can't be negative"); warn = True
            elif strive > STRIVE_CAP_MORTAL * 100 + 1e-9:
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
            self._auto_respira_exp()
            self._save_settings()
        self.copy_btn.setText(tr("Copy results"))
        res = self.engine.calculate(self._inputs())
        self._update_absorb_base(res)
        self._update_array_out()
        self._update_pill_attempts()
        if not res.valid:
            for _, attr in RESULT_ROWS:
                getattr(self, attr).setText("—")
            self.o_error.setText(tr(res.error))
            return
        self.o_error.setText(tr(res.error))
        self.o_phase.setText(self._fmt_band(res.phase_days, res.phase_band))
        self.o_stage.setText(self._fmt_band(res.stage_days, res.stage_band))
        self.o_target.setText(self._fmt_band(res.target_days, res.target_band)
                              if res.target_valid else "—")
        if res.prestock_valid:
            self.o_prestock.setText(
                f"{res.prestock_pct:,.0f}%  — "
                + self._fmt_band(res.prestock_days, res.prestock_band))
            gate = self.timegate.value()
            if gate > 0:
                margin = gate - res.prestock_days
                if margin >= 0:
                    self.o_gate.setText(
                        "✓ " + tr("stocked {} early").format(
                            tr_duration(fmt_days(margin))))
                else:
                    self.o_gate.setText(
                        "✗ " + tr("short by {}").format(
                            tr_duration(fmt_days(-margin))))
            else:
                self.o_gate.setText("—")
        else:
            self.o_prestock.setText("—")
            self.o_gate.setText("—")
        self.o_abode.setText(f"{res.abode_aura:,.1f}")
        self.o_basexp.setText(f"{res.base_xp_per_day:,.0f}")
        self.o_effxp.setText(f"{res.effective_xp_per_day:,.0f}")
        self.o_pillxp.setText(f"{res.pill_xp_per_day:,.0f}")
        flat_share = ((res.pill_xp_per_day + res.respira_xp_per_day
                       + res.elixir_xp_per_day)
                      / res.effective_xp_per_day * 100
                      if res.effective_xp_per_day else 0.0)
        self.o_speedup.setText(tr("{}% of daily XP / +{}% speed").format(
            f"{flat_share:.1f}", f"{res.gem_speedup * 100:.0f}"))
        self.o_speedup.setToolTip(tr(
            "Share of your effective daily XP that comes from flat sources "
            "(pills + Respira + elixirs), and the Aura Gem's speed bonus on "
            "cultivation. Flat XP does not scale with grade EXP, so a high share "
            "means slower progress at higher grades than raw speed suggests."))
        self.o_mythic.setText(f"{res.mythic_pills_per_day:.2f}")
        self.o_pearl.setText(f"{res.pearl_xp_per_day:,.0f}")
        self.o_respira.setText(f"{res.respira_xp_per_day:,.0f}")
        self.o_elixir.setText(f"{res.elixir_xp_per_day:,.0f}")
        self.o_fruit.setText(f"{res.fruit_xp:,.0f}")
        self.o_fruit_days.setText(tr_duration(fmt_days(res.fruit_days_saved)))

    def _copy_results(self):
        plain = lambda s: re.sub(r"<[^>]+>", "", s)
        rows = [
            (tr("Stage"), self.stage.currentText()), (tr("Half-step"), self.phase.currentText()),
            (tr("Grade"), self.grade.currentText()),
        ]
        rows += [(tr(text), plain(getattr(self, attr).text())) for text, attr in RESULT_ROWS]
        text = "\n".join(f"{k}: {v}" for k, v in rows)
        QApplication.clipboard().setText(text)
        self.copy_btn.setText(tr("Copied ✓"))


def _icon_path() -> str:
    for p in (resource_path("breakthrough-calc.png"),
              resource_path("packaging", "breakthrough-calc.png")):
        if os.path.exists(p):
            return p
    return ""


def main():
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
