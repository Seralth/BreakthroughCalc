"""Cross-reference integrity for the Reference/Guide docs.

The pages link to each other with app://ref/<slug>[#<anchor>] and
app://guide/<slug>[#<anchor>] hrefs, but nothing guaranteed the targets
existed -- a renamed section or anchor would silently dead-link in the app.
These tests build every page and assert each cross-link resolves: the slug
is a real page in the matching page set, and the anchor is an
<a name='...'> present in that specific target page's HTML.
"""

import re
from collections import defaultdict

import pytest

from breakthrough_calc.docs import build_guide_pages, build_reference_pages
from breakthrough_calc.engine import Engine
from breakthrough_calc.shelf import load_sources

# docs.py is Qt-free and only reads accent color strings (acc["muted"],
# acc["bad"]); use a Qt-free stub so this test runs on CI's Qt-less test
# job instead of importing theme (which pulls PySide6).
_ACCENTS: dict = defaultdict(lambda: "#888888")

# app://<tree>/<slug> or app://<tree>/<slug>#<anchor>
_LINK_RE = re.compile(r"app://(ref|guide)/([a-z0-9_-]+)(?:#([a-z0-9_-]+))?")


def _anchor_present(html: str, anchor: str) -> bool:
    """True if the page defines <a name='anchor'> (either quote style)."""
    return re.search(rf"<a\s+name=['\"]{re.escape(anchor)}['\"]", html) is not None


@pytest.fixture(scope="module")
def ref_pages():
    return build_reference_pages(_ACCENTS, Engine().data,
                                 load_sources())


@pytest.fixture(scope="module")
def guide_pages():
    return build_guide_pages(_ACCENTS)


def _check_page_list(pages):
    assert isinstance(pages, list)
    assert pages, "expected a non-empty list of pages"
    for entry in pages:
        slug, title, html = entry  # unpacks -> shape is (slug, title, html)
        assert isinstance(slug, str) and slug
        assert isinstance(title, str) and title
        assert isinstance(html, str) and html


def test_reference_pages_build(ref_pages):
    _check_page_list(ref_pages)


def test_guide_pages_build(guide_pages):
    _check_page_list(guide_pages)


def test_all_cross_reference_links_resolve(ref_pages, guide_pages):
    """Every app://ref|guide/<slug>[#<anchor>] target must exist: the slug in
    the corresponding page set, and the anchor in that target page's HTML."""
    # tree -> {slug: html}
    by_tree = {
        "ref": {slug: html for slug, _, html in ref_pages},
        "guide": {slug: html for slug, _, html in guide_pages},
    }
    all_html = "\n".join(html for _, _, html in (*ref_pages, *guide_pages))

    links = _LINK_RE.findall(all_html)
    assert links, "expected the docs to contain cross-reference links"

    for tree, slug, anchor in links:
        target = f"app://{tree}/{slug}" + (f"#{anchor}" if anchor else "")
        assert slug in by_tree[tree], (
            f"dead link {target}: no '{slug}' page in the {tree} set "
            f"(have: {sorted(by_tree[tree])})")
        if anchor:
            assert _anchor_present(by_tree[tree][slug], anchor), (
                f"dead link {target}: no <a name='{anchor}'> in the "
                f"{tree}/{slug} page")
