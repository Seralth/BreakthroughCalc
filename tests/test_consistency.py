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
            if fname == "i18n_glossary.json":
                continue  # curation input, deliberately not shipped
            if fname.endswith(".json"):
                self.assertIn(f"assets/data/{fname}", pubspec,
                              f"data/{fname} missing from pubspec assets")


if __name__ == "__main__":
    unittest.main()
