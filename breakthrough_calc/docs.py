"""Reference/Guide documentation content for the desktop app (no Qt).

build_reference_pages() / build_guide_pages() return ordered
[(slug, title, html)] lists. The GUI wraps each page in a QTextBrowser and
derives the slug -> sub-tab-index maps by enumeration, so the order here IS
the tab order and defines the app://ref/<slug> and app://guide/<slug> link
targets used for cross-references.
"""

from __future__ import annotations

from .catalog import model_range

_ISSUES_URL = "https://github.com/Seralth/BreakthroughCalc/issues"


def _footer(color: str, prose: str) -> str:
    """Shared feedback footer. The reference pages color it with the theme's
    muted accent while the guide hardcodes gray — both preserved exactly."""
    return (f"<hr><p style='color:{color}'>{prose}"
            f"<a href='{_ISSUES_URL}'>github.com/Seralth/BreakthroughCalc/issues</a>.</p>")


def _vault_bonus_rows(shelf_catalog: dict, wanted: dict) -> list:
    """[[source name, bonus summary], ...] for every Vault entry with an
    effect aimed at one of `wanted`'s target ids ({target_id: unit_suffix}).
    Renders from the same catalog the Vault uses so it can't drift."""
    rows = []
    for s in (shelf_catalog or {}).get("sources", []):
        parts = []
        for e in s.get("effects", []):
            tid = e.get("target")
            if tid not in wanted:
                continue
            if "value_model" in e:
                lo, hi = model_range(e["value_model"])
                parts.append(f'{lo:g}–{hi:g}'
                             f'{wanted[tid]} by star/upgrade')
                continue
            if e.get("value") is None:
                continue
            part = f'+{e["value"]:g}{wanted[tid]}'
            ml = e.get("min_level")
            if isinstance(ml, int) and ml > 1:
                kind = s.get("levels", {}).get("kind")
                part += (f" (Tier {ml})" if kind == "tier"
                         else f" (level {ml})")
            elif ml == "max":
                part += " (max level)"
            parts.append(part)
        if parts:
            name = s["name"]
            if s.get("rank"):
                name += f' ({s["rank"]} book)'
            rows.append([name, ", ".join(parts)])
    return rows


def _curio_bonus_rows(shelf_catalog: dict) -> list:
    """[[curio name, cultivation effect summary], ...] for every curio that
    helps cultivation (pill effect, Respira, abode aura, Aura Gem gains,
    auxiliary path). Renders from the catalog so it can't drift. Sorted by
    name."""
    cult = {"pill_effect", "pill_attempts", "respira_attempts",
            "respira_effect"}
    rows = []
    for s in (shelf_catalog or {}).get("sources", []):
        if s.get("category") != "curio":
            continue
        parts = []
        for e in s.get("effects", []):
            tid = e.get("target")
            note = e.get("note", "")
            if tid == "info":
                if "Abode Aura" in note or "Aura Gem" in note \
                        or "Respira" in note or "Auxiliary" in note:
                    parts.append(note.split(" (inside")[0].rstrip("."))
                continue
            if tid not in cult:
                continue
            if "value_model" in e:
                lo, hi = model_range(e["value_model"])
                parts.append(f'Cultivation Pill Effect '
                             f'+{lo:g}% to +{hi:g}% '
                             f'by star and upgrade')
            elif e.get("value") is not None:
                parts.append(note.rstrip(".") or f'+{e["value"]:g}')
        if parts:
            rows.append([s["name"], "; ".join(dict.fromkeys(parts))])
    rows.sort(key=lambda r: r[0])
    return rows


def build_reference_pages(acc: dict, engine_data: dict,
                          shelf_catalog: dict) -> list:
    """Read-only reference, split into topic sub-tabs. Tables render from
    the same data the engine uses so they can't drift from the calculations."""
    d = engine_data
    muted = acc["muted"]

    def table(title, headers, rows, note=""):
        h = f"<h3>{title}</h3><table cellpadding='4' cellspacing='0' border='1' style='border-collapse:collapse'>"
        h += "<tr>" + "".join(f"<th>{c}</th>" for c in headers) + "</tr>"
        for r in rows:
            h += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
        h += "</table>"
        if note:
            h += f"<p style='color:{muted}'>{note}</p>"
        return h

    footer = _footer(muted, (
        "Spotted an error, or have data for a "
        "\"?\" in a table (a screenshot of a tier you've crossed, an endgame "
        "number)? Please report it at "))

    # ---- Basics --------------------------------------------------------
    basics = "<h2>Basics</h2>"
    basics += (
        "<a name='cultivation'></a><h3>How cultivation works</h3>"
        "<p>Your character gains cultivation EXP automatically, one tick every "
        "<b>8 seconds</b> (a \"Cosmoapsis\"). The EXP per tick is your <b>Cultivation "
        "Speed</b>, and everything about progression speed hangs off this one number:</p>"
        "<p style='margin-left:16px'><b>Cultivation Speed = Abode Aura × Absorption Ratio</b></p>"
        "<p><b>Abode Aura</b> is your abode's output: a base energy (130 for Connection "
        "through Incarnation) multiplied by your total aura bonus — the sum of your "
        "Energy Array level, aura curios, sect level bonus, and similar. <b>Absorption "
        "Ratio</b> is how much of that aura you absorb: each Stage/Grade has a base "
        "band that rises as you progress, plus bonuses from gear and Strive. All three "
        "numbers are shown together on the in-game <b>Cultivation Bonus</b> screen, "
        "which is where the calculator's inputs come from.</p>"
        "<p>Progression is Stage → Half-step (Early/Middle/Late) → Grade. Each grade "
        "requires a fixed amount of EXP; the calculator sums the remaining EXP through "
        "your target and divides by your projected speed at each future grade.</p>"
        "<h3>The three Worlds</h3>"
        "<p>Stages group into three Worlds (the in-game realm ladder "
        "[Human – Spirit – Immortal]):</p>"
        "<table cellpadding='4' cellspacing='0' border='1' "
        "style='border-collapse:collapse'>"
        "<tr><th>World</th><th>Stages</th><th>Entered by</th></tr>"
        "<tr><td>Mortal World</td><td>Novice → Connection → Foundation → "
        "Virtuoso → Nascent Soul → Incarnation</td><td>—</td></tr>"
        "<tr><td>Spiritual World</td><td>Voidbreak → Wholeness → Perfection "
        "→ Nirvana</td><td>Ascension (the first timegate)</td></tr>"
        "<tr><td>Immortal World</td><td>Celestial → Eternal → Supreme</td>"
        "<td>Transcendence</td></tr>"
        "</table>"
        "<p>World boundaries carry the big resets — a fresh Myrimon fruit "
        "tier and extractor — while pill ranks step with every major Stage "
        "(Connection 1R … Incarnation 5R, Voidbreak 6R … Supreme 12R). Each "
        "era from Incarnation on is paced by a server timegate "
        "(<a href='app://guide/timegate'>Guide → Timegate</a>).</p>"
        "<h3>Strive (the catch-up mechanic)</h3>"
        "<p>From Nascent Soul onward, <b>Strive</b> multiplies your absorption: "
        "Absorption = (stage base + Virya blessing points) × (1 + Strive) — the "
        "blessing points join in from Incarnation (Perfected) on (<a "
        "href='app://guide/timegate'>Guide → Timegate</a>). It's a catch-up bonus that GROWS the "
        "further you are behind your server's #1 cultivator and fades to zero as you "
        "close the gap — so long-term projections made at a high Strive are optimistic. "
        "Set \"Server #1's Stage\" in the calculator to model the drop-off. "
        "Counter-intuitively, Strive does not change your projected time at your "
        "current position — it cancels out of the math — it only matters for how speed "
        "evolves as you climb.</p>")
    basics += ("<h3>Core formulas</h3><ul>"
               "<li>Cultivation Speed = Abode Aura × Absorption Ratio</li>"
               "<li>Abode Aura = 130 × (1 + total aura bonus) — base 130 holds for "
               "Connection through Incarnation</li>"
               "<li>Cultivation ticks every 8 seconds (one Cosmoapsis)</li>"
               "<li>Absorption = (stage base + Virya blessing points) × (1 + Strive); "
               "Strive unlocks at Nascent Soul and fades as you approach your server's #1</li>"
               "<li>Pill EXP = base × (1 + pill effect + quality star mark [+ Vase star/skin "
               "for reds])</li></ul>"
               "<h3>Crit variance (best / worst)</h3>"
               "<p>Respira crits and fruit gushes are random, so the breakthrough estimate "
               "carries a range. The app shows a <b>best / worst</b> band (a ~90% likely "
               "interval, not literal extremes). Because these are sums of many independent "
               "rolls, luck averages out: the band is widest on short estimates and tightens "
               "as the horizon grows — the opposite of runaway long-term drift. Fruit gushes "
               "also have a pity floor (a gush is guaranteed within 6 fruits of the last one), which further "
               "narrows the fruit side of the band.</p>"
               "<a name='tips'></a><h3>Tips for using the calculator</h3>"
               "<ul><li>Fill in Abode Aura and Absorption Ratio from the Cultivation Bonus "
               "screen and press Apply — that guarantees a current speed. A red warning "
               "means one of your readings is stale.</li>"
               "<li>Re-read your numbers after any upgrade that touches aura (Energy Array, "
               "curios, sect level) — bonuses creep constantly and quietly.</li>"
               "<li>Percentages in this game stack additively almost everywhere (pill "
               "effect sources, artifact star + skin bonuses, energy discounts). When in "
               "doubt, add percentage points; don't multiply.</li>"
               "<li>Save a profile per character/scenario from the toolbar; each profile "
               "keeps its own inputs.</li>"
               "<li>Projections assume instant first-try breakthroughs and today's daily "
               "routine held constant — treat long-range estimates (with high Strive "
               "especially) as optimistic bounds.</li></ul>"
               "<p>Realm timegates pace whole-server progression; Myrimon fruits (see the "
               "Myrimon &amp; Extractor tab) are the main F2P tool for meeting them. The "
               "prestock playbook for a gate is on <a href='app://guide/timegate'>Guide → "
               "Timegate</a>.</p>")

    # ---- Pills & Respira -------------------------------------------------
    pills = "<h2>Pills &amp; Respira</h2>"
    pills += (
        "<a name='daily'></a><h3>Daily pills</h3>"
        "<p>Cultivation pills are the main controllable EXP income. All colors share "
        "ONE daily attempt pool (the \"Daily pill attempts\" input) — using a blue "
        "costs the same attempt a gold would, so always consume your highest color "
        "first. Red (Mythic) pills refined by the Starsea Vase are exempt from the "
        "limit. A pill's tooltip shows its total EXP with your bonus in parentheses; "
        "the calculator works with base values (total − bonus).</p>")
    pills += table(
        "Cultivation Pill base EXP (per rank)",
        ["Rank", "Rare (Blue)", "Epic (Purple)", "Legendary (Gold)", "Mythic (Red)"],
        [[rk, f"{b:,}", f"{p:,}", f"{g:,}", f"{m:,}"]
         for rk, (g, p, b, m) in d["pill_xp"].items()],
        "Base values before bonuses (the in-game tooltip shows "
        "total with the bonus in parentheses: base = total − bonus). All pill-effect "
        "bonuses add as percentage points and multiply the base once.")
    pills += table(
        "Cultivation Pill Effect sources",
        ["Source", "Bonus"],
        _vault_bonus_rows(shelf_catalog, {"pill_effect": "%"}),
        "All sources stack additively. Record what you own in the Vault and "
        "the pill-effect rows fill themselves; anything the Vault does not "
        "carry (event buffs, Dao Ancestor treasures) can be typed in as a "
        "custom row. Quality-specific bonuses (Star Marks, Daozu treasures, "
        "Lotus Throne) apply only to pills of that color — enter those in "
        "the Star Marks fields.")

    # ---- Curios --------------------------------------------------------
    curios = "<h2>Curios</h2>"
    curios += (
        "<p>Curios (the Treasury half of the Vault) are passive relics. Most "
        "give combat stats, but a handful help cultivation directly — pill "
        "effect, Respira, and abode aura — and those are the ones worth "
        "chasing for breakthrough speed.</p>"
        "<a name='acquisition'></a><h3>They come from random draws</h3>"
        "<p>You don't buy a specific curio. New curios and the shards that "
        "star them up come from draws, so a particular curio landing is luck, "
        "not a plan. That's why the Advisor lists curios separately as "
        "\"worth pulling for\" rather than mixing them into the plannable "
        "steps — it tells you which curio, if you drew it, would save the "
        "most time, without pretending you can just go get it.</p>"
        "<a name='starup'></a><h3>Stars and upgrades</h3>"
        "<p>A curio's cultivation bonus grows two ways. <b>Upgrade level</b> "
        "raises the base value in small steps; <b>stars</b> add a scalar on "
        "top (shown in game as \"Increases Curio Passive Stats\"). Stars run "
        "0 to 5 and then <b>Awaken</b>. For a percentage cultivation bonus "
        "the two add in percentage points — e.g. Yang Spirit Jade at 4 stars, "
        "upgrade 3 reads 3.2% (1.6 from the upgrade + 1.6 from the star "
        "scalar). Record the star and upgrade in the Vault and the pill / "
        "Respira fields fill themselves.</p>"
        "<p>A few cultivation curios are <b>Special</b> — the Spirit Seal "
        "set, for instance — and can't be starred or upgraded; they give "
        "one fixed bonus.</p>")
    curios += table(
        "Cultivation curios",
        ["Curio", "What it gives"],
        _curio_bonus_rows(shelf_catalog),
        "Set stars and upgrade levels in the Vault's Treasury; only these "
        "curios feed the calculator. Abode-aura curios are already inside "
        "your entered Abode Aura reading — they're listed so you know which "
        "ones to keep.")

    # ---- Artifacts & Gems ----------------------------------------------
    artifacts = "<h2>Artifacts &amp; Gems</h2>"
    artifacts += (
        "<h3>Creation Artifacts</h3>"
        "<p>Three artifacts convert a shared resource — <b>Artifact Energy</b> (each "
        "artifact has its own pool) — into extra cultivation EXP:</p>"
        "<ul><li><b>Starsea Vase</b>: refines any cultivation pill into a Mythic (red) "
        "pill worth far more EXP. Reds don't count against the daily attempt pool, so "
        "the Vase is effectively free extra pills every day — keep it fed.</li>"
        "<li><b>Dual-Star Mirror</b>: duplicates owned items, including your red pills "
        "(only reds whose EXP bonus matches your Vase's unlocked tiers). Its copies "
        "stack on top of Vase production.</li>"
        "<li><b>Timereversal Pearl</b>: converts energy into auxiliary-path EXP. Its "
        "per-use EXP scales with your own cultivation speed bonuses, so re-read its "
        "tooltip after aura upgrades.</li></ul>"
        "<p>Energy regenerates over time and stops at the cap, so idle energy above "
        "cap is wasted — spend before it fills. The paid daily charge (30 "
        "Fateum/Destium for +100) is usually the cheapest EXP a payer can buy; the "
        "calculator has a per-artifact checkbox for whether you use it.</p>")
    artifacts += table(
        "Creation Artifact energy",
        ["Property", "Value"],
        [["Regeneration", "1 energy / 15 min at 0★ (faster per star)"],
         ["Cap", "200 at 0★ (rises with stars); regen stops at cap"],
         ["Daily charge", "+100 energy for 30 Fateum/Destium, once per day per artifact"],
         ["Mirror copy cost", "200 base; −5% (1★), −10% (3★), −10% skin — discounts add together"],
         ["Mirror 5★", "15% chance of an extra copy per Duplication"],
         ["Pearl use cost", "10 energy; star/skin discounts add (skin −10%)"],
         ["Pearl EXP bonus", "+20% from 1★ (does not grow at higher stars)"]])
    artifacts += table(
        "Starsea Vase — refine energy cost (per pill rank)",
        ["Rank", "Standard Energy"],
        [[rk, d["vase_energy_cost"].get(rk, 100)] for rk in d["pill_xp"]],
        "Refining an Epic pill costs −5% energy, a Legendary −20%. Star effects: "
        "+10% EXP on refined pills (1★), +20% (3★), 15% chance to consume no energy (5★). "
        "Skin: +8% EXP. Refined reds don't count toward daily pill attempts.")
    artifacts += (
        "<h3>Aura Gems</h3>"
        "<p>An equipped Aura Gem stores aura while you're away and releases it, acting "
        "as a flat percentage speed-up on cultivation. The calculator (following "
        "Donk's sheet) models it as a constant parallel bonus by rarity:</p>")
    artifacts += table(
        "Aura Gem speed bonus",
        ["Rarity", "Bonus"],
        [[k, f"+{v * 100:.0f}%"] for k, v in d["gem_bonus"].items() if k != "None"])
    artifacts += (
        "<p><b>The Aura Gem is claimable storage</b>: it accrues gem% of your "
        "cultivation speed up to a cap (18-32 hours' worth depending on rarity). "
        "Claim before it caps or the excess is lost; the calculator assumes you "
        "always claim in time.</p>")

    pills += (
        "<h3>Respira</h3>"
        "<p>Respira (the daily cultivation exercise) grants a burst of Cultivation "
        "EXP from a limited number of daily attempts, resetting on Stage/half-step "
        "breakthrough. Each attempt rolls a crit multiplier — <b>×1 / ×2 / ×5 / ×10</b> "
        "at 60% / 30% / 8% / 2% — averaging <b>×1.8</b>. Enter "
        "your daily attempt limit and the base (non-crit) EXP per attempt; the ×1.8 "
        "average is applied for you, so daily Respira EXP ≈ attempts × base × 1.8. "
        "Temporary event attempts go in the separate one-off field.</p>"
        "<p><b>How to read the base EXP per attempt:</b> perform several Respira and "
        "watch the Cultivation EXP each one grants. Most attempts give the same "
        "smaller number — that is the <b>base</b> (non-crit) value to enter. Now and "
        "then an attempt gives 2×, 5×, or 10× that (a crit) — ignore those; the app "
        "already accounts for crits via the ×1.8 average. So enter the smallest / "
        "most common EXP you see, not a big crit result.</p>")
    pills += table(
        "Respira bonus sources",
        ["Source", "Effect"],
        _vault_bonus_rows(shelf_catalog,
                          {"respira_attempts": " attempt/day",
                           "respira_effect": "% Respira Effect"}),
        "Record these in the Vault; the Attempts / day and Respira Effect "
        "books fields fill themselves.")
    pills += (
        "<h3>Flat EXP — why pills matter less each grade</h3>"
        "<p><b>Pills and Respira grant flat EXP.</b> The percentage shown on the pill "
        "panel is relative to your current grade's EXP, so the same pills matter less "
        "as grades grow — pill-heavy accounts slow down more than naive projections "
        "suggest.</p>"
        "<p><b>Daily pills and Respira reset</b> on a major breakthrough/ascension — "
        "spend them before breaking through.</p>")

    # ---- Elixirs & Stat Pills (permanent consumables) --------------------
    # Verified 2026-07-10 from in-game screens (formula panel, elixir
    # tooltips, Compare BR "Pill and Elixir Details") — see repo notes.
    elixirs = "<h2>Elixirs &amp; Stat Pills</h2>"
    elixirs += (
        "<p>Beyond the daily cultivation pills, the game has <b>permanent</b> "
        "consumables. The word \"pill\" is overloaded in-game — three different "
        "things carry it:</p>"
        "<ul>"
        "<li><b>Cultivation pills</b> (cultivation screen, Pill tab): daily-limited "
        "EXP items — covered on the Pills &amp; Respira page. Daily attempts reset "
        "on a Main Stage breakthrough.</li>"
        "<li><b>Stat pills</b> (crafted via alchemy formulas, <b>used from the "
        "backpack</b>): flat permanent combat stats with a fixed lifetime use "
        "cap.</li>"
        "<li><b>Aux-path \"pills\"</b> (cultivation screen, Elixir tab — e.g. "
        "Hundred Fortunes Pill): cultivation EXP for your auxiliary path — "
        "mechanically elixirs.</li>"
        "</ul>"
        "<p><b>Elixirs</b> are the other permanent family: reward/shop items "
        "granting either combat stats (\"stat elixirs\") or cultivation EXP "
        "(\"EXP elixirs\"), both with diminishing returns the more of an item "
        "you consume. Both families are covered below.</p>"

        "<h3>Stat pills (alchemy)</h3>"
        "<p>Crafted from per-rank formulas (e.g. Windride = +10 P.EVA, Agility = "
        "+10 M.EVA). Every use grants the full listed stat — no decay — until the "
        "pill's <b>permanent use cap</b> for that rank is exhausted: "
        "<b>R1 20 · R2 40 · R3+ 50</b> uses. The counter is on the pill itself, "
        "so pills from shops or rewards spend the same budget as crafted ones, "
        "and it ticks even if you never learn the formula.</p>"
        "<p>Each <b>major realm breakthrough unlocks the next rank's 50 uses</b> "
        "per pill line rather than raising old caps — the Compare BR panel's "
        "\"Stat Pill Use Limit\" reads 320 at Nascent Soul, 420 at Incarnation, "
        "520 at Voidbreak (two evasion pill lines × the unlocked ranks).</p>"
        "<p><b>Practical read:</b> there is no way to waste a stat pill — every "
        "use pays the same flat amount and the budget refills only by reaching "
        "new realms — so take them as you get them. The only real decision is "
        "whether the crafting cost is worth it, and that gets steep at high "
        "ranks.</p>")
    elixirs += table(
        "Stat pill crafting cost (one craft)",
        ["Rank", "Herb", "Spiritium", "Formula source"],
        [["R1", "Greenspirit ×1", "500", "Market"],
         ["R2", "Miragium ×2", "5,000", "Sect Library"],
         ["R3", "Spirit Marrow ×3", "24,000", "Sect Library"],
         ["R4", "Loftine ×4", "80,000", "Sect Library"],
         ["R5", "Udumbara ×6", "300,000", "Sect Library"]],
        "All formulas craft at Max Quality. A fully capped +10 line across "
        "R1–R5 is worth (20+40+50+50+50) × 10 = 2,100 of the stat.")
    elixirs += (
        "<a name='tolerance'></a><h3>Stat elixirs (tolerance ladder)</h3>"
        "<p>Stat elixirs (Yijing, Celeszure, Gouchen, dews and fruits…) grant "
        "permanent combat stats — but with <b>diminishing returns</b>. Each "
        "item tracks how many you've consumed over your character's lifetime "
        "(the \"Used\" number on its panel), and the <b>effect ratio</b> steps "
        "down through fixed tiers as that count grows: the first few pay 150% "
        "of the listed stat, later ones less and less, until \"Pill limit "
        "reached; it no longer takes effect\" ends the item for good. The "
        "<code>a/b</code> counter on the panel is your position inside the "
        "<i>current</i> tier, not the overall cap.</p>"
        "<p>The ladder is a property of the item, <b>not the character</b>: "
        "a 3R elixir steps through the same tiers no matter whose realm "
        "consumes it.</p>"
        "<p><b>Practical read:</b> there is no timing play — an elixir is "
        "worth the same whenever you take it, so use them as they arrive. "
        "When buying, remember the posted stat is the <i>base</i>: your next "
        "pill actually pays base × your current ratio, so an item deep into "
        "its ladder is worth a fraction of its face value.</p>")
    elixirs += table(
        "Stat elixir effect-ratio tiers (uses per tier)",
        ["Effect ratio", "3R", "4R", "5R"],
        [["150%", "10", "10", "10"],
         ["120%", "—", "20", "20"],
         ["100%", "20", "30", "40"],
         ["80%", "50", "—", "—"],
         ["70%", "?", "60", "?"],
         ["50% / 30% / 20%", "?", "?", "?"]],
        "\"?\" marks tiers whose exact widths aren't known "
        "yet; the in-game tooltip says the ladder continues 70 → 50 → 30 → "
        "20% before the hard cap. Cultivation-EXP elixirs use different "
        "(wider) tiers — their first tier is 20 uses, not 10.")
    elixirs += (
        "<h3>Elixirs and paths</h3>"
        "<p>Cultivation-EXP elixirs are path-specific: the Vigor ladder feeds "
        "Literatia, Fatebreaker Ghostia, Emerald Magicka, Nonagen Corporia, "
        "Cloudcut Grit Swordia; Spiritual Nectar feeds your current path and "
        "Hundred Fortunes / Pyroessence your auxiliary path. A red requirement "
        "line means the realm requirement isn't met on that item's path. On a "
        "Path Switch, each elixir's remaining quantity, use attempts and "
        "efficiency swap along with the paths.</p>"

        "<a name='expelixirs'></a><h3>Getting EXP elixirs</h3>"
        "<p>In normal play, EXP elixirs only trickle in — small amounts from "
        "various sources, often priced in Fateum, which is scarce enough that "
        "an F2P player should generally prioritize spending it on the garden "
        "first — it feeds the law system that starts at Voidbreak (see "
        "<a href='app://guide/voidbreak'>Guide → Voidbreak+</a>). The exception: <b>breaking through to a new realm offers three "
        "real-money elixir packs</b>, and for anyone optimizing money spent "
        "these packs are among the best value in the game — the elixirs' "
        "150%/120% early tiers make each realm's batch worth the most right "
        "when you buy it.</p>"

        "<h3>The Sense stat</h3>"
        "<p>Sense (internally <code>spirit_max</code>) currently does one "
        "thing: it gates how many treasures you can carry — Fabao slots "
        "unlock at Sense 1/7/13/16/19/22 and Gubao slots at 15/18/21. It "
        "grows by about 1 per realm level, and the game's own tooltip says "
        "further uses are planned. It is not part of any damage or "
        "cultivation formula the client exposes.</p>")

    # ---- Myrimon & Extractor ---------------------------------------------
    myrimon = "<h2>Myrimon &amp; Extractor</h2>"
    myrimon += (
        "<a name='fruits'></a><h3>Myrimon Fruits</h3>"
        "<p>Fruits processed through the Aura Extractor grant a one-time EXP payout "
        "(the calculator credits it against the earliest remaining EXP). Payout scales "
        "with fruit rank, your Culti/Quality/Gush levels, and extractor rarity — higher "
        "quality rolls multiply the base substantially, so extractor upgrades compound.</p>"
        "<p><b style='color:" + acc['bad'] + "'>Advisory</b> — tiering the extractor up requires "
        "consuming a number of fruits, so <b>spend only the minimum needed for each "
        "tier-up and stockpile everything else until the extractor is maxed</b>. Every "
        "fruit eaten early forfeits the better quality/EXP multipliers it would have "
        "received at higher extractor tiers — the same hoard is worth substantially "
        "more processed at max rarity. Note also that the extractor resets on a realm "
        "ascension (see Mechanics notes below), so burn the stockpile before "
        "ascending, and only after the extractor is upgraded.</p>"
        "<p>Fruits also lose 50% of their EXP once the realm's <b>timegate</b> passes — "
        "eat the stockpile before the timegate, not merely before your own breakthrough. "
        "Extractor leveling priority: Quality → "
        "Cultivation → Gush → High Rank, taking High Rank only after the others are "
        "maxed. Myrimon unlocks at Virtuoso; the Mortal World (Virtuoso through "
        "Incarnation) shares one fruit/extractor tier, and each World afterwards gets "
        "its own — Spiritual at Voidbreak, Immortal at Celestial. Myrimon "
        "uses stack (after the first week's event) — save them for Sunday or until you "
        "cross the next BR requirement. Each week's event runs Wednesday through the "
        "following Tuesday, with one free run each on Wednesday, Friday and Sunday "
        "(3 total), plus up to 2 purchasable <b>Myrimon Tokens</b> from the cash shop, "
        "each worth +1 run in the week you redeem it (5 runs max in a week if both are "
        "bought and used). Tokens themselves are inventory items — buy them freely and "
        "hold them unredeemed as long as you like. Near a realm ascension, don't redeem "
        "saved tokens for a few extra of the current realm's fruit; hold them and "
        "redeem right after ascending for the new realm's higher-tier fruit "
        "instead.</p>"
        "<a name='verified'></a><h3>Mechanics notes</h3><ul>"
        "<li><b>Fruit ranks map to realm bands</b> (R3 covers Nascent-Voidbreak; R6 "
        "starts the Spiritual world; R12 the Immortal world) — R4/R5 don't exist.</li>"
        "<li><b>Extractor tracks</b>: Quality raises the quality-roll odds, the "
        "Cultivation Bonus track gives +4% orb EXP per level, and the Gush track "
        "raises the gush multiplier.</li>"
        "<li><b>Extractor rarity</b>: each rarity rank unlocks +20% orb EXP for its "
        "tier (Uncommon through Mythic); when the extractor's rank matches your Stage "
        "(server's highest), base fruit EXP +50%.</li>"
        "<li><b>Gush</b>: base multiplier 150%, raised by the Gush track; a gush is "
        "guaranteed within 6 fruits of the last one (soft pity — any gush, random or "
        "guaranteed, resets the counter), on top of the displayed random rate.</li>"
        "<li><b>Aura Extractor resets</b> to Common quality / bonus level 0 when you "
        "ascend to a new realm — stage breakthroughs within a realm (e.g. Nascent "
        "Soul → Incarnation) don't reset it — and leftover fruits of the previous "
        "realm are auto-consumed at the pre-upgrade rates. Finish upgrading the "
        "extractor <b>before</b> burning a stockpile, and burn the stockpile before "
        "ascending.</li></ul>")

    # ---- Combat & Gear ---------------------------------------------------
    # Sourced from decompiled client config tables (attrib, equipment,
    # equip_ten_lv_affix, affix_mark_rank, equip_suit, level_equip).
    # Combat itself is resolved server-side; these are the client-visible rules.
    combat = "<h2>Combat Stats &amp; Gear</h2>"
    combat += (
        "<p>This page is about fighting, not cultivating — nothing here changes "
        "your breakthrough time. It's a plain-language tour of what your stats "
        "mean and what all the gear upgrade buttons actually do.</p>"

        "<h3>Your stats, in short</h3>"
        "<p>Everything starts from five <b>base stats</b>. Each point you gain "
        "quietly converts into the combat numbers you see on your sheet:</p>")
    combat += table(
        "What each base stat gives you",
        ["Base stat", "Each point gives"],
        [("Physique", "+4 Physical ATK, +2 Physical DEF"),
         ("Psyche", "+4 Magical ATK, +2 Magical DEF"),
         ("STR", "+1000 Max HP, +3 Physical DEF"),
         ("CON", "+1000 Max MP, +3 Magical DEF"),
         ("Agility", "+3 Dodge, +3 Hit Rate (helps both damage types)")])
    combat += (
        "<p>Notice the pattern: every combat stat has a <b>physical</b> and a "
        "<b>magical</b> version. Your path fights with one or the other, so "
        "Physique-type stats matter to a body cultivator the way Psyche-type "
        "stats matter to a mage — the other half mostly just pads your defense.</p>"
        "<p>You'll also see PvP-only lines like \"DMG dealt to Taoists +x%\" — "
        "those don't come from base stats at all; they come from the gear "
        "systems below.</p>"

        "<h3>How crit works</h3>"
        "<p><b>Crit Chance</b> is shown as a flat number, not a percent. The "
        "game converts it to a real chance <i>relative to your realm</i> — the "
        "same flat crit that felt great at Foundation is worth a smaller "
        "percentage by Nascent Soul. To see your actual percentage, tap the "
        "crit stat in-game: its tooltip shows your current crit rate for your "
        "realm. (The exact conversion curve lives on the server, so no formula "
        "here — the tooltip is the source of truth.)</p>"
        "<p>The rest of the crit family:</p>"
        "<ul>"
        "<li><b>Crit DMG</b>: a crit deals <b>150%</b> damage baseline "
        "(rounded down); Crit DMG bonuses raise that multiplier.</li>"
        "<li><b>Crit Defense</b>: each +1% cuts an attacker's crit multiplier "
        "by 1% against you.</li>"
        "<li><b>Crit Resistance</b>: lowers the <i>chance</i> of being crit "
        "in the first place.</li>"
        "</ul>"

        "<h3>Gear in one paragraph</h3>"
        "<p>You wear a weapon, armor and an accessory, plus <b>Relics</b> as "
        "their own separate category. Rarity climbs white → green → blue → "
        "purple → yellow. When an item is forged its stats roll within a "
        "range — so two copies of the same item can differ, and a well-rolled "
        "piece is worth keeping.</p>"

        "<h3>Leveling gear (Augmentation)</h3>"
        "<p>Pouring materials into a piece does three things:</p>"
        "<ul>"
        "<li><b>Every level:</b> its base stats grow a little. Steady, nothing "
        "to time.</li>"
        "<li><b>Every 10th level:</b> it unlocks an extra bonus line. Which "
        "line is fixed per item — one weapon always grows a Crit DMG line, "
        "another an ATK line.</li>"
        "<li><b>Resonance:</b> a bonus across your whole equipped set that "
        "looks at the level of your <i>lowest</i> piece. Push everything past "
        "the next threshold together and you unlock PvP bonuses like \"Relic "
        "DMG to Taoists +x%\".</li>"
        "</ul>"
        "<p><b>Practical takeaway:</b> level your gear evenly. One maxed sword "
        "does less for you than eight pieces raised together, because "
        "Resonance only counts your weakest piece.</p>"
        "<p><b>Nothing is locked in:</b> the forge's <b>Reset</b> tab lets "
        "you reset any item, returning <b>100% of the materials</b> poured "
        "into it — and the base item itself — so you can redistribute "
        "upgrade materials among different pieces (say, to even out levels "
        "for Resonance) without losing your investment.</p>"

        "<h3>Carvings (the enchant lines)</h3>"
        "<p>From Foundation on, gear can hold <b>Carvings</b> — bonus stat "
        "lines you level separately by feeding them Carving EXP items. Slots "
        "unlock as the item's augment level rises, and a carving that keeps "
        "leveling steps up through its own rarity colors, getting stronger at "
        "each step. Carvings have their own Resonance too, again counted "
        "across everything you're wearing.</p>"

        "<h3>Gear sets</h3>"
        "<p>Each realm has a gear set: wear enough current-realm pieces and "
        "the set bonus turns on, granting those PvP damage/reduction lines "
        "and raising caps like how far carvings can go. The catch: <b>when "
        "you break through to a new realm, the old set bonus switches off</b> "
        "— you build it back up with the new realm's gear. Budget for that "
        "rather than being surprised by it.</p>"

        "<h3>Immortactic gear</h3>"
        "<p>A separate side-track of equipment with its own levels and stars. "
        "Its stats grow in 2-level steps, with a Crit DMG boost every 20th "
        "level.</p>"

        "<h3>Affix priorities</h3>"
        "<p>Which rolled bonus lines to chase on gear and relics has "
        "its own page now — see the <a href='app://ref/affixes'>"
        "Affixes tab</a> for the full tier list, the named rolls and "
        "their ranges, and the paralysis/penetration math.</p>"

        "<h3>About the missing numbers</h3>"
        "<p>The rules and thresholds above are exact. The "
        "<i>values</i> — what a given 10-level bonus or resonance rank "
        "grants — are decided server-side and vary by item and realm, so this "
        "page doesn't guess at them. Where a number isn't listed, read it as "
        "\"unknown\", not \"zero\". For the exact per-point math the game does "
        "expose, see the <a href='app://ref/advanced#perpoint'>Advanced tab</a>.</p>")

    # ---- Affixes ---------------------------------------------------------
    # Tier ranking is a widely circulated community list (opinion);
    # per-point math and caps are verified from the decompiled client
    # configs — see docs/knowledge/combat-mechanics.md for sources.
    affixes = "<h2>Gear &amp; Relic Affixes</h2>"
    affixes += (
        "<p>Affixes are the rolled bonus lines on forged gear and "
        "relics. Which item drops is luck; which <i>lines</i> it rolls "
        "is what separates a keeper from forge fodder. The tier "
        "ranking below is subjective; the caps and "
        "per-point math are exact.</p>"
        "<p>Two caps drive most of the ranking: <b>crit rate is "
        "hard-capped at 50%</b> and <b>hit is capped at 99%</b> (with "
        "a 25% floor — nobody can be evade-tanked below a 1-in-4 "
        "chance to hit). Capped stats are dead value past the cap.</p>"

        "<h3>T0 — always chase</h3>")
    affixes += table(
        "T0 affixes",
        ["Affix", "Effect", "Appears on"],
        [("Wonder", "+30–46% ALL base stats", "gear"),
         ("Blade Rage", "+20–28% P.ATK", "swords, bracelets"),
         ("Spellforge", "+20–28% M.ATK", "fans, pendants"),
         ("Spirit", "+9–21% relic cooldown", "relics"),
         ("Ulti Sharp / Ulti Occult", "+15–21% P./M. ATK bonus on "
          "ultimates", "gear"),
         ("Bladeglow", "+11–15.4% flying-sword attack frequency",
          "longswords, greatswords"),
         ("Ether Veil", "+15–25.2% relic shield limit",
          "trigrams, pearls"),
         ("Infinite Edge", "+15–25.2% relic damage limit",
          "damaging relics")])
    affixes += (
        "<p>Base-stat % multipliers are the strongest lines in the "
        "game. Cast speed and the limit breakers matter most from "
        "Voidbreak on, where relic damage and shields cap easily.</p>"

        "<h3>T1 — good</h3>")
    affixes += table(
        "T1 affixes",
        ["Affix", "Effect", "Appears on"],
        [("Annihilation", "+7.2–16.8% crit multiplier (gear); "
          "+18–42% relic crit multiplier (relics)", "gear, relics"),
         ("Pursuit", "flat crit damage (stage-scaled; higher roll on "
          "relics)", "gear, relics"),
         ("Fatal", "flat crit chance (relic roll ≈4× the gear roll); "
          "dead value past the 50% cap", "gear, relics"),
         ("Sharp / Occult", "flat P./M. ATK on gear, flat P./M. DMG "
          "on relics", "gear, relics"),
         ("Corporia / Magicka", "flat Physique / Manipulation "
          "(+4 ATK, +2 DEF per point)", "gear"),
         ("Nimble", "flat Agility (+3 Hit and +3 EVA, both damage "
          "types, per point)", "gear"),
         ("Longevity / Vitality", "flat HP / MP", "gear")])
    affixes += (
        "<p><b>Match the line to your path.</b> Sharp on a magical "
        "path — or Occult on a physical one — is trash <i>on gear</i>; "
        "on relics the mismatch penalty doesn't apply. Corporia and "
        "Magicka follow the same rule.</p>"

        "<h3>T2 — situational</h3>")
    affixes += table(
        "T2 affixes",
        ["Affix", "Effect", "Appears on"],
        [("Conflict", "+9–21% relic status duration (T3 on relics "
          "with no status to extend)", "relics"),
         ("Precise / Focus", "flat P./M. Hit (relic roll ≈4× the "
          "gear roll)", "gear, relics"),
         ("Insight / Agile", "flat P./M. EVA", "gear"),
         ("Stalwart / Refuge", "flat P./M. DEF", "gear"),
         ("Guardian", "flat crit resistance", "gear"),
         ("Soulclaim / Gloom", "paralysis chance / duration boost",
          "weapons"),
         ("Tranquil / Serene", "paralysis chance / duration resist",
          "armor")])
    affixes += (
        "<p>Defense lines are weak because Penetration strips up to "
        "50% of defense when the attacker wins the contested check — "
        "see the <a href='app://ref/advanced#penblock'>Advanced tab</a>.</p>"
        "<p><b>Paralysis math:</b> "
        "boost and resist cancel 1:1; each leftover point shifts proc "
        "chance by 0.2% (enhance capped at +100%, resist at −50%) and "
        "duration by 0.5% — but the duration <i>boost</i> caps at "
        "<b>+25%</b> (only the resist side reaches −50%), so "
        "duration-boost lines saturate at 50 points of advantage.</p>"

        "<h3>T3 — avoid</h3>")
    affixes += table(
        "T3 affixes",
        ["Affix", "Effect", "Appears on"],
        [("Bone / Tolerate", "% HP / MP regen — only ticks out of "
          "combat, which never happens in duels or the Voidgate",
          "gear"),
         ("Bladesoul", "+11–15.4% chance to keep flying swords when "
          "controlled — resummoning is near-instant anyway",
          "longswords, greatswords")])
    affixes += (
        "<h3>Practical takeaway</h3>"
        "<p>Prioritize T0/T1 lines on weapons and pendants first. "
        "Reroll toward base-stat % (Wonder / Blade Rage / Spellforge) "
        "and relic cast speed — those two families define endgame "
        "power. Tier placement is subjective; the numbers and "
        "caps quoted are exact.</p>")

    # ---- World Systems ---------------------------------------------------
    # System explainers assembled from the client's own tooltip/description
    # strings (i18n dump) plus user-verified play notes; numbers that are
    # server-side balance data are omitted rather than guessed.
    systems = "<h2>World Systems</h2>"
    systems += (
        "<p>Short explainers for the systems the rest of this app keeps "
        "mentioning. Where a number is server-side, it's omitted rather "
        "than guessed.</p>"

        "<h3>Currencies</h3>"
        "<ul>"
        "<li><b>Spiritium</b> — \"the basic currency in the cultivation "
        "world. Mainly obtained in Realms. Used in Market, Alchemy, Forge "
        "Room and other daily matters.\" Realm idle production scales with "
        "your Demon Spire progress.</li>"
        "<li><b>Fateum</b> — the premium-adjacent currency, \"obtained "
        "from gameplay or by exchanging Destium\"; spent in the "
        "Fatevillion shop, on Path Switches, refreshes, and artifact "
        "daily charges.</li>"
        "<li><b>Destium</b> — purchase-only; converts to Fateum 1:1 "
        "(irreversible). Also used in the Auction House.</li>"
        "</ul>"
        "<p>Two more shop currencies worth knowing: <b>Revealstone</b> "
        "(Seeker Shop) and <b>Citrine</b> + <b>Sect Contribution</b> "
        "(Sect Library) — see the shop guide below.</p>"
        "<p><b>Spending guidance:</b> Fateum is the scarce one for F2P — "
        "prioritize the garden (law fruits) once laws unlock at Voidbreak, "
        "ahead of elixirs and convenience refreshes. Payers get the most "
        "per unit from artifact daily charges and the realm-breakthrough "
        "elixir packs.</p>"

        "<h3>Shop-by-shop buying guide</h3>"
        "<p>Widely recommended priorities:</p>"
        "<ul>"
        "<li><b>Market</b> (Spiritium): Demonroot (pet skills), Kunlun "
        "Jade (backpack space), Monster Core, Rare+ cultivation pills, "
        "Atlases, stat elixirs. Mechanics: it refreshes every 3 hours, "
        "you get 10 manual refreshes/day (each costing more Spiritium), "
        "and every 5th refresh guarantees an Epic item.</li>"
        "<li><b>Seeker Shop</b> (Revealstone): <b>buy nothing before "
        "Voidbreak.</b> Nature Mantras there cost ~200 each and you'll "
        "want 3,300+ of them — hundreds of thousands of Revealstone — "
        "and F2P sources are scarce, so every stone spent early is a "
        "mantra missing later.</li>"
        "<li><b>Sect Library</b> (Citrine / Sect Contribution): Ability "
        "Manuscripts first — skipping them slows ability progression "
        "badly — then blueprints and alchemy formulas. Citrine comes "
        "from mining spiritual veins (capped ~2 h/day + 7 h/week — "
        "mine daily, prioritize the highest vein tier).</li>"
        "<li><b>Fatevillion</b> (Fateum): the <b>Cultivation Bag</b> is "
        "the standout must-buy; cultivation elixirs are worth it for "
        "F2P while your tolerance ratio is still above ~120%; Demonlure "
        "for realm farming; and anything at a 70% discount deserves a "
        "look. <b>The shop resets on every breakthrough — minor ones "
        "included</b> (Connection 9→10 counts), so check it before "
        "each one.</li>"
        "</ul>"
        "<p><b>Cheap daily Fateum habits</b>: the first daily Technique "
        "Points purchase (100 points for 50 Fateum) and the second "
        "daily sect Construct (the first is free, the second costs 50) "
        "are both efficient. Refreshing unclaimed Bounty Quests below "
        "Rare and Sect Tasks below C-rating once a day upgrades them "
        "guaranteed.</p>"

        "<a name='garden'></a><h3>Garden &amp; Elemental Laws</h3>"
        "<p>The <b>garden</b> grows seeds into rewards: each seed takes up "
        "plot slots and matures over time; you get a limited number of "
        "daily <b>watering</b> attempts to speed growth (the first is free "
        "each day — don't miss it), and growth can also be rushed with "
        "energy + Spiritium. Seeds yield alchemy materials, technique "
        "seeds, and — the headline crop — <b>Law Fruits</b>.</p>"
        "<p><b>Elemental Laws</b> (unlock at Voidbreak; five elements — "
        "Metal, Wood, Water, Fire, Earth) are a long-term damage system. "
        "<b>Law Points</b> accrue naturally over time, faster as a law "
        "levels, and each element's own generation rate <b>doubles at "
        "milestone levels</b> — 50, 150, 250, 350… every 100 levels, "
        "always ending in 50. Law Points are spent to upgrade laws once "
        "the Stage requirement is met, and also feed a separate "
        "<b>Cosmic Laws</b> system from the <i>same shared pool</i> — "
        "leveling Elemental Laws first raises income for both. Every "
        "100M Law Points auto-converts to a <b>Tao Motto</b>.</p>"
        "<p><b>Law Fruit</b> is what actually feeds Elemental Laws, grown "
        "in the garden: four natural tiers — Green (4h grow), Blue (16h), "
        "Purple (40h), Yellow (88h) — plus a non-grown <b>Red</b> tier "
        "produced by the <b>Shears</b> artifact. <b>Blitz</b> converts a "
        "fruit into hours of law-learning progress at whichever element's "
        "<i>current</i> rate it's applied to — Green 1h, Blue 3h, Purple "
        "6h, Yellow 12h, Red 14h — capped at <b>120 Blitz-hours/day</b> "
        "(Red is exempt from the cap). Which tier is actually best "
        "depends on the bottleneck: Green wins per grow-hour (best when "
        "garden space is the limit), Yellow wins per seed (best when seed "
        "supply is the limit) — the opposite ranking, so it's worth "
        "knowing which one actually binds before following either rule "
        "blindly.</p>"
        "<p><b>Garden capacity</b>: fully unlocked is a 6×6 grid (36 "
        "cells); Law Fruit and Ploughwood seeds both take a 3-cell "
        "footprint, so a full grid holds 12 Law Fruit slots — a natural "
        "ceiling of 72 Blitz-hours/day at all-Green. The <b>Pot</b> "
        "artifact (a Creation Artifact — see Artifacts &amp; Gems) speeds "
        "growth (1 energy = 1 hour saved) and typically pushes that "
        "ceiling to roughly 108/day. <b>Garden slots not bought before "
        "reaching Voidbreak are permanently lost throughput</b> once Law "
        "Fruit becomes usable — there's no way to retroactively recover "
        "missed law levels — so fully unlocking the garden pre-Voidbreak "
        "is worth doing even though the same cells also serve Ploughwood "
        "and gear-crafting plants; the standard practice is to dedicate "
        "the whole thing to Law Fruit for roughly the first year.</p>"
        "<p><b>Law Suppression</b>: compare your total Elemental Law "
        "level (summed across all 5 elements) against an opponent's. "
        "Each level of advantage deals <b>+0.05% additional damage</b>, "
        "capping at <b>+30% at 600 levels ahead</b> — the bonus only "
        "applies while you're ahead, and going further past 600 doesn't "
        "add more.</p>"

        "<h3>Breakthrough failure</h3>"
        "<p>Stage breakthroughs <b>can fail</b>. A failure injures your "
        "<b>Primordial Soul</b>, which must be restored before you can "
        "attempt again — but \"cultivation won't be affected while "
        "injured\", so EXP keeps accruing. Pills \"increase breakthrough "
        "success rate\" (per their own tooltip).</p>"
        "<p><b>In practice</b> (mortal world): the Primordial Soul recovery "
        "is a wait — around an hour at early stages, but growing steeply "
        "with realm (a mid/late Incarnation failure has been observed at "
        "13 hours). Breakthrough pills shorten the wait; better pills "
        "shorten it more. Unless you're racing other players for your "
        "server's top spots, a failure costs you little — but in a race "
        "those hours are exactly what decides it. The calculator assumes "
        "first-try breakthroughs, so a failure streak pushes real dates "
        "past its estimates by the recovery waits.</p>"

        "<h3>Path Switch</h3>"
        "<p>Available from Foundation. Costs Fateum (rising 800 → 2400) "
        "with a <b>7-day cooldown</b>, and is blocked during competitive "
        "phases (ascendance events, brawl registrations, matchmaking, "
        "mining, server/sect transfer days). Your elixirs' state swaps "
        "with the paths: remaining quantity, use attempts, and tolerance "
        "efficiency all follow the path they belong to.</p>"

        "<h3>Sects</h3>"
        "<p>The social layer: joining one opens the <b>Sect Library</b> "
        "(pill formulas are exchanged here from R2 up), sect salary, "
        "tasks, treasure hunts, and the sect events (Meditation, Duel, "
        "Clash). Sect realm dominion gives practical buffs — +20% "
        "gathering speed on Spiritual Veins in the dominated realm.</p>"
        "<p><b>Picking one:</b> sects are guilds — join an active one and "
        "have fun; an active sect naturally progresses and its benefits "
        "follow. If you care about the PvP sect events, aim for a "
        "stronger active sect, but that's personal preference. Just "
        "don't sit sectless: the library and salary alone are worth "
        "it.</p>"

        "<a name='spire'></a><h3>Demon Spire</h3>"
        "<p>A floor-climbing combat tower. Your current floor pays "
        "<b>continuous hourly income</b> — Ability Knowledge (which "
        "levels your Abilities) and a bonus to Spiritium production in "
        "Realms — so every floor you clear is a permanent income raise. "
        "Climb it whenever your battle rating allows; it's one of the "
        "\"keep pushed at every stage\" systems.</p>"

        "<h3>Curios</h3>"
        "<p>Collectible items placed on the <b>Sacred Altar</b> (six "
        "slots). A slot boosts the passive stats of curios matching its "
        "type (HP, MP, P.ATK, M.ATK, P.DEF, M.DEF); percentage-stat "
        "curios don't benefit. Altar effects multiply with a curio's "
        "Star-Up. Rarities run Rare → Epic → Legendary → Mythic, from a "
        "draw system with guarantees. Several curios also carry the "
        "cultivation bonuses (pill effect, Respira) listed elsewhere in "
        "this reference.</p>"

        "<h3>Techniques</h3>"
        "<p>Unlockable passives: meet a technique's requirements to learn "
        "it, then spend <b>Technique Points</b> to tier it up — "
        "<b>special effects unlock at Tiers 3, 6 and 9</b> (higher-rank "
        "manuals continue at 12 and 15). The early-game "
        "picks the guide names (Longevity, Energy Unification, "
        "Rejuvenation) are examples of buying these tier effects at their "
        "cheapest; the same logic — tier breakpoints first — carries "
        "through the rest of the game.</p>"

        # Community-guide material (2026) from here down — priorities
        # and tier lists are consensus, not client data.
        "<h3>Technique roadmap (recommended priorities)</h3>"
        "<p>Quick per-rank picks below. The full rank-by-rank list "
        "through R21 — ratings and how deep to tier each manual — is "
        "on <a href='app://guide/techniques'>Guide → Techniques</a>:"
        "</p><ul>"
        "<li><b>R4</b>: Golden Core and Astrology; Focus's unlock "
        "too.</li>"
        "<li><b>R5</b>: Ninefall; Bloodization for its aura node.</li>"
        "<li><b>R6</b>: Yin's Grasp to Tier 9; Conflagration and "
        "Unbound Blade.</li>"
        "<li><b>R7</b>: Floral Essence and Purify &amp; Cleanse.</li>"
        "<li><b>R8</b>: Chroma and Astral Arcanum, plus your path's "
        "PvP pick.</li>"
        "<li><b>R9</b>: Harvest God Secret; Honored Origin for its "
        "aura nodes.</li>"
        "<li><b>R10</b>: everything — Immortal Ascension to Tier 12 for "
        "its +1 daily pill attempt (Tier 15 beyond that is stats-only).</li>"
        "<li><b>R11+</b>: each rank's law-speed manual first.</li>"
        "</ul>"
        "<p>For Technique Points, "
        "the recommended <b>Spirit World</b> strategy is three passes: "
        "clear what you can, come back stronger, finish later — rather "
        "than grinding one full clear early.</p>"

        "<h3>Curio priorities</h3>"
        "<ul><li>Value order: <b>abode/pill-bonus curios &gt; main-path "
        "ATK &gt; HP/MP</b>.</li>"
        "<li>Star up <b>Pen &amp; Block equally</b> — a Pen roughly "
        "1000 over the opponent's Block negates their defense.</li>"
        "<li>Get <b>everything to 2–3 stars minimum</b> before pushing "
        "any single curio deep.</li>"
        "<li>Daemonfae, Field and Reincarnation curios have their own "
        "niches — hold them rather than feeding them away.</li></ul>"

        "<h3>Fields (Perfection)</h3>"
        "<p>At Perfection you pick a Field; the usual mapping:</p>"
        "<ul><li><b>Solarium</b> — PvE-leaning and the usual F2P "
        "pick.</li>"
        "<li><b>Swordium</b> — the general-purpose choice.</li>"
        "<li><b>Darkmyth</b> — team-oriented; pick it with your sect, "
        "not solo.</li></ul>"
        "<p>Fields level and enlighten separately and have their own "
        "field-soul structure — details not covered here yet.</p>")

    # ---- Combat & Gear: Advanced ---------------------------------------
    # Expert-level internals recovered from the client's own stat
    # definitions and tooltip text; only mechanics the game states
    # explicitly are listed with numbers.
    advanced = "<h2>Cultivation Internals (Advanced)</h2>"
    advanced += (
        "<p>The exact numbers behind the calculator's model, for readers who "
        "want to check the math.</p>"
        "<h3>Respira crit distribution</h3>")
    advanced += table(
        "Per-attempt crit roll",
        ["Multiplier", "Chance"],
        [("×1", "60%"), ("×2", "30%"), ("×5", "8%"), ("×10", "2%")],
        "Mean multiplier 1.8 (the calculator's expected value), variance 2.56 "
        "per attempt — the main driver of the best/worst band on short "
        "horizons.")
    advanced += (
        "<h3>Fruit gush pity</h3>"
        "<p>The extractor's \"Gush guaranteed in Aura Orb x6\" counter is a "
        "<b>soft pity</b>: any gush — random or guaranteed — resets it. "
        "A gush is guaranteed within 6 fruits "
        "of the last one, not on every literal 6th, and the displayed gush "
        "chance is the per-fruit random rate with the pity layered on top. "
        "The calculator models this as "
        "a Markov chain over the miss streak (a fruit gushes at the "
        "displayed random rate, or with certainty after 5 straight misses) "
        "and computes the exact mean and variance of the gush count, which "
        "both raises the expected fruit XP at low Gush levels and narrows "
        "the fruit side of the band.</p>"
        "<h3>Strive tier tables</h3>"
        "<p>The live value is recomputed "
        "hourly on the server, so the calculator uses these only for the "
        "<i>shape</i> of the drop-off, anchored to your real Strive.</p>"
        "<ul>"
        "<li><b>Young servers</b> (world level &lt; 30): by major-realm gap "
        "to server #1 — 15% / 20% / 30% / 40% / 50% / 60% / 70% for gaps "
        "1–7.</li>"
        "<li><b>Mature servers</b> (world level ≥ 30): by minor-<i>level</i> "
        "gap — 70% at ≥60 levels, 30% at ≥50, 20% at ≥40 — plus an additive "
        "major-realm bonus of 30% (1 realm) or 50% (2+ realms). The 70% + "
        "50% sum is the ~120% cap seen on aged servers.</li>"
        "</ul>"
        "<h3>How the best/worst band is built</h3>"
        "<p>The band is a ~90% central interval (P5–P95): the calculator "
        "sums the variance of every random roll over the horizon (Respira "
        "crits, and the fruit gush count with the soft pity folded in — "
        "the pity truncates miss streaks, so fruits carry less variance "
        "than independent rolls would) and takes ±1.645 standard deviations "
        "around the mean. Because variance grows with the square root of "
        "the number of rolls, the band is widest in relative terms on "
        "short projections and tightens as the horizon grows.</p>"

        "<h2>Combat Internals (Advanced)</h2>"
        "<p>Exact combat mechanics. "
        "Damage resolution itself runs on the server, so treat this as the "
        "rulebook rather than a full damage calculator.</p>"

        "<h3>Flat stats and realm normalization</h3>"
        "<p>Crit Chance, Crit Resistance, Hit Rate and Dodge are stored as "
        "flat values and converted to effective percentages against a "
        "<i>realm-dependent standard</i>. This is why the game's own tooltip "
        "reports your \"crit rate at your current realm\": the flat number "
        "keeps its value, but each realm raises the standard it's measured "
        "against, deflating the percentage. The normalization curve is "
        "server-side; the in-game tooltip is the only exact readout.</p>"

        "<a name='perpoint'></a>"
        "<h3>Per-point mechanics</h3>")
    advanced += table(
        "Per-point coefficients and caps",
        ["Stat", "Effect per point", "Cap"],
        [("Penetration (phys/spell)", "−0.1% target defense per point, "
          "active only while your Penetration is higher than the "
          "target's", "—"),
         ("Block (phys/spell)", "while your Block is higher than the "
          "attacker's: 30% chance per hit to block, reducing damage "
          "0.1% per point of advantage", "—"),
         ("Stun duration enhance", "+0.5% stun duration", "+25%"),
         ("Stun duration resist", "−0.5% stun duration taken", "−50%"),
         ("Stun chance enhance", "+0.2% stun proc chance", "+100%"),
         ("Stun chance resist", "−0.2% stun proc chance", "−50%"),
         ("Elemental Rule level", "+0.05% damage per level of advantage "
          "over the target", "—")])
    advanced += (
        "<a name='penblock'></a><h3>Penetration and Block, exactly</h3>"
        "<p>These are <b>mirror-image contested stats</b>: each is compared "
        "against the <i>opponent's</i> copy of the same stat, and only the "
        "side with the higher value gets any effect at all.</p>"
        "<p><b>Penetration</b> (physical or spell): while your Penetration "
        "is higher than the target's, every point of it strips 0.1% off the "
        "target's defense against your hits — 500 pen means the target "
        "defends with 50% less DEF. Against someone with more Penetration "
        "than you, yours does <i>nothing</i>.</p>"
        "<p><b>Block</b> (physical or spell): while your Block is higher "
        "than the attacker's, each incoming hit has a <b>30% chance</b> to "
        "trigger a block, and a triggered block reduces that hit's damage "
        "by 0.1% per point of your <i>advantage</i> — the margin counts, "
        "not your raw total. On average it's worth 30% × 0.1% × margin per "
        "hit.</p>"
        "<p><b>Practical read:</b> both are stat-check races. Small "
        "investments do literally nothing against players who invest more — "
        "unlike defense or crit, which always contribute.</p>"

        "<h3>Stuns, exactly</h3>"
        "<p>Stun effects have two dials — <i>whether</i> the stun lands and "
        "<i>how long</i> it lasts — and each dial has an attacker stat and "
        "a defender stat fighting each other:</p>"
        "<ul>"
        "<li><b>Stun chance</b>: the attacker's enhance adds +0.2% proc "
        "chance per point (capped at +100%); the defender's resist removes "
        "0.2% per point (capped at −50%).</li>"
        "<li><b>Stun duration</b>: the attacker's enhance adds +0.5% "
        "duration per point (capped at +25%); the defender's resist "
        "removes 0.5% per point (capped at −50%).</li>"
        "</ul>"
        "<p>On top of these, three <i>flat percent</i> stats exist that the "
        "game explicitly says are \"not affected by any other effect\" — "
        "they apply after the contested math: a direct % increase to stun "
        "duration you inflict, a direct % reduction to the chance of being "
        "stunned (1% = exactly 1%), and a direct % reduction to stun "
        "duration you suffer.</p>"

        "<h3>Crit, exactly</h3>"
        "<ul>"
        "<li><b>Crit Chance</b> is flat and realm-normalized (see above); "
        "it applies to Ability and Relic hits and rises mainly from realm "
        "breakthroughs, weapons and accessories.</li>"
        "<li><b>Crit Resistance</b> is the defensive mirror: also flat and "
        "realm-normalized, it reduces the <i>chance</i> of being crit, and "
        "comes mainly from breakthroughs and armor. Its tooltip shows your "
        "effective resist % for your realm.</li>"
        "<li><b>Crit DMG</b>: a crit deals <b>150%</b> damage baseline, "
        "rounded <i>down</i>; Crit DMG% raises this multiplier. Soul-bound "
        "Talismans have their own <b>120%</b> crit base.</li>"
        "<li><b>Crit Additive DMG</b>: a flat damage amount added on top of "
        "a crit (base 0). It's added after the multiplier, not multiplied "
        "by it.</li>"
        "<li><b>Crit Block</b> trades exactly 1:1 — each 1% removes 1% from "
        "the attacker's crit <i>multiplier</i> against you (150% becomes "
        "140% against 10% Crit Block). It reduces how hard crits hit, never "
        "whether they happen.</li>"
        "</ul>"
        "<p><b>Practical read:</b> the chance fight (Crit Chance vs Crit "
        "Resistance) and the damage fight (Crit DMG vs Crit Block) are "
        "separate. Stacking Crit DMG does nothing against someone you "
        "can't crit, and Crit Block won't stop crits from landing — it "
        "only blunts them.</p>"

        "<h3>Sustain, exactly</h3>"
        "<p>Out of combat you regenerate <b>2% of max HP and MP per "
        "second</b>; regen stats raise this rate. Shields come in three "
        "kinds: standard shields absorb a fixed capacity of damage, MP-fed "
        "shields route damage into your Max MP pool instead of a capacity "
        "limit, and blood shields are fed from HP. There are also statuses "
        "that strengthen an active shield's absorption, deal bonus damage "
        "while your shield holds, and cleanse debuffs when a shield is "
        "applied.</p>"

        "<h3>The gear stat formula</h3>"
        "<p>An item's visible stat line is computed as:</p>"
        "<p style='margin-left:16px'><code>floor( base[rank][affix] × "
        "roll × rarity_scale )</code></p>"
        "<ul>"
        "<li><code>base[rank][affix]</code> — a lookup keyed by the item's "
        "level requirement and which affix the line is; this table is "
        "server-side.</li>"
        "<li><code>roll</code> — the forge-time quality roll, interpolated "
        "linearly between the affix's min and max range (a 0–100 score).</li>"
        "<li><code>rarity_scale</code> — a flat multiplier per rarity color; "
        "higher rarity scales every line on the item.</li>"
        "</ul>"
        "<p>Carving lines use the same base lookup times a per-carving-level "
        "multiplier, which is why a carving's value jumps when its rarity "
        "tier steps up. Augment levels multiply the item's base stats by a "
        "smooth per-level curve on top of all of this.</p>"

        "<h3>Damage families</h3>"
        "<p>Offense and defense are tracked separately per <i>source</i>: "
        "Abilities, Relics and Immortactic arts each have their own attack, "
        "defense and crit lines, and PvP (\"vs Taoists\") and PvE (\"vs "
        "monsters\") are independent trees on top of that. Two consequences "
        "worth knowing: a \"Relic DMG +x%\" line does nothing for your "
        "Ability damage, and PvE reduction does nothing in duels. There are "
        "also path-split modifiers — damage vs Immortal-path and vs "
        "Demon-path cultivators are separate stats.</p>"

        "<h3>How Battle Rating is put together</h3>"
        "<p>The total is computed server-side, but the client defines the "
        "structure: every stat carries a BR weight, and your BR is the "
        "weighted sum of everything you have, plus pre-scored blocks for "
        "gear. The in-game BR breakdown panel groups it into: character "
        "level &amp; realm, inner skill, gear (base + affixes + augment "
        "levels + carvings), Relics (same sub-parts), Abilities and their "
        "training, Curios (base + active + set), pets (level, skills, "
        "growth), plus talismans, celebrity cards and the rest.</p>"
        "<p>Two useful things fall out of the client weights:</p>"
        "<ul>"
        "<li><b>Defense is weighted ~2.1× attack per point</b> (and HP/MP "
        "pool points are weighted far below either) — the game \"prices\" a "
        "point of defense as worth about twice a point of attack.</li>"
        "<li><b>Each gear piece and Relic arrives with its BR pre-computed</b> "
        "(a base score, and for Relics a realm-corrected score that only "
        "applies once your realm meets the item's requirement — an "
        "under-realm Relic shows its uncorrected, lower BR).</li>"
        "</ul>"
        "<p>The exact weight constants are known, but the "
        "server's final assembly (level factors, rounding) isn't, "
        "so per-stat BR predictions from these weights are approximate.</p>"
        "<p>One BR formula <i>is</i> fully client-side — standard monster "
        "BR:</p>"
        "<p style='margin-left:16px'><code>floor( (hp_std^0.98 + "
        "mp_std^0.98) × hp_mult × max(atk_mults) )</code></p>"
        "<p>where <code>hp_std</code>/<code>mp_std</code> are the standard "
        "stat values for the monster's level and the multipliers are the "
        "monster's own scaling. The 0.98 exponent means BR grows slightly "
        "sub-linearly with raw stats. The same per-level standards table "
        "drives realm normalization: the \"standard\" each flat stat is "
        "measured against grows by roughly 5–8× per realm tier, which is "
        "exactly why a flat crit value loses percentage on breakthrough.</p>")

    return [(slug, title, html + footer) for slug, title, html in (
        ("basics", "Basics", basics),
        ("pills", "Pills & Respira", pills),
        ("elixirs", "Elixirs & Stat Pills", elixirs),
        ("myrimon", "Myrimon & Extractor", myrimon),
        ("curios", "Curios", curios),
        ("artifacts", "Artifacts & Gems", artifacts),
        ("combat", "Combat & Gear", combat),
        ("affixes", "Affixes", affixes),
        ("systems", "World Systems", systems),
        ("advanced", "Advanced", advanced),
    )]


def build_guide_pages(acc: dict) -> list:
    """Stage-by-stage cultivation guide, one page per realm band. `acc` is
    accepted for symmetry with build_reference_pages; the guide's prose and
    footer use no theme accents today."""
    footer = _footer("gray", (
        "Spotted an error or something missing? Please report "
        "corrections and new data at "))

    # Path meta assembled from a circulating community guide (2026) plus
    # the maintainer's read of Discord consensus — opinion, not client data.
    paths = (
        "<h2>Choosing your path</h2>"
        "<p>The first decision in the game. It's less permanent than it "
        "looks — Path Switch exists from Foundation (7-day cooldown, "
        "rising Fateum cost) — but your path shapes combat style, gear "
        "priorities, and which elixirs/pets/aux picks fit. This summary "
        "is <i>subjective</i>, and opinion is genuinely "
        "mixed — treat it as orientation, not law.</p>"
        "<h3>The five paths</h3>"
        "<ul>"
        "<li><b>Swordia</b> (HP / physical) — highest sustained DPS in "
        "the game; strong in both PvP and PvE bossing. Very reliant on "
        "its relics (flying swords). The safe strong pick.</li>"
        "<li><b>Corporia</b> (HP / physical) — burst physical damage "
        "with a death-immunity ultimate; not relic-reliant. Weaker "
        "early, much stronger later; PvE is its weak side — a "
        "PvP-leaning pick.</li>"
        "<li><b>Magicka</b> (MP / magic) — AoE damage, lots of shields "
        "and crowd control. Good at PvE farming (gear and pill "
        "materials) and holds up in PvP, though it takes more piloting "
        "than Swordia. The flexible pick.</li>"
        "<li><b>Ghostia</b> (MP / magic) — summons a ghost companion "
        "that taunts and deals damage; unblockable-paralyze ultimate. "
        "Very relic-reliant. Strong PvE and dueling.</li>"
        "<li><b>Literatia</b> (MP / magic) — the newest path: builds "
        "<i>erudition</i> to unleash a high-burst mana dump (Literal "
        "Reality). Weak early in the mortal world and scales up later; "
        "good AoE farm and PvE, PvP still unproven.</li>"
        "</ul>"
        "<p><b>Rules of thumb:</b> want one answer for everything — "
        "Swordia. PvE/farming focus — Ghostia or Magicka. PvP focus — "
        "Corporia or Swordia. Patient scaler who accepts a weak mortal "
        "world — Literatia. Aux pairings are on the "
        "<a href='app://guide/aux'>Aux Paths tab</a>.</p>"
        "<p>Note that relic-reliant paths (Swordia, Ghostia) care more "
        "about relic income and forging; ability-focused paths "
        "(Corporia, Magicka, Literatia) lean on ability levels — which "
        "come from Demon Spire climbing (<a href='app://ref/systems#spire'>"
        "Reference → World Systems</a>).</p>")

    # Server calendar sources: docs/knowledge/game-mechanics-verified.md
    # (Worlds section); day numbers are era estimates.
    server = (
        "<h2>How a server unfolds</h2>"
        "<p>OverMortal is server-paced. World-level timegates hold the "
        "whole server to one calendar — nobody enters a new era before its "
        "gate opens — and the catch-up mechanics accelerate everyone behind "
        "the front. Two consequences: your first month has a known shape, "
        "and you cannot fall permanently behind.</p>"
        "<h3>The first month (day numbers drift by era)</h3>"
        "<ul><li><b>Day 0</b> — the server opens. The early stages fly: "
        "Novice–Foundation on day one, Virtuoso by its end, Nascent Soul "
        "around day 3 free-to-play.</li>"
        "<li><b>Weeks 1–4</b> — the climb through Nascent Soul and "
        "Incarnation. Build the extractor and stockpile fruits, keep every "
        "daily stream full, and keep battle rating growing: the Ascension "
        "Virya blessings at Incarnation's end gate on Myrimon Wonder boss "
        "clears.</li>"
        "<li><b>~Day 35–38</b> — the first timegate lifts: Ascension into "
        "Voidbreak, the Mortal → Spiritual World boundary. The parked weeks "
        "before it are the prestock window — the full playbook is on "
        "<a href='app://guide/timegate'>Guide → Timegate</a>.</li>"
        "<li><b>Day 40</b> — server transfer unlocks (for Voidbreak and "
        "higher).</li>"
        "<li><b>After that</b> — every major Stage from Wholeness on is "
        "paced by its own gate, and the World-boundary resets (fresh "
        "Myrimon tier and extractor) repeat at Celestial. The rhythm you "
        "learn at the first gate is the game's permanent shape.</li></ul>"
        "<h3>Why you can't fall behind</h3>"
        "<p>Two mechanics work together. Timegates hold the server's front "
        "in place — the leaders sit parked at caps, stocking overcap EXP "
        "while the gate is closed — and <b>Strive</b> multiplies absorption "
        "for everyone behind the front, fading only as you close the gap "
        "(<a href='app://ref/basics'>Reference → Basics</a>). The server "
        "bunches up at every gate, then peels off front to back. A slow "
        "week doesn't compound; the system pulls you back toward the "
        "pack.</p>"
        "<h3>Joining an established server</h3>"
        "<ul><li>Once a gate has opened for the server it stays open — you "
        "ascend the moment you're ready, no waiting.</li>"
        "<li><b>Strive is your engine</b>: the further behind the front you "
        "start, the bigger your absorption multiplier.</li>"
        "<li>The +50% highest-Stage fruit bonus isn't yours until you reach "
        "the server's front, so extractor leveling discipline "
        "(<a href='app://ref/myrimon'>Reference → Myrimon &amp; "
        "Extractor</a>) matters even more for you — the multipliers you "
        "control are the ones you get.</li>"
        "<li>Server transfer (Voidbreak and higher) can move you to a "
        "server whose calendar fits your pace.</li></ul>")

    routine = (
        "<h2>Your daily loop</h2>"
        "<p>OverMortal is an idle game with a short list of things that "
        "actually need your hands each day. Everything here is collected "
        "from the other guide pages — this is just the checklist "
        "form.</p>"
        "<h3>Every day</h3><ul>"
        "<li><b>Spend your daily pill attempts</b> — highest color first "
        "(all colors share the one attempt pool; Vase reds are exempt and "
        "always free to eat). Never leave attempts unused: pill EXP roughly "
        "halves per quality step, so a full limit of a lower color beats a "
        "half-filled limit of a higher one.</li>"
        "<li><b>Use your Respira attempts.</b></li>"
        "<li><b>Keep artifact energy below its cap</b> — Vase refines, "
        "Mirror duplications, Pearl uses. Energy regenerating into a full "
        "pool is wasted. If you pay, the 30 Fateum/Destium daily charge "
        "per artifact is among the cheapest EXP money buys.</li>"
        "<li><b>Claim your Aura Gem</b> before its storage caps (18–32 "
        "hours depending on rarity) — once it's full it stops "
        "accruing.</li>"
        "<li><b>Check the market</b> for Demonroot (pet skills) and "
        "similar limited stock.</li>"
        "<li><b>Take stat pills and elixirs as they arrive</b> — there's "
        "no timing play on either (<a href='app://ref/elixirs'>"
        "Reference → Elixirs &amp; Stat Pills</a>).</li>"
        "<li><b>Myrimon runs</b>: during the event's first week they don't "
        "accumulate — use them daily at the highest realm you can clear. "
        "After the first week they stack (see Weekly).</li>"
        "</ul>"
        "<h3>Weekly</h3><ul>"
        "<li>Banked <b>Myrimon runs</b>: spend them on Sunday, or hold "
        "them until you can clear a higher-requirement dungeon. Fruits go "
        "to the stockpile, not the extractor, until the extractor is "
        "maxed (<a href='app://ref/myrimon#verified'>Reference → Myrimon &amp; "
        "Extractor</a>).</li>"
        "<li><b>Spend resources as they come.</b> Hoarding pays only in "
        "the parked weeks before a timegate (<a href='app://guide/timegate'>"
        "Guide → Timegate</a>) — between gates, saved resources are power "
        "you didn't use.</li>"
        "</ul>"
        "<h3>Before every major breakthrough</h3><ul>"
        "<li><b>Spend all daily pills and Respira attempts</b> — they "
        "reset on the breakthrough.</li>"
        "<li><b>Eat the fruit stockpile before a realm ascension</b> — "
        "the extractor resets to Common there and auto-consumes leftovers "
        "at pre-upgrade rates. (Stage breakthroughs within a realm don't "
        "reset it.)</li>"
        "<li><b>Spend Fatevillion shop tokens</b> — that shop resets "
        "too.</li>"
        "<li><b>Don't claim pill bags</b> until after the ascension — "
        "claimed bags count against the old realm.</li>"
        "<li>If you spend money: the <b>three elixir packs</b> offered on "
        "reaching the new realm are among the best value in the game "
        "(<a href='app://ref/elixirs#expelixirs'>Reference → Elixirs &amp; Stat "
        "Pills</a>); the full what's-worth-it list is on "
        "<a href='app://guide/spending'>Guide → Spending</a>.</li>"
        "</ul>"
        "<h3>Quality-of-life settings</h3><ul>"
        "<li>Turn off <b>wandering</b> (settings) — it only animates your "
        "character walking around and costs attention for nothing.</li>"
        "<li>Set <b>battle speed to 3×</b> once it unlocks; there is no "
        "downside.</li>"
        "</ul>")

    novice = (
        "<h2>Novice – Foundation (your first day)</h2>"
        "<p>These first realms go by in hours. The goal is simple: keep the "
        "cultivation bar filling and break through the moment you can — the "
        "<b>Breakthrough</b> button appears on the main cultivation screen "
        "when the bar is full.</p><ul>"
        "<li><b>Break through to Connection immediately.</b> Nothing in Novice "
        "is worth lingering for.</li>"
        "<li><b>Pills</b> are the bottles on the bottom row of the cultivation "
        "screen — each grants instant cultivation EXP and you have a daily "
        "attempt limit. Early on, use only <b>blue</b> pills and don't max out "
        "your daily attempts until you've claimed the pill bag from the early "
        "quests. Save 5-10 attempts for Foundation 10, and spend pills mainly "
        "when they push you over a stage breakthrough. (What each pill is "
        "worth: <a href='app://ref/pills#daily'>Reference → Pills &amp; "
        "Respira</a>.)</li>"
        "<li><b>Alchemy:</b> save your blue and purple pill materials for "
        "F9-F10 rather than crafting them the moment you get them.</li>"
        "<li><b>Respira</b> is the daily breathing exercise on the cultivation "
        "screen (the \"Today's Attempts\" counter). Before breaking through to "
        "Foundation, open <b>Techniques</b> and max <b>Longevity</b> — it "
        "permanently adds +1 daily Respira attempt and is cheapest now.</li>"
        "<li>In Foundation, unlock the <b>Energy Unification</b> technique "
        "before spending your Respira attempts, and hold your pill attempts "
        "until Foundation Late with the <b>Rejuvenation</b> technique at T3 "
        "(techniques boost how much each attempt is worth).</li>"
        "<li><b>Energy Array</b> materials come from the world-map realms: "
        "56 violetite from <b>Violet Streams</b>, then 110 frostite from "
        "<b>Lake Blackwater</b>. The array permanently raises your Abode "
        "Aura, which is the base of your cultivation speed "
        "(<a href='app://ref/basics#cultivation'>Reference → Basics</a> explains the "
        "speed formula).</li></ul>")

    virtuoso = (
        "<h2>Virtuoso (usually end of day 1)</h2>"
        "<ul><li><b>Myrimon unlocks here</b> — it appears as the <b>Aura "
        "Extractor</b> lotus next to your character on the cultivation "
        "screen, fed by fruits from the weekly Myrimon dungeon runs. This "
        "becomes your single biggest free source of cultivation EXP, so read "
        "<a href='app://ref/myrimon'>Reference → Myrimon &amp; "
        "Extractor</a> before spending anything.</li>"
        "<li>During the first week of the Myrimon event your daily runs "
        "<b>don't accumulate</b> — use them every day, at the highest realm "
        "you can clear. After that first week they stack, so you can bank "
        "them for Sunday or until you can clear a higher-requirement "
        "dungeon.</li>"
        "<li>Work through <b>Realm Abyss</b> and <b>Cultivation Ruins</b> "
        "(in the realm/world-map menus) for all three Virtuoso realms — "
        "they hand out one-time cultivation rewards.</li>"
        "<li>Check the events panel for realm exploration events; the curio "
        "rewards are worth the detour.</li>"
        "<li>Free equipment upgrade materials: open the <b>Library of No "
        "Bound → Encyclopedia Tales</b> and go through the lore chronicles. "
        "Each chronicle has a comment section with notes from game NPCs — "
        "the <b>first like you give in each chronicle's comments</b> awards "
        "equipment upgrade material. Worth sweeping once while pushing "
        "through Virtuoso.</li></ul>")

    nascent = (
        "<h2>Nascent Soul (~day 3 for F2P)</h2>"
        "<ul><li>Pacing: expect ~3 days to reach Nascent Late and ~3 more to "
        "Incarnation. Spenders arrive faster; don't panic if you're a day "
        "behind these numbers.</li>"
        "<li><b>Strive unlocks here.</b> It's a catch-up bonus that raises "
        "your absorption while you're behind your server's #1 cultivator — "
        "you'll see your absorption ratio exceed the stage's base. In this "
        "calculator it appears as the implied Strive readout under the "
        "Absorption Ratio input, and the \"Server #1's Stage\" input starts "
        "to matter for long-range estimates. (<a href='app://ref/basics#tips'>"
        "Reference → Basics</a> covers how Strive enters the math.)</li>"
        "<li>Keep the <b>story</b>, <b>Demon Spire</b>, and <b>realms</b> "
        "pushed as far as they'll go at every cultivation stage — several "
        "systems gate on them.</li>"
        "<li>By now <b>stat pills and elixirs</b> are flowing in from "
        "shops and rewards. Take them as they arrive — neither can be "
        "wasted by using them early, and stat pills' use caps grow with "
        "each realm anyway. What they are and how their limits work: "
        "<a href='app://ref/elixirs#tolerance'>Reference → Elixirs &amp; Stat "
        "Pills</a>.</li></ul>")

    incarnation = (
        "<h2>Incarnation</h2>"
        "<ul><li>This is the extractor endgame for the mortal world. Open "
        "the <b>Aura Extractor → Boost</b> screen and max its tracks — "
        "<b>Quality first</b>, then Cultivation, then Gush (High Rank last, "
        "only after the rest). Keep <b>stockpiling fruits</b> instead of "
        "eating them: every extractor level makes each fruit worth more, and "
        "at Mortal World rank the extractor adds <b>+50% base fruit EXP</b> "
        "while you're at the server's highest Stage.</li>"
        "<li><b>Eat the stockpile before the realm timegate</b> — fruits "
        "lose 50% of their EXP once the next realm's timegate passes — or on "
        "the last day before your own breakthrough, whichever comes first. "
        "(Timegates and the full fruit math: <a href='app://ref/myrimon#fruits'>"
        "Reference → Myrimon &amp; Extractor</a>.)</li>"
        "<li>Before breaking through to Voidbreak: <b>spend all pills and "
        "Respira attempts</b> (they reset on the breakthrough), <b>don't</b> "
        "claim daily pill bags until after ascension, and spend your "
        "<b>Fatevillion</b> shop tokens beforehand — that shop resets on "
        "breakthroughs too.</li>"
        "<li>On the ascension itself you'll be offered <b>three real-money "
        "elixir packs</b> — if you spend at all, these are among the best "
        "value in the game (<a href='app://ref/elixirs#expelixirs'>Reference → "
        "Elixirs &amp; Stat Pills</a> explains "
        "why the early tolerance tiers make them worth the most).</li>"
        "<li><b>Keep battle rating growing all era</b> — the Ascension "
        "Virya blessing tiers gate on Myrimon Wonder boss clears (Amethyst "
        "Fiend, Jade-Eyed Lion). Reaching the gate weeks with the bosses "
        "unkillable means blessings locked exactly when they matter "
        "most.</li>"
        "<li>The run-up to the realm timegate — prestocking past 100%, the "
        "Ascension Virya blessings, and what to do the day the gate lifts — "
        "has its own page: <a href='app://guide/timegate'>Guide → "
        "Timegate</a>.</li></ul>")

    # Overcap/Virya mechanics and half-step totals:
    # docs/knowledge/game-mechanics-verified.md + data/breakthrough.json.
    timegate = (
        "<h2>The Voidbreak timegate</h2>"
        "<p>A world-level timegate blocks the ascension from Incarnation "
        "into Voidbreak until a fixed server day (roughly day 35–38 of a "
        "server's life; the exact day drifts by era). This ascension is "
        "also the <b>Mortal → Spiritual World boundary</b> — the fresh "
        "Myrimon tier and extractor ride on it (see the Worlds table in "
        "Reference → Basics). Handled well, the gated weeks become a "
        "stockpile that carries you deep into Voidbreak the day the gate "
        "opens. The same pattern returns at every later gate.</p>"
        "<h3>Excess EXP: nothing is lost at a full gauge</h3>"
        "<ul><li>While the gate blocks your breakthrough, cultivation EXP "
        "keeps accruing past the full gauge into an <b>Excess EXP</b> pool "
        "that is returned after the breakthrough.</li>"
        "<li>Breakthroughs are always <b>manual</b>: stocked excess applies "
        "as you click through each grade, so a large pool clears whole "
        "half-steps in one go.</li>"
        "<li>The gauge percentage past 100% reads as EXP gained since the "
        "start of your current half-step ÷ that half-step's total — read it "
        "off the half-step completion gauge that fills to 100% and keeps "
        "climbing, not the per-grade step bar. An overcap percentage "
        "translates directly into future progress.</li>"
        "</ul>"
        "<h3>What a given stock buys you</h3>"
        "<table cellpadding='4' cellspacing='0' border='1' "
        "style='border-collapse:collapse'>"
        "<tr><th>Half-step</th><th>Total EXP</th></tr>"
        "<tr><td>Incarnation Late</td><td>61.8M</td></tr>"
        "<tr><td>Voidbreak Early (20 grades)</td><td>68.0M</td></tr>"
        "<tr><td>Voidbreak Middle (20 grades)</td><td>142.1M</td></tr>"
        "<tr><td>Voidbreak Late (20 grades)</td><td>307.7M</td></tr>"
        "</table>"
        "<ul><li><b>100%</b> — gauge full: take the Completion breakthrough "
        "(below) and keep stocking.</li>"
        "<li><b>210%</b> — the excess clears all of Voidbreak Early on "
        "ascension day.</li>"
        "<li><b>440%</b> — Early and Middle both: you arrive at Voidbreak "
        "Late G1 immediately.</li></ul>"
        "<h3>Accrual while parked at a full gauge</h3>"
        "<ul><li>You accrue at the <b>capped row's base band</b> — no "
        "future-row speed scaling.</li>"
        "<li><b>Strive does not apply while overcapped.</b> Server leaders "
        "lose nothing; the further behind the top player you are, the more "
        "parking under-performs your normal rate.</li>"
        "<li><b>Virya blessing points apply in full.</b></li>"
        "<li>Flat daily EXP — pills, Respira, elixirs, fruits — lands in "
        "the pool at face value, unaffected by parking.</li></ul>"
        "<p>Base bands rise with each half-step: Incarnation Late 0.40 → "
        "Voidbreak Early 0.50 → Middle 0.65 → Late 0.80.</p>"
        "<h3>Ascension Virya blessings: the biggest lever</h3>"
        "<p>Blessing points are the difference between a mediocre stock and "
        "a huge one. Tiers unlock from your primary and secondary paths "
        "together:</p>"
        "<ul><li><b>Completion</b> — reach Incarnation Late 100% and "
        "<b>break through into Incarnation (Perfected)</b>. A full gauge "
        "alone is not enough: the blessing system does not start until this "
        "breakthrough is taken. It is not blocked by the timegate — the "
        "gate blocks only the ascension into Voidbreak — so take it the "
        "moment the gauge fills. It removes realm restrictions on "
        "cultivation pills (higher-rank pills can feed a lower secondary "
        "path; rank-appropriate pills already work there without it) and "
        "unlocks pill auto-transmogrification, which lets breakthrough "
        "pills of one path be used on the other (physical ↔ magical). "
        "Together these make the secondary rush below possible.</li>"
        "<li><b>Perfection</b> — primary at Incarnation (Perfected), "
        "secondary at Nascent Soul Late, clear Amethyst Fiend in Myrimon "
        "Wonder: <b>+20 points</b> absorption in your current Stage.</li>"
        "<li><b>Perfect</b> — secondary at Incarnation Middle, clear "
        "Jade-Eyed Lion: a second absorption tier, plus an 'Absorption "
        "Ratio Before Voidbreak Middle' line that comes into play once you "
        "are in Voidbreak.</li></ul>"
        "<p>Secondary requirements are satisfied on <b>reaching</b> the "
        "named half-step, not completing it. On the Incarnation base band a "
        "live +20 points already lifts your parked rate well above the raw "
        "passive rate, so the rush is worth prioritising. How the tiers "
        "carry into Voidbreak depends on your build — read your in-game "
        "absorption there and enter it into the calculator rather than "
        "assuming a fixed total.</p>"
        "<h3>Preparing while gated</h3>"
        "<ul><li><b>Cap Incarnation early and take the Completion "
        "breakthrough at once.</b> Days spent climbing to the cap are not "
        "stocking days, and the gauge filling by itself starts nothing. "
        "Top off with banked fruits if the gauge won't fill on streams "
        "alone.</li>"
        "<li><b>Rush the Virya tiers immediately after.</b> Divert your "
        "daily pills to the secondary path (passive stays on the primary): "
        "Nascent Soul Late unlocks the first absorption tier, Incarnation "
        "Middle the next. The earlier the tiers land, the longer they lift "
        "your parked accrual. Clear the two Myrimon Wonder bosses ahead of "
        "time so they never hold a tier hostage.</li>"
        "<li><b>Fill every flat stream, every day.</b> Never leave pill "
        "attempts unused: pill EXP roughly halves per quality step, so a "
        "full limit of the next quality down matches a half-filled limit "
        "of the one above.</li>"
        "<li><b>Eat the fruit bank before the gate opens</b> — the banking "
        "and 50% rules are on <a href='app://guide/incarnation'>Guide → "
        "Incarnation</a>. Leftovers don't survive the ascension anyway: "
        "the mortal extractor resets at the World boundary and "
        "auto-consumes them at pre-upgrade rates.</li>"
        "<li><b>Hoard for the arrival — the parked weeks are the window.</b> "
        "Sect contribution (~13–14k) for the new realm's blueprints and "
        "formulas; Fateum and Fate Tokens, Revealstones, plant speed-ups; "
        "trove jadeslips for Cosmic Atlas, Ancient Treasure and Pet Index — "
        "their contents re-tier on realm breakthrough, so opened on arrival "
        "they pay out at the new realm's tier. Don't run this hoard between "
        "gates: realm gates are months apart, and resources sat on for "
        "months are power you didn't use.</li>"
        "<li><b>Fully unlock the garden before Voidbreak, even though Law "
        "Fruit isn't usable until you're there.</b> A garden slot not "
        "bought before the ascension is permanently lost Elemental Law "
        "throughput for however long it stays unbought — there's no way "
        "to recover missed law levels retroactively. This is separate "
        "from harvesting it empty below: buy every cell now, then "
        "replant Law Fruit the moment Voidbreak opens (<a "
        "href='app://ref/systems#garden'>Reference → World Systems</a> "
        "covers the throughput math).</li>"
        "<li><b>Spend what dies with the realm.</b> Beyond the "
        "pre-breakthrough rules on the Incarnation page, spend Ability "
        "Knowledge and harvest the garden empty before ascending.</li>"
        "<li><b>Have breakthrough materials ready.</b> Excess EXP applies "
        "only as fast as you can click through breakthroughs; missing "
        "consumables are the only thing that can stall a charged "
        "climb.</li></ul>"
        "<h3>Gate day</h3>"
        "<ul><li><b>Ascend the moment the gate lifts.</b> Voidbreak Early's "
        "base band (0.50) beats Incarnation Late's (0.40) — whether you "
        "park or push, you accrue faster inside.</li>"
        "<li><b>Click through Voidbreak Early</b> — your excess charges its "
        "grades instantly.</li>"
        "<li><b>Route by where the server's leaders are, not by your "
        "current Strive number.</b> Two rates compete once you are inside. "
        "Parked at the Early cap you accrue at your base band <i>plus your "
        "blessing</i>, with no Strive; pushing live through Middle you "
        "accrue at Middle's higher base band × (1 + Strive). Strive is "
        "measured against the server's top cultivator, so what matters is "
        "the Strive you would have <i>while in Middle</i>:"
        "<ul><li><b>Never be the first into Middle.</b> While the leaders "
        "hold the Early cap, pushing past them makes you the front — your "
        "Strive drops away and you grind Middle at its flat base band, "
        "which the parked rate can beat.</li>"
        "<li><b>Front-runners</b>: stay parked until the pool covers all "
        "142.1M of Middle, then clear it in one push and arrive at "
        "Voidbreak Late. A one-push spends no live time in Middle, so lost "
        "Strive never enters into it.</li>"
        "<li><b>After the leaders push to Late</b>, trailing players keep "
        "their Strive while climbing Middle live. Once your live Strive is "
        "high enough that the live rate beats the parked rate, pushing "
        "wins; below that, keep parking until your own pool covers the "
        "rest.</li></ul>"
        "The crossover depends on how much blessing you have live in "
        "Voidbreak, so let the calculator compare the two for your own "
        "absorption and Strive. The net effect: the server bunches at the "
        "Early cap, then peels off front to back.</li>"
        "<li><b>Move your streams up a tier.</b> Switch to the newly "
        "unlocked pill rank as soon as it's sustainable, start leveling "
        "the Spiritual World's fresh extractor with the new fruit income, "
        "open the saved jadeslips, and spend the hoarded sect "
        "contribution. The rest of arrival day (laws, Pandemonium, the "
        "trove) is the checklist on <a href='app://guide/voidbreak'>Guide "
        "→ Voidbreak+</a>.</li></ul>"
        "<h3>By account type</h3>"
        "<ul><li><b>Without the Vase</b>: your pill stream is exactly the "
        "daily limit, so quality per attempt is everything you control "
        "there — and your prestock leans hardest on passive accrual, which "
        "makes the Virya rush proportionally your biggest lever. Fruits are "
        "your swing resource; bank them well.</li>"
        "<li><b>With the Vase (and Mirror)</b>: refined red pills bypass "
        "the daily limit, so a fed Vase adds stock at face value every "
        "parked day, and the Mirror stacks copies on top. Keep them fed for "
        "the whole gated stretch — artifact energy sitting at its cap is "
        "stock lost (<a href='app://ref/artifacts'>Reference → Artifacts "
        "&amp; Gems</a>).</li>"
        "<li><b>Free-to-play</b>: fruits are the main F2P tool for meeting "
        "timegates, and blessings are progression-gated, not paid — a "
        "built secondary path is worth more than any consumable. Sustain "
        "the best pill quality you can, but a full limit of a lower "
        "quality still beats a half-filled limit of a higher one.</li>"
        "<li><b>Paying</b>: the two standout paid levers during a gate are "
        "the daily artifact charges and the three elixir packs offered on "
        "entering the new realm — take those at Voidbreak, not before. The "
        "full what's-worth-it list is on <a href='app://guide/spending'>"
        "Guide → Spending</a>.</li>"
        "<li><b>Underdeveloped secondary path</b>: the blessing tiers need "
        "the secondary at Nascent Soul Late, then Incarnation Middle. "
        "Completion's realm-restriction removal exists exactly to fix this "
        "— the moment it lands, divert your now-unrestricted daily pills "
        "to the secondary and power-level it. Until the tiers land you "
        "park at base band only — well under half the blessed rate — so "
        "every day of delay is expensive.</li></ul>"
        "<p>Set <b>Timegate lifts in</b> on the calculator's input panel "
        "to compare the gate date against the prestock projection and see "
        "where your stock will land you.</p>")

    voidbreak = (
        "<h2>Voidbreak and beyond</h2>"
        "<ul><li>Arriving with a prestock? When to hold the Early cap vs "
        "push into Middle is on <a href='app://guide/timegate'>Guide → "
        "Timegate</a>.</li>"
        "<li>Dailies and pill bags <b>reset on ascension</b> — same rule "
        "as the Incarnation checklist: spend before you break through.</li>"
        "<li>Ascension opens the <b>Spiritual World's own Myrimon tier</b> — "
        "new fruit ranks (R6+) and a fresh extractor that starts back at "
        "Common quality and bonus level 0. Stage breakthroughs inside the "
        "World keep it; the next reset like this comes at Celestial "
        "(Immortal World). The stockpile-then-eat rhythm repeats at each "
        "World.</li>"
        "<li><b>Strive above 120% is normal here.</b> The 120% cap belongs "
        "to the mortal world; later realms allow overcapping (for example by "
        "keeping your aux path a minor realm behind your main). The "
        "calculator only warns about >120% readings in mortal-world "
        "stages.</li></ul>"

        # Community-guide material (2026): friend levels/payoffs are the
        # circulating consensus list, cross-checked against the app's own
        # pill/Respira source data where the two overlap.
        "<h3>Ascension day checklist</h3>"
        "<p>The order of operations for the day you break through to "
        "Voidbreak:</p><ul>"
        "<li><b>Before</b> the breakthrough: don't claim dailies or pill "
        "bags — they count against the old realm (same rule as every "
        "major breakthrough).</li>"
        "<li><b>Hold unredeemed Myrimon Tokens</b> (the cash-shop item, up "
        "to 2/week, each worth +1 run) rather than cashing them in on a "
        "few extra mortal-realm fruit — tokens are inventory items you "
        "can bank indefinitely, so redeem them right after ascending for "
        "Voidbreak-tier fruit instead.</li>"
        "<li><b>Immediately after</b>: unlock <b>laws</b> as soon as "
        "possible, buy <b>law fragments</b>, plant <b>law fruits</b> in "
        "the garden, and buy <b>Nature Mantras</b>.</li>"
        "<li>Unlock <b>Pandemonium</b> and its three maps.</li>"
        "<li>Claim the <b>treasure trove</b> at Voidbreak, not at "
        "Incarnation — it scales with the realm you claim it in.</li>"
        "</ul>"
        "<h3>Immortal Friends (recommended priorities)</h3>"
        "<p>Friends' levels pay off in cultivation terms at specific "
        "breakpoints. The recommended unlock/level priorities:</p><ul>"
        "<li><b>Crane Boy</b> to max — <b>+1 daily pill attempt</b>.</li>"
        "<li><b>Iron Fan</b> 36, <b>Daji</b> 73, <b>Shen Gongbao</b> 117 "
        "— <b>+1 daily Respira attempt</b> each.</li>"
        "<li><b>Jiang Ziya</b> 116 and <b>Taotie</b> 117 — <b>+3% pill "
        "effect</b> each.</li>"
        "<li><b>Macaque</b> 17 — +3% Respira EXP (already included in "
        "your in-game Respira tooltip).</li>"
        "<li>Also on the priority list (payoff "
        "unknown): <b>White Astra</b> 31, <b>Princess Adalinda</b> 81, "
        "<b>Leizhenzi</b> 129.</li>"
        "</ul>"
        "<p>These attempt/effect bonuses are exactly what the "
        "calculator's pill and Respira source pickers model — tick them "
        "there once you hit the breakpoints.</p>")

    pets = (
        "<h2>Pets</h2>"
        "<p>Pets are combat companions — they raise your battle rating and "
        "fight beside you. They do <b>not</b> affect cultivation speed or "
        "breakthrough timing. Where they earn their keep is PvE damage "
        "rankings — Demonbend Abyss, Beast Invasion, Monster Hunt, Town "
        "Boss, the tower — which mostly means single-target damage against "
        "one boss. In PvP even the tanky pets only survive a couple of "
        "extra hits, so taunts and stuns rarely get to matter.</p><ul>"
        "<li><b>Raise ONE pet only.</b> Every rarity step costs more copies "
        "and essences than the last, and activities like Realm Map farming "
        "allow a single pet anyway — a second half-built pet helps "
        "nowhere.</li>"
        "<li>Corporia: <b>Blazelion</b>. Highest single-target damage, and "
        "its debuffs raise the physical damage the enemy takes.</li>"
        "<li>Magicka: <b>Blazelion</b> is the recommended pick too. "
        "Babewyrm's debuffs do boost your magic damage, but it needs Fire "
        "essences — by far the scarcest — so a Wyrm usually sits several "
        "rarity steps behind what a Lion would be. Check the Pets tab with "
        "your own numbers before committing.</li>"
        "<li><b>Babedeer</b> costs double essences for PvP-only value, and "
        "<b>Berpent</b> only comes from events — neither "
        "suits a focused build.</li></ul>"
        "<h3>Exchange and elimination</h3>"
        "<p>Pets are bought with rare essences: Blazelion 5 Metal + 5 Wood, "
        "Babewyrm 5 Water + 5 Fire, Babetoise 5 Metal + 5 Earth, Babeox "
        "5 Wood + 5 Water, Babedeer 10 Fire + 10 Earth. Eliminating an "
        "owned pet (Abode → Pet → Eliminate, costs Fateum) returns its "
        "essences in full — Berpent returns 5 Water + 5 Earth — so spare "
        "pets are currency: melt the ones you don't raise to buy copies of "
        "the one you do. The <b>Pets tab</b> does this math for you: enter "
        "what you own and it shows the copies and rarity reachable by "
        "going all-in on each pet.</p>"
        "<h3>Rarity ladder</h3>"
        "<table cellpadding='4' cellspacing='0' border='1' "
        "style='border-collapse:collapse'>"
        "<tr><th>Rarity</th><th>Copies</th><th>Pet realm</th></tr>"
        "<tr><td>Common</td><td>1</td><td>Primitive</td></tr>"
        "<tr><td>Uncommon</td><td>1</td><td>Primitive</td></tr>"
        "<tr><td>Uncommon +1</td><td>1</td><td>Virtuoso Early</td></tr>"
        "<tr><td>Rare</td><td>2</td><td>Virtuoso Late</td></tr>"
        "<tr><td>Rare +1</td><td>3</td><td>Nascent Soul Early</td></tr>"
        "<tr><td>Rare +2</td><td>5</td><td>Nascent Soul Middle</td></tr>"
        "<tr><td>Epic</td><td>8</td><td>Nascent Soul Late</td></tr>"
        "<tr><td>Epic +1</td><td>11</td><td>Incarnation Early</td></tr>"
        "<tr><td>Epic +2</td><td>14</td><td>Incarnation Middle</td></tr>"
        "<tr><td>Legendary</td><td>17</td><td>Incarnation Late</td></tr>"
        "<tr><td>Legendary +1</td><td>21</td><td>Voidbreak Early</td></tr>"
        "<tr><td>Legendary +2</td><td>26</td><td>Voidbreak Middle</td></tr>"
        "<tr><td>Legendary +3</td><td>32</td><td>Voidbreak Late</td></tr>"
        "</table>"
        "<p>Copies are cumulative — reaching Legendary consumes 17 in "
        "total. Upgrades also take epic essences (2 by Uncommon +1, 13 in "
        "total by Rare +2), and your pet must reach the listed pet realm "
        "first.</p>"
        "<h3>Feeding and skills</h3>"
        "<table cellpadding='4' cellspacing='0' border='1' "
        "style='border-collapse:collapse'>"
        "<tr><th>Pill</th><th>Common</th><th>Uncommon</th><th>Rare</th></tr>"
        "<tr><td>R1</td><td>125</td><td>250</td><td>400</td></tr>"
        "<tr><td>R2</td><td>625</td><td>1,250</td><td>2,000</td></tr>"
        "<tr><td>R3</td><td>1,900</td><td>3,800</td><td>6,080</td></tr>"
        "<tr><td>R4</td><td>5,000</td><td>10,000</td><td>16,000</td></tr>"
        "<tr><td>R5</td><td>8,000</td><td>16,000</td><td>25,600</td></tr>"
        "</table>"
        "<p>Pet XP per pill. R1 Cleansing/Aura · R2 Nutrition/Revitalising "
        "· R3 Crimson/Ice Heart · R4 Purity/Dracospirit · R5 Chalcedonius/"
        "Reinvigoration. Epic pills give roughly double Rare. Food: "
        "Platycodon 3,500 · Siler 11,000 · Redarrow Flower 33,500 · "
        "Dragongall Flower 54,000 · Curculigo 79,000.</p><ul>"
        "<li><b>Feed food and Common/Uncommon pills.</b> Rarity multiplies "
        "a pill's pet XP far less than it multiplies the pill's value "
        "everywhere else — Rare and better pills are wasted as feed.</li>"
        "<li>Skills unlock with rarity — the second at Uncommon, third at "
        "Rare, fourth at Epic — and level up with <b>Demonroot</b>; buy it "
        "in the market when you see it.</li>"
        "<li>Pets are a low spending priority: heavy pet investment is "
        "whale territory, and free players get most of the value from just "
        "leveling their one pet steadily.</li>"
        "<li>The pet system hands out speed-up items — <b>save them for "
        "law fruits</b> in your garden rather than spending them on the "
        "pet itself (they're part of the standard pre-Voidbreak prep).</li>"
        "</ul>")

    aux = (
        "<h2>Aux Paths (dual pathing)</h2>"
        "<p>Your auxiliary path is a second cultivation class alongside "
        "your main. A good aux adds real fighting power (stats, mana, "
        "shields, crowd control); a bad one adds only small stats. Common "
        "picks:</p><ul>"
        "<li><b>Corporia</b> main → Magicka aux (extra MP and shields for "
        "survivability). Most things work; Literatia is not recommended.</li>"
        "<li><b>Magicka</b> main → Ghostia aux (MP for shields, extra "
        "crowd control, and a ghost that helps monster farming).</li>"
        "<li><b>Swordia</b> main → Magicka aux for sustained damage "
        "(MP + shields); Corporia aux for burst builds.</li>"
        "<li><b>Ghostia</b> main → Corporia aux (survivability and a "
        "strong ultimate that doesn't eat the mana your ghost needs); "
        "Magicka as the alternative.</li>"
        "<li><b>Literatia</b> main → Magicka for F2P/low spenders; "
        "Corporia or Ghostia for committed dual-pathers.</li></ul>"
        "<p><b>Aux paths and cultivation:</b> from Voidbreak through "
        "Wholeness, the aux path enables the Strive overcap play: reach "
        "half-step in Voidbreak, then at Wholeness hold your main path at "
        "Middle G1 and park the aux at Early G20, overcapping its gauge "
        "(~404% stocked = the rest of Wholeness covered; how overcap "
        "percentages read is on <a href='app://guide/timegate'>Guide → "
        "Timegate</a>), then level the main normally "
        "keeping the aux a minor realm behind. It works because an Early "
        "path always counts below a Middle path for Strive, so the bonus "
        "keeps applying. This is why the calculator's 120% Strive warning "
        "only applies to mortal-world stages.</p>"
        "<p>The calculator models one path at a time — enter the numbers "
        "for whichever path you're actively cultivating.</p>")

    # Ratings derived 2026-07-17 from docs/knowledge/technique-books.md
    # (R4–R9 verified node tables; post-R9 sheet extraction) under a
    # fixed speed-value rubric — independently of the community sheet's
    # own grades. Rows sorted best-first within each rank. Mirror of
    # guide_tab.dart's table.
    manual_rows = [
        ("R1", "Longevity", "A", "Aura at learn, then a Respira attempt"),
        ("R2", "Energy Unification", "B", "Small Respira and aura nodes"),
        ("R2", "Rejuvenation", "B", "Small aura node, small pill node"),
        ("R3", "Cosmic Power", "A+", "Respira attempt at learn, effect after"),
        ("R3", "Lifeboom", "A", "Pill effect, then a Respira attempt"),
        ("R3", "Yang", "C", "Crit and monster-damage PvE pick"),
        ("R4", "Astrology", "S", "Aura, Respira effect, then pill attempt"),
        ("R4", "Golden Core", "A", "Pill effect stacked twice plus Respira"),
        ("R4", "Focus", "B", "One small pill node, then Sense filler"),
        ("R4", "Soul Drain", "C", "Monster-farming pick"),
        ("R5", "Ninefall", "A", "Aura twice plus a pill node"),
        ("R5", "Bloodization", "B", "One good aura node behind combat filler"),
        ("R5", "Solarics", "B", "One aura node, rest combat filler"),
        ("R5", "Taiyin Meridian", "B", "Single Respira node amid combat lines"),
        ("R5", "Lunarics", "C", "Control-stacking PvP pick"),
        ("R6", "Yin's Grasp", "S+", "Aura, Respira +5%, then pill attempt"),
        ("R6", "Dragon Flight", "A", "Pill +2% and aura +2%, then filler"),
        ("R6", "Unbound Blade", "B", "Lone aura +3%, rest ability PvP"),
        ("R6", "Conflagration", "B", "Single aura +3% at T9, rest PvP"),
        ("R6", "Lion's Roar", "B", "Respira and Spiritium early, then stop"),
        ("R6", "Thunder Winds", "C", "Crit-stat combat book"),
        ("R7", "Floral Essence", "S+", "All-speed tree ending in pill attempt"),
        ("R7", "Purify &amp; Cleanse", "S+",
         "Instant Respira on learn, attempts later"),
        ("R7", "Great Yang Manual", "S", "Aura, Respira +5%, pill +4% ladder"),
        ("R7", "Aqua Power", "C", "Ability PvP; Spiritium +4% tail"),
        ("R7", "Bulwark", "C", "Control resist and PvE defense"),
        ("R7", "Dragonsound", "C", "Control plus monster damage; PvE pick"),
        ("R7", "Ninefall Hoarfrost", "C", "Magic-side PvP defense pick"),
        ("R7", "Sunset Halberd Dance", "C", "Physical-path PvP pick"),
        ("R7", "Vajra", "C", "Relic PvP niche"),
        ("R8", "Chroma", "S+", "Both attempt nodes; every node speed"),
        ("R8", "Astral Arcanum", "S", "Pill early, aura twice at T9/T12"),
        ("R8", "Cauldron Refinement", "B", "Respira +3% at T3, then combat"),
        ("R8", "Moon Meru", "B", "Control filler until Respira +10% at T12"),
        ("R8", "Tao of Taiqing", "B", "Combat tree until lone aura +4% at T12"),
        ("R8", "Zixiao Sutra", "B", "Pill and aura cheap early, then stop"),
        ("R8", "Dracophant", "C", "Monster and relic defense pick"),
        ("R8", "No-Thought Sutra", "C", "Paralysis stack for PvP"),
        ("R8", "Origin Scripture", "C", "Physical PvP defense pick"),
        ("R9", "Harvest God Secret", "S+", "Aura three times, then a pill attempt"),
        ("R9", "Honored Origin", "A−", "Aura on learn, +3% again at T9"),
        ("R9", "Heartless", "B", "Physical PvP until Respira +10% at T12"),
        ("R9", "Laws of Nature", "B", "Pill unlock at learn; Respira +10% at T12"),
        ("R9", "Divine Water", "C", "Magic-path PvP pick"),
        ("R9", "Eight-Nine Method", "C", "Relic-ability defense pick"),
        ("R9", "Gold Smasher", "C", "Relic-control PvP pick"),
        ("R9", "Mara Incarnation", "C", "Physical ability-PvP pick"),
        ("R9", "Seven Star Blade", "C", "Relic PvP pick"),
        ("R9", "Way of Creation", "C", "Relic and ability hybrid PvP"),
        ("R9", "Wordless Scripture", "C", "Control-stacking utility pick"),
        ("R9", "Zhurong Mantra", "C", "Magic ability-PvP pick"),
        ("R10", "Immortal Ascension", "S+", "Must-take — worth tiering to 12 for +1 daily pill attempt"),
        ("R11", "Thunder Lord Incantation", "S", "Every node is law speed"),
        ("R11", "Heavenly Rhythm", "S",
         "All Respira: attempt mid-tree, effect around it"),
        ("R11", "Pure Mysterious", "A+", "Aura twice early, Fire law capstone"),
        ("R11", "Square Inch Script", "B", "One deep Respira node amid PvP filler"),
        ("R12", "Cloud Satchel", "S", "Every node is law speed"),
        ("R12", "Star Blade", "A−", "Two law nodes, rest combat filler"),
        ("R13", "Pure Starlight", "A", "Early Respira, ends in two law nodes"),
        ("R13", "Five Thunder Mantra", "B", "Aura at unlock, then all-PvP filler"),
        ("R14", "Yin Yang Harmony", "S", "Every node is law speed"),
        ("R14", "Chaos Origin", "S",
         "All Respira: attempt mid-tree, effect around it"),
        ("R14", "Samsara Scripture", "B", "One early aura node, Spiritium tail"),
        ("R15", "Celestial Cloud Scripture", "S", "Every node is law speed"),
        ("R15", "Taisu Scripture", "A", "Aura at learn plus three law nodes"),
        ("R15", "Heaven Execution", "C", "PvP ladder only"),
        ("R16", "Immortality Cloud", "S", "Every node is law speed"),
        ("R16", "Supreme Heavenly Tao", "A", "Respira attempt mid-tree, then combat"),
        ("R16", "Pure Jade One", "B+", "Aura twice up front, then pure PvP"),
        ("R17", "Demonbane Technique", "B", "One Qiyun node early, rest divine combat"),
        ("R17", "Zen Lotus Technique", "B", "Demonic mirror: same lone Qiyun node"),
        ("R18", "Magnetic Light Maneuver", "A", "Qiyun twice, then Respira +7%"),
        ("R18", "Sanskrit Chant", "C", "Crit-stacking PvP pick"),
        ("R19", "Draconic Demon Taming", "B", "One Qiyun node, then stat filler"),
        ("R19", "Jade Reincarnation Technique", "C",
         "Demon damage and stat lines only"),
        ("R20", "Book of Forgotten Wishes", "C",
         "Nothing stands out — take what you like"),
        ("R21", "Book of Necromancy", "B", "A small Qiyun node amid filler"),
        ("R21", "Book of Meditation", "C", "Control and stat lines, no speed"),
    ]
    techniques = (
        "<h2>Technique manuals: what to buy</h2>"
        "<p>Every manual carries bonus nodes — one on learning, more at "
        "tier breakpoints (Tiers 3/6/9, adding 12 and 15 at higher "
        "ranks). The nodes that change your breakthrough time are the "
        "cultivation ones — Base Abode Aura, pill effect and attempts, "
        "Respira effect and attempts — the same bonuses the Vault "
        "tracks (record your books there and the calculator fills "
        "itself). Everything else is combat stats, mostly PvP. "
        "Ratings grade cultivation-speed value only: <b>S+</b> "
        "must-buy, tier deep · <b>S</b> core speed manual · <b>A</b> "
        "solid speed value · <b>B</b> a node or two worth a stop · "
        "<b>C</b> combat or utility only (the note names its niche). "
        "How deep to go is judgment; the node values are the manuals' "
        "own numbers.</p>"
        "<ul>"
        "<li><b>Buy breakpoints, not tiers</b>: a manual is worth "
        "reaching its next good node — stopping between nodes buys only "
        "raw stats.</li>"
        "<li><b>Cultivation nodes come first</b>: an abode-aura or pill "
        "node pays out every day forever; a PvP line only pays when you "
        "fight.</li>"
        "<li>From R11 on, <b>elemental-law learning speed</b> joins the "
        "top of the list — law levels are a time-integral, so speed "
        "compounds (<a href='app://ref/systems'>Reference → World "
        "Systems</a> covers laws).</li>"
        "</ul>"
        "<h3>R4–R9, rank by rank</h3>"
        "<ul>"
        "<li><b>R4</b> — all three earn their cost: Golden Core (+2%/+3% "
        "pill effect), Astrology (+3% Respira effect, then +1 daily pill "
        "attempt), and Focus at least for its +1% pill effect "
        "unlock.</li>"
        "<li><b>R5</b> — Ninefall is the pick (abode-aura nodes "
        "bracketing +2% pill effect). Bloodization up to its +3% aura "
        "node. Solarics: the aura node for everyone; physical paths "
        "continue for the P.ATK.</li>"
        "<li><b>R6</b> — Yin's Grasp is the standout, take it to Tier 9: "
        "+5% Respira effect, then +1 daily pill attempt. Conflagration "
        "and Unbound Blade stack PvP lines and land Base Abode Aura +3% "
        "at Tier 9. Dragon Flight to Tier 6 (+2% pill effect, +2% "
        "aura).</li>"
        "<li><b>R7</b> — Floral Essence and Purify &amp; Cleanse are the "
        "rank's best, every node good: Floral Essence stacks Respira, "
        "pill effect and +1 pill attempt; Purify &amp; Cleanse is the "
        "Respira manual (instant-complete on learning, +4%/+7% effect, "
        "+1 attempt). Great Yang Manual: weak unlock, good everything "
        "else (+2% aura, +5% Respira, +4% pill effect). Aqua Power (to "
        "Tier 6), Ninefall Hoarfrost and Sunset Halberd Dance are the "
        "PvP picks.</li>"
        "<li><b>R8</b> — Chroma is the must-buy: pill effect, +1 Respira "
        "attempt, +4% aura, +1 pill attempt. Astral Arcanum right behind "
        "it (pill effect plus double aura nodes). Tao of Taiqing: top "
        "pick for magic paths — PvP lines ending in +4% aura. Origin "
        "Scripture: the physical-path all-rounder. Zixiao Sutra: first "
        "two nodes only (+1% pill effect, +2% aura).</li>"
        "<li><b>R9</b> — Harvest God Secret is the cultivation manual of "
        "the rank: +3% Respira, +3%/+4% aura, +1 pill attempt. Honored "
        "Origin: bought for its aura nodes, the control stats are a "
        "bonus. Divine Water (magic) and Heartless (physical, ends in "
        "+10% Respira) are the PvP picks. Laws of Nature: the +1% pill "
        "effect unlock early; Tier 12 adds +10% Respira effect.</li>"
        "</ul>"
        "<h3>R10 and beyond</h3>"
        "<p>Everything at R10 is worth taking — Immortal Ascension "
        "(the rank's only Universal book) to Tier 12 for its +1 daily "
        "pill attempt; Tier 15 beyond that is stats-only. From R11 the "
        "ranks settle into a "
        "pattern: each has a law-speed manual (rated S across the "
        "board), usually an abode-aura or Respira manual, and a PvP "
        "manual. New node families appear here: elemental-law learning "
        "speed, Qiyun efficiency, and divine/demonic damage.</p>"
        "<h3>Every Universal manual, rated</h3>"
        "<table cellpadding='4' cellspacing='0' border='1' "
        "style='border-collapse:collapse'>"
        "<tr><th>Rank</th><th>Manual</th><th>Rating</th><th>Why</th></tr>"
        + "".join(
            f"<tr><td>{r}</td><td>{n}</td><td>{g}</td><td>{w}</td></tr>"
            for r, n, g, w in manual_rows) +
        "</table>"
        "<p>Manuals above R9 aren't on the Vault shelves yet — add "
        "their pill/Respira bonuses as custom rows in the calculator's "
        "source pickers so projections see them.</p>")

    # Spending advice is community consensus (2026 guide + Discord);
    # BR figures are era-specific estimates, not client data.
    spending = (
        "<h2>Spending (if you pay at all)</h2>"
        "<p>None of this is a recommendation to spend — it's an "
        "answer to \"if I do, what's actually worth it?\" "
        "All of it is subjective.</p>"
        "<h3>Priorities</h3><ul>"
        "<li><b>Permanent one-time buys first</b>: the watering curio "
        "set and the permanent passes beat any consumable pack — you "
        "buy them once and they pay out forever.</li>"
        "<li>The <b>three elixir packs on reaching a new realm</b> are "
        "among the best consumable value in the game (early tolerance "
        "tiers make them worth the most — see <a href='app://ref/"
        "elixirs#tolerance'>Reference → Elixirs &amp; Stat Pills</a>).</li>"
        "<li>The daily 30 Fateum/Destium <b>artifact charges</b> are "
        "among the cheapest EXP money buys.</li>"
        "<li><b>Law fruit packs are atrocious value — do not buy "
        "them.</b></li>"
        "<li>Heavy <b>pet</b> investment is whale territory "
        "(<a href='app://guide/pets'>Guide → Pets</a>).</li>"
        "</ul>"
        "<h3>Timegate BR targets (era-specific estimates)</h3>"
        "<p>Rough battle-rating bands players aim for at each "
        "realm's timegate content, by spending tier (F2P → heavy). "
        "These drift with every era — treat as orientation only:</p>"
        "<ul><li><b>Incarnation</b>: 800m – 2b+</li>"
        "<li><b>Voidbreak</b>: 9b – 25b+</li>"
        "<li><b>Wholeness</b>: 45b – 100b+</li></ul>")

    return [(slug, title, html + footer) for slug, title, html in (
        ("paths", "Choosing a Path", paths),
        ("server", "Server Timeline", server),
        ("routine", "Daily Routine", routine),
        ("novice", "Novice–Foundation", novice),
        ("virtuoso", "Virtuoso", virtuoso),
        ("nascent", "Nascent Soul", nascent),
        ("incarnation", "Incarnation", incarnation),
        ("timegate", "Timegate", timegate),
        ("voidbreak", "Voidbreak+", voidbreak),
        ("pets", "Pets", pets),
        ("aux", "Aux Paths", aux),
        ("techniques", "Techniques", techniques),
        ("spending", "Spending", spending),
    )]
