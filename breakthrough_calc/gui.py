"""Qt GUI for the Breakthrough Calculator."""

from __future__ import annotations

import os
import sys

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QGuiApplication

from . import __version__
from PySide6.QtWidgets import (
    QAbstractSpinBox, QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QGridLayout, QHBoxLayout,
    QInputDialog, QLabel,
    QMainWindow, QPushButton, QScrollArea, QSpinBox, QTabWidget,
    QTextBrowser, QVBoxLayout,
    QWidget,
)

from . import theme, i18n
from .docs import build_guide_pages, build_reference_pages
from .i18n import tr, tr_duration
from .engine import Engine, Inputs, fmt_days, load_pill_sources, load_respira_sources
from .labels import (
    VASE_INPUT_LABELS, phase_disp, phase_key, stage_disp, stage_key,
    vase_input_disp, vase_input_key,
)
from .profiles import ProfileStore, settings_path
from .update_check import UpdateChecker
from .widgets import (
    DonateDialog, PillEffectRows, WheelGuard, clear_accents, link_enabled,
    make_catalog_menu, restyle_all, style_accent,
)

STARS = ["0*", "1*", "2*", "3*", "4*", "5*"]

# Energy Array: base energy is a known constant only for these Stages (wiki).
BASE_ENERGY = 130.0
BASE_ENERGY_STAGES = {"Connection", "Foundation", "Virtuoso", "Nascent", "Incarnation"}

# Strive (the catch-up absorption multiplier) unlocks at Nascent Soul.
STRIVE_STAGES = {"Nascent", "Incarnation", "Voidbreak", "Wholeness", "Perfection",
                 "Nirvana", "Celestial", "Eternal", "Supreme"}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = Engine()
        self._store = ProfileStore(settings_path())
        self._loading = True
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

    # ---- UI construction -------------------------------------------------
    def _build_ui(self):
        self.setWindowTitle(tr("Breakthrough Calculator"))
        clear_accents()  # full rebuild: drop stale accent-label registrations
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
        self.target_phase = QComboBox(); self.target_phase.addItem("")
        self.target_grade = QComboBox(); self.target_grade.addItem("")
        self.timegate = QDoubleSpinBox(); self.timegate.setRange(0, 1000); self.timegate.setDecimals(1); self.timegate.setSuffix(tr(" days"))
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
        style_accent(self.absorb_base, "muted", self._acc)
        f.addRow("", self.absorb_base)
        self.array_out = QLabel("—"); self.array_out.setWordWrap(True)
        style_accent(self.array_out, "muted", self._acc)
        f.addRow("", self.array_out)
        self.array_apply = QPushButton(tr("Apply to Cultivation Speed"))
        self.array_apply.clicked.connect(self._apply_array_speed)
        f.addRow("", self.array_apply)
        f.addRow(tr("Cultivation Speed (XP / Cosmoapsis)"), self.speed)
        f.addRow(tr("Aura Gem"), self.gem)
        f.addRow(tr("Target Stage"), self.target)
        f.addRow(tr("Target half-step"), self.target_phase)
        f.addRow(tr("Target grade"), self.target_grade)
        f.addRow(tr("Timegate lifts in"), self.timegate)
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
        self.pe_catalog = load_pill_sources()
        self.pe_rows = PillEffectRows(self.pe_catalog, lambda: self._acc)
        self.pe_rows.changed.connect(self.recalc)
        f.addRow(tr("Cultivation pill effect"), self.pe_rows)

        self.pill_limit.setToolTip(tr("Shared daily attempt limit for all cultivation pills (vase red pills are exempt)."))
        f.addRow(tr("Daily pill attempts (shared)"), self.pill_limit)
        f.addRow(tr("Legendary (Gold) used / day"), self.gold_day)
        f.addRow(tr("Epic (Purple) used / day"), self.purple_day)
        f.addRow(tr("Rare (Blue) used / day"), self.blue_day)
        self.pill_attempts = QLabel("")
        style_accent(self.pill_attempts, "muted", self._acc)
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
        link_enabled(self.vase, self.vase_star, self.vase_skin, self.vase_charge,
                     self.vase_input, self.vase_input_label)
        link_enabled(self.mirror, self.mirror_star, self.mirror_skin, self.mirror_charge)
        link_enabled(self.pearl, self.pearl_star, self.pearl_skin, self.pearl_charge,
                     self.pearl_xp10, self.pearl_xp10_label)
        lv.addWidget(arts)

        respira = QGroupBox(tr("Respira"))
        rf = QFormLayout(respira)
        self.respira_per_day = QDoubleSpinBox(); self.respira_per_day.setRange(0, 1e5)
        self.respira_per_day.setToolTip(tr(
            "Your daily Respira attempt limit as shown in-game (base + permanent "
            "bonus attempts). The base limit is 10/day (confirmed from game "
            "data). Leave out temporary event attempts."))
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

            def rsp_label(src):
                if src.get("kind") == "attempt":
                    return f'{src["name"]}  (+{src["value"]:g}/day)'
                label = tr("info") if src.get("kind") == "exp_pct" else tr("pill limit")
                return f'{src["name"]}  ({label})'
            self._respira_menu = make_catalog_menu(
                rsp_btn, self.respira_catalog, rsp_label,
                checkable=True, enabled=lambda src: src.get("kind") == "attempt",
                on_sync=self._sync_respira_menu,
                on_triggered=self._toggle_respira_source)
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
        style_accent(respira_hint, "muted", self._acc)
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
        self.RESULT_ROWS = [
            ("Half-step breakthrough in", "o_phase"),
            ("Stage breakthrough in", "o_stage"),
            ("Target Stage reached in", "o_target"),
            ("Prestock for target (overcap)", "o_prestock"),
            ("At timegate", "o_gate"),
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
        self.o_error = QLabel(""); style_accent(self.o_error, "bad", self._acc); self.o_error.setWordWrap(True)
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
            lbl = mklabel(); style_accent(lbl, "good", self._acc, "font-weight: bold; color: {};"); self.pin_labels[attr] = lbl
            pf.addRow(tr(text), lbl)
        self.unpin_btn = QPushButton(tr("Clear A")); self.unpin_btn.clicked.connect(self._unpin_results)
        pf.addRow(self.unpin_btn)
        self.pin_box.setVisible(False)
        outer.addWidget(self.pin_box, 1)

        tabs = QTabWidget()
        tabs.addTab(central, tr("Calculator"))
        self._tabs = tabs
        self._doc_history = []
        # Doc-tree registry: top-level tab index per tree, populated where the
        # tabs are inserted (slug -> sub-tab maps live in _ref/_guide_slugs).
        self._doc_tab_index = {}
        self._doc_tab_index["ref"] = tabs.count()
        tabs.addTab(self._build_reference_tab(), tr("Reference"))
        self._doc_tab_index["guide"] = tabs.count()
        tabs.addTab(self._build_guide_tab(), tr("Guide"))
        self.setCentralWidget(tabs)

    def _rebuild_doc_tabs(self):
        # Rebuild the Reference and Guide tabs (all sub-tab browsers) so accent
        # colors baked into the HTML follow theme changes; keep the sub-tabs.
        sub = self._ref_tabs.currentIndex() if getattr(self, "_ref_tabs", None) else 0
        gsub = self._guide_tabs.currentIndex() if getattr(self, "_guide_tabs", None) else 0
        ref_idx = self._doc_tab_index["ref"]
        guide_idx = self._doc_tab_index["guide"]
        self._tabs.removeTab(guide_idx)
        self._tabs.removeTab(ref_idx)
        self._tabs.insertTab(ref_idx, self._build_reference_tab(), tr("Reference"))
        self._tabs.insertTab(guide_idx, self._build_guide_tab(), tr("Guide"))
        self._ref_tabs.setCurrentIndex(sub)
        self._guide_tabs.setCurrentIndex(gsub)
        self._update_back_buttons()
        self.resize(1180, 680)  # note: re-triggers on every theme change

    def _doc_sub_tabs(self) -> dict:
        """Top-level tab index -> that doc tree's sub-QTabWidget."""
        return {self._doc_tab_index["ref"]: self._ref_tabs,
                self._doc_tab_index["guide"]: self._guide_tabs}

    # Internal link scheme for Reference/Guide cross-references:
    # app://ref/<slug> and app://guide/<slug>. The slug -> sub-tab maps are
    # derived by enumerating the docs.py page lists, so they cannot drift
    # from the tab order.
    def _open_doc_link(self, url: QUrl):
        if url.scheme() != "app":
            QDesktopServices.openUrl(url)
            return
        tree, slug = url.host(), url.path().strip("/")
        anchor = url.fragment()
        if tree == "ref" and slug in self._ref_slugs:
            self._push_doc_history()
            self._tabs.setCurrentIndex(self._doc_tab_index["ref"])
            self._ref_tabs.setCurrentIndex(self._ref_slugs[slug])
            self._scroll_to_anchor(self._ref_tabs, anchor)
        elif tree == "guide" and slug in self._guide_slugs:
            self._push_doc_history()
            self._tabs.setCurrentIndex(self._doc_tab_index["guide"])
            self._guide_tabs.setCurrentIndex(self._guide_slugs[slug])
            self._scroll_to_anchor(self._guide_tabs, anchor)

    @staticmethod
    def _scroll_to_anchor(sub, anchor):
        # Land on the relevant section (app://ref/<slug>#<anchor>); without
        # an anchor, start the destination page from the top.
        w = sub.currentWidget()
        if not isinstance(w, QTextBrowser):
            return
        if anchor:
            w.scrollToAnchor(anchor)
        else:
            w.verticalScrollBar().setValue(0)

    # Back-navigation for the app:// cross-links: each link click pushes the
    # (tab, sub-tab, scroll) the reader left, so the Back button in the tab
    # corner returns them to the exact spot they were reading.
    def _doc_location(self):
        idx = self._tabs.currentIndex()
        sub = self._doc_sub_tabs().get(idx)
        if sub is None:
            return None
        w = sub.currentWidget()
        scroll = w.verticalScrollBar().value() if isinstance(w, QTextBrowser) else 0
        return (idx, sub.currentIndex(), scroll)

    def _push_doc_history(self):
        loc = self._doc_location()
        if loc:
            self._doc_history.append(loc)
            self._update_back_buttons()

    def _go_back(self):
        if not self._doc_history:
            return
        idx, sub_idx, scroll = self._doc_history.pop()
        self._tabs.setCurrentIndex(idx)
        sub = self._doc_sub_tabs()[idx]
        sub.setCurrentIndex(sub_idx)
        w = sub.currentWidget()
        if isinstance(w, QTextBrowser):
            w.verticalScrollBar().setValue(scroll)
        self._update_back_buttons()

    def _update_back_buttons(self):
        show = bool(self._doc_history)
        for tabs in (getattr(self, "_ref_tabs", None),
                     getattr(self, "_guide_tabs", None)):
            if tabs is not None and tabs.cornerWidget() is not None:
                tabs.cornerWidget().setVisible(show)

    def _build_doc_tab(self, pages) -> QTabWidget:
        """Wrap ordered (slug, title, html) pages in QTextBrowser sub-tabs
        with the app:// link wiring and a Back corner button."""
        tabs = QTabWidget()
        for _slug, title, html in pages:
            b = QTextBrowser()
            b.setOpenLinks(False)
            b.anchorClicked.connect(self._open_doc_link)
            b.setHtml(html)
            # Escape & so QTabWidget doesn't eat it as a mnemonic marker
            tabs.addTab(b, title.replace("&", "&&"))
        back = QPushButton(tr("← Back"))
        back.clicked.connect(self._go_back)
        back.setVisible(False)
        tabs.setCornerWidget(back)
        return tabs

    def _build_reference_tab(self) -> QWidget:
        pages = build_reference_pages(self._acc, self.engine.data,
                                      self.pe_catalog, self.respira_catalog)
        self._ref_slugs = {slug: i for i, (slug, _, _) in enumerate(pages)}
        self._ref_tabs = tabs = self._build_doc_tab(pages)
        return tabs

    def _build_guide_tab(self) -> QWidget:
        pages = build_guide_pages(self._acc)
        self._guide_slugs = {slug: i for i, (slug, _, _) in enumerate(pages)}
        self._guide_tabs = tabs = self._build_doc_tab(pages)
        return tabs

    # ---- signal wiring ---------------------------------------------------
    def _wire(self):
        self.stage.currentTextChanged.connect(self._on_stage_changed)
        self.phase.currentTextChanged.connect(self._on_phase_changed)
        self.target.currentTextChanged.connect(self._on_target_stage_changed)
        self.target_phase.currentTextChanged.connect(self._on_target_phase_changed)
        for w in (self.grade, self.gem, self.target_grade, self.top_stage, self.pill_rank, self.vase_star,
                  self.vase_input, self.mirror_star, self.pearl_star, self.fruit_rank, self.extractor):
            w.currentTextChanged.connect(self.recalc)
        for w in (self.completion, self.speed, self.absorb, self.pill_limit,
                  self.gold_day, self.purple_day, self.blue_day, self.mark_blue,
                  self.mark_purple, self.mark_gold, self.pearl_xp10,
                  self.respira_per_day, self.respira_event, self.respira_exp, self.fruit_count, self.reset_in,
                  self.timegate):
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
        self._wheel_guard = WheelGuard(self)
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
            self.target_phase: "Optional: a half-step within the target Stage. Blank = start of the Stage.",
            self.target_grade: "Optional: a grade within the target half-step. Blank = start of the half-step.",
            self.timegate: "Optional: days until the world-level timegate lifts (shown in-game once someone "
                           "reaches the last half-step). Compared against the prestock time. Reminder: use "
                           "Myrimon fruits BEFORE the gate — the gate unlocks the next realm, so they lose the +50% highest-realm bonus.",
            self.o_prestock: "Overcap needed for the target, in the game's own display convention (XP since the "
                             "start of the final half-step ÷ that half-step's total), and the time to stock it. "
                             "While timegated you stay parked at the Stage cap, so XP accrues at your CURRENT "
                             "speed — no future-grade speedups. Slower than the ungated 'Target reached in'.",
            self.o_gate: "Whether your stocked XP reaches the target before the timegate lifts.",
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
        return Inputs(
            stage=stage_key(self.stage.currentText()), phase=phase_key(self.phase.currentText()),
            grade=self.grade.currentText(), grade_completion=self.completion.value() / 100.0,
            culti_speed=self.speed.value(), absorption_ratio=self.absorb.value() / 100.0,
            aura_gem=i18n.reverse(self.gem.currentText()), target_stage=stage_key(self.target.currentText()),
            target_phase=phase_key(self.target_phase.currentText()),
            target_grade=self.target_grade.currentText(),
            timegate_days=self.timegate.value(),
            top_stage=stage_key(self.top_stage.currentText()),
            pill_rank=self.pill_rank.currentText(), pill_effect=self.pe_rows.total() / 100.0,
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
            "gem": self.gem, "target": self.target,
            "target_phase": self.target_phase, "target_grade": self.target_grade,
            "timegate_days": self.timegate,
            "top_stage": self.top_stage,
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
        "phase": phase_key, "target_phase": phase_key,
        "gem": i18n.reverse, "extractor": i18n.reverse,
        "vase_input": vase_input_key,
    }
    _KEY_TO_COMBO = {
        "stage": stage_disp, "target": stage_disp, "top_stage": stage_disp,
        "phase": phase_disp, "target_phase": phase_disp,
        "gem": tr, "extractor": tr,
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
        vals["pill_sources"] = self.pe_rows.sources()
        vals["respira_sources"] = sorted(self._respira_checked)
        return vals

    def _apply_state(self, vals: dict):
        prev, self._loading = self._loading, True
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
