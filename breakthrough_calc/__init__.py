__version__ = "3.4"


def parse_version(s: str):
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

# GitHub repo used by the update checker and release links.
REPO = "Seralth/BreakthroughCalc"

# Donations: in-game voucher gifting via SEAGM (no URL prefill supported —
# the RID must be pasted into the site's RID field manually).
DONATE_URL = "https://www.seagm.com/en-us/overmortal-vouchers-global"
DONATE_RID = "28953_U1C466A474D1A0000"
