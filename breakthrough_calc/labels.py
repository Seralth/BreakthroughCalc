"""Combo-box label domains: internal data keys <-> localized display strings.

Settings persist the INTERNAL keys; legacy files that stored display names
(in any language) are migrated via i18n.reverse + the reverse maps kept by
each LabelMap.
"""

from __future__ import annotations

from . import i18n
from .i18n import tr

PHASE_LABELS = {"N/A": "N/A", "EARLY": "Early", "MIDDLE": "Middle", "LATE": "Late"}

# Display-only canonical Stage names; internal data keys stay unchanged.
STAGE_LABELS = {"Nascent": "Nascent Soul"}

# Vase input pill: internal key -> English display item.
VASE_INPUT_LABELS = {"Blue": "Blue/White", "Purple": "Purple (Epic)",
                     "Gold": "Gold (Legendary)"}


class LabelMap:
    """One combo domain's converters.

    disp(key): internal key -> tr()'d display label.
    key(disp): displayed (localized) name, legacy English display name, or an
    internal key -> internal key.
    """

    def __init__(self, labels: dict[str, str]):
        self.labels = labels
        self.keys = {v: k for k, v in labels.items()}

    def disp(self, key: str) -> str:
        return tr(self.labels.get(key, key))

    def key(self, disp: str) -> str:
        return self.keys.get(i18n.reverse(disp), i18n.reverse(disp))


STAGE = LabelMap(STAGE_LABELS)
PHASE = LabelMap(PHASE_LABELS)
VASE_INPUT = LabelMap(VASE_INPUT_LABELS)


def stage_disp(key: str) -> str:
    return STAGE.disp(key)


def stage_key(disp: str) -> str:
    """Displayed (localized) stage name, legacy English display name, or an
    internal key -> internal key."""
    return STAGE.key(disp)


def phase_disp(key: str) -> str:
    return PHASE.disp(key)


def phase_key(disp: str) -> str:
    return PHASE.key(disp)


def vase_input_disp(key: str) -> str:
    return VASE_INPUT.disp(key)


def vase_input_key(disp: str) -> str:
    return VASE_INPUT.key(disp)
