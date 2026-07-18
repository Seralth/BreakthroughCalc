"""Cross-platform consistency pins.

The desktop package and the Flutter app are parallel implementations; these
constants are maintained in both trees and have drifted before (desktop
shipped __version__ 2.12 while mobile was at 2.14 — the desktop update
checker compares against the repo-wide latest GitHub release, so a drifted
desktop build nags "update available" forever).
"""

import json
import os
import re
import unittest

import breakthrough_calc

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*parts: str) -> str:
    with open(os.path.join(REPO, *parts), encoding="utf-8") as f:
        return f.read()


class VersionSync(unittest.TestCase):
    def test_desktop_and_mobile_versions_match(self):
        pubspec = re.search(r"^version:\s*([\d.]+)\+\d+\s*$",
                            read("mobile", "pubspec.yaml"), re.M)
        self.assertIsNotNone(pubspec, "pubspec version line not found")
        main_dart = re.search(r"const appVersion = '([\d.]+)';",
                              read("mobile", "lib", "main.dart"))
        self.assertIsNotNone(main_dart, "appVersion const not found in main.dart")

        desktop = breakthrough_calc.__version__
        # pubspec carries major.minor.patch; the app-facing versions are
        # major.minor. All three must agree on major.minor.
        pub_mm = ".".join(pubspec.group(1).split(".")[:2])
        self.assertEqual(desktop, pub_mm,
                         "breakthrough_calc.__version__ vs mobile/pubspec.yaml")
        self.assertEqual(desktop, main_dart.group(1),
                         "breakthrough_calc.__version__ vs main.dart appVersion")


class DonationSync(unittest.TestCase):
    def test_donate_constants_match_mobile(self):
        main_dart = read("mobile", "lib", "main.dart")
        self.assertIn(breakthrough_calc.DONATE_URL, main_dart,
                      "DONATE_URL differs between platforms")
        self.assertIn(breakthrough_calc.DONATE_RID, main_dart,
                      "DONATE_RID differs between platforms — codes gift to "
                      "the wrong recipient")


class RepoSlugSync(unittest.TestCase):
    def test_update_check_repo_slug_matches(self):
        self.assertIn(f"github.com/repos/{breakthrough_calc.REPO}/",
                      read("mobile", "lib", "fetch_release_io.dart"))


class DataAssetList(unittest.TestCase):
    def test_pubspec_declares_every_data_catalog(self):
        """sync_data.sh copies data/ into mobile assets; a new data file that
        is not declared in pubspec silently never ships on mobile."""
        pubspec = read("mobile", "pubspec.yaml")
        for fname in sorted(os.listdir(os.path.join(REPO, "data"))):
            if fname in ("i18n_glossary.json", "pill_effect_sources.json",
                         "respira_sources.json"):
                # curation input / legacy-migration fixtures, not shipped
                continue
            if fname.endswith(".json"):
                self.assertIn(f"assets/data/{fname}", pubspec,
                              f"data/{fname} missing from pubspec assets")


if __name__ == "__main__":
    unittest.main()


class SharedTranslations(unittest.TestCase):
    """Translations are one shared file (data/i18n.json) that both apps load
    at runtime — so desktop and mobile can never drift. Guard the wiring:
    neither platform may re-hardcode a translation table."""

    def test_desktop_loads_from_the_shared_json(self):
        from breakthrough_calc import i18n
        shared = json.loads(read("data", "i18n.json"))
        # every shared entry is reachable through the desktop table
        for en, row in list(shared.items())[:50]:
            for lang, val in row.items():
                self.assertEqual(i18n.TRANSLATIONS.get(lang, {}).get(en), val)

    def test_mobile_loads_the_shared_asset_not_a_literal(self):
        dart = read("mobile", "lib", "i18n.dart")
        self.assertIn("void loadTranslations(", dart)
        self.assertNotIn("const Map<String, Map<String, String>> _t", dart)
        main = read("mobile", "lib", "main.dart")
        self.assertIn("assets/data/i18n.json", main)
        self.assertIn("loadTranslations(", main)
