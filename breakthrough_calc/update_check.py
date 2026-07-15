"""GitHub release check for the desktop app.

UpdateChecker owns the network access and emits result(label_text, visible)
for the toolbar's update label; the manual flag controls whether negative
outcomes (up to date / check failed) are surfaced at all.
"""

from __future__ import annotations

import json

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from . import REPO, __version__, parse_version
from .i18n import tr


class UpdateChecker(QObject):
    # (label text, visible) for the toolbar's update label.
    result = Signal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._nam = QNetworkAccessManager(self)

    def check(self, manual: bool = False):
        req = QNetworkRequest(QUrl(f"https://api.github.com/repos/{REPO}/releases/latest"))
        req.setHeader(QNetworkRequest.UserAgentHeader, f"BreakthroughCalc/{__version__}")
        req.setTransferTimeout(5000)
        reply = self._nam.get(req)
        reply.finished.connect(lambda: self._on_reply(reply, manual))

    def _on_reply(self, reply: QNetworkReply, manual: bool):
        reply.deleteLater()
        latest, url = None, f"https://github.com/{REPO}/releases/latest"
        if reply.error() == QNetworkReply.NoError:
            try:
                data = json.loads(bytes(reply.readAll()).decode("utf-8"))
                latest = parse_version(data.get("tag_name", ""))
                url = data.get("html_url") or url
            except ValueError:
                latest = None
        if latest is None:
            if manual:
                self.result.emit(tr("Update check failed"), True)
            return
        if latest > parse_version(__version__):
            tag = ".".join(str(x) for x in latest)
            self.result.emit(
                f'<a href="{url}">{tr("Update available: v{}").format(tag)}</a>', True)
        elif manual:
            self.result.emit(tr("Up to date (v{})").format(__version__), True)
