"""Cross-reference navigation for the Reference/Guide documentation trees.

One DocController owns the reader's location, the back-history stack and the
`app://ref|guide/<slug>#<anchor>` cross-link parsing — the doc-nav state and
logic that used to be scattered inline across MainWindow. It is the desktop
twin of mobile's DocNavigator (mobile/lib/doc_nav.dart): the consumption
contract in one place.

MainWindow builds the Qt tab widgets (they need `tr()`, the page builders and
the accent palette) and registers each tree here via `register_tree`; a tapped
link's `anchorClicked` and the corner Back button delegate to `open_link` /
`go_back`, which drive top-tab + sub-tab switching, anchor scrolling and the
Back button's visibility.
"""

from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QTextBrowser


class DocController:
    """Doc-tree navigation state + logic over a top-level QTabWidget.

    Holds, per doc tree ('ref'/'guide'): its top-level tab index, its sub-tab
    QTabWidget and its slug -> sub-index map, plus the shared back-history
    stack of (top index, sub index, scroll) locations. Fresh per UI rebuild,
    so a language switch starts with an empty history and re-registered
    widgets (mirrors the old `_doc_history.clear()`).
    """

    def __init__(self, top_tabs):
        self._tabs = top_tabs          # top-level QTabWidget
        self._history = []             # [(top_idx, sub_idx, scroll)]
        self.tab_index = {}            # tree -> top-level tab index
        self._sub = {}                 # tree -> sub-tab QTabWidget
        self._slugs = {}               # tree -> {slug: sub index}

    # ---- registration ----------------------------------------------------
    def register_tree(self, tree: str, top_index: int, sub_tabs, slugs: dict):
        """Record (or replace, on rebuild) a doc tree's widgets and indices."""
        self.tab_index[tree] = top_index
        self._sub[tree] = sub_tabs
        self._slugs[tree] = slugs

    def sub_index(self, tree: str) -> int:
        """Current sub-tab index of a tree (0 if not registered yet)."""
        sub = self._sub.get(tree)
        return sub.currentIndex() if sub is not None else 0

    def set_sub_index(self, tree: str, index: int):
        sub = self._sub.get(tree)
        if sub is not None:
            sub.setCurrentIndex(index)

    def _sub_tabs(self) -> dict:
        """Top-level tab index -> that doc tree's sub-QTabWidget."""
        return {self.tab_index[t]: self._sub[t] for t in self._sub}

    # ---- cross-link navigation -------------------------------------------
    # Internal link scheme for Reference/Guide cross-references:
    # app://ref/<slug> and app://guide/<slug>. The slug -> sub-tab maps are
    # derived by enumerating the docs.py page lists, so they cannot drift
    # from the tab order.
    def open_link(self, url: QUrl):
        if url.scheme() != "app":
            QDesktopServices.openUrl(url)
            return
        tree, slug = url.host(), url.path().strip("/")
        anchor = url.fragment()
        if tree in self._slugs and slug in self._slugs[tree]:
            self.push_history()
            self._tabs.setCurrentIndex(self.tab_index[tree])
            sub = self._sub[tree]
            sub.setCurrentIndex(self._slugs[tree][slug])
            self.scroll_to_anchor(sub, anchor)

    @staticmethod
    def scroll_to_anchor(sub, anchor):
        # Land on the relevant section (app://ref/<slug>#<anchor>); without
        # an anchor, start the destination page from the top.
        w = sub.currentWidget()
        if not isinstance(w, QTextBrowser):
            return
        if anchor:
            w.scrollToAnchor(anchor)
        else:
            w.verticalScrollBar().setValue(0)

    # ---- back-navigation --------------------------------------------------
    # Each link click pushes the (tab, sub-tab, scroll) the reader left, so the
    # Back button in the tab corner returns them to the exact spot.
    def _location(self):
        idx = self._tabs.currentIndex()
        sub = self._sub_tabs().get(idx)
        if sub is None:
            return None
        w = sub.currentWidget()
        scroll = w.verticalScrollBar().value() if isinstance(w, QTextBrowser) else 0
        return (idx, sub.currentIndex(), scroll)

    def push_history(self):
        loc = self._location()
        if loc:
            self._history.append(loc)
            self.update_back_buttons()

    def go_back(self):
        if not self._history:
            return
        idx, sub_idx, scroll = self._history.pop()
        self._tabs.setCurrentIndex(idx)
        sub = self._sub_tabs()[idx]
        sub.setCurrentIndex(sub_idx)
        w = sub.currentWidget()
        if isinstance(w, QTextBrowser):
            w.verticalScrollBar().setValue(scroll)
        self.update_back_buttons()

    def update_back_buttons(self):
        show = bool(self._history)
        for tabs in self._sub.values():
            corner = tabs.cornerWidget()
            if corner is not None:
                corner.setVisible(show)
