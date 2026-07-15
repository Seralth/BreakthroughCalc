> **Name corrections (2026-07-15, verified against the APK i18n string
> corpus; applied in data/sources.json):** "Iron Fan" → **Princess Iron
> Fan**; "Macaque" → **Six Eared Macaque**; "Dragon's Flight" → **Dragon
> Flight** (no apostrophe). The Ascension Virya tier ladder is officially
> **Completion / Eminence / Perfection / Half Step** (ratings 1/3/5/7) —
> the community's "Perfection (C)" / "Perfect" tier names collide with
> Stage names and are replaced. "Ninefall Hoarfrost" is a distinct book
> from "Ninefall". Timereversal Pearl is absent from this APK build's
> strings (predates it) — community name retained.

{
  "catalog_version": "candidate-1 (Track A inventory, 2026-07-15)",
  "provenance": {
    "read": [
      "/home/seralth/Projects/Cultivation Clac/BreakthroughCalc/data/pill_effect_sources.json",
      "/home/seralth/Projects/Cultivation Clac/BreakthroughCalc/data/respira_sources.json",
      "/home/seralth/Projects/Cultivation Clac/BreakthroughCalc/docs/knowledge/game-mechanics-verified.md",
      "/home/seralth/Projects/Cultivation Clac/BreakthroughCalc/docs/knowledge/elixir-sense-mechanics.md",
      "/home/seralth/Projects/Cultivation Clac/BreakthroughCalc/docs/knowledge/combat-mechanics.md",
      "/home/seralth/Projects/Cultivation Clac/BreakthroughCalc/breakthrough_calc/docs.py",
      "/home/seralth/Projects/Cultivation Clac/BreakthroughCalc/breakthrough_calc/fields.py (field-key alignment)",
      "/home/seralth/Projects/Cultivation Clac/BreakthroughCalc/mobile/lib/guide_tab.dart"
    ],
    "note": "Field keys below match breakthrough_calc/fields.py registry keys exactly. Mobile guide_tab.dart is a strict subset of desktop docs.py — no desktop-missing sources found in it."
  },

  "target_field_classification": {
    "raw_additive_safe": {
      "description": "Shelf may derive these by summing owned-source effects (pp = percentage points, additive per in-game convention).",
      "fields": ["respira_per_day", "respira_books", "respira_event", "pill_limit", "pill_effect", "mark_gold", "mark_purple", "mark_blue", "bless_pp", "bless_window_pp", "bless_window", "elixir_per_day", "elixir_effect", "aura_gem", "vase", "vase_star", "vase_skin", "vase_charge", "mirror", "mirror_star", "mirror_skin", "mirror_charge", "pearl", "pearl_star", "pearl_skin", "pearl_charge", "lvl_culti", "lvl_quality", "lvl_gush", "extractor_rarity", "fruit_highest_rank"]
    },
    "display_embedded": {
      "description": "Entered as-displayed-in-game and ALREADY include source effects. The shelf must NEVER add source values on top; only derive via explicit models (see models key) or leave user-entered.",
      "fields": {
        "respira_exp": "Displayed per-attempt value = per-Stage server base x (1 + respira_books%). Includes Macaque +3% and all book %. Only derivable via the stage-base model.",
        "culti_speed": "On-screen Cultivation Speed = abode x absorption (incl. strive, blessing pp, Virya, Heavenly Power). Never add anything.",
        "absorption_ratio": "On-screen TOTAL incl. strive + blessing pp; engine already strips current-row blessing using bless_pp/bless_window_pp to recover true Strive — bless_pp inputs are safe BECAUSE the engine does this stripping.",
        "abode_aura": "Includes Energy Array, aura curios, sect level, technique-book Base Abode Aura lines (deliberately uncataloged to avoid double-count).",
        "pearl_xp_per_10": "Pearl tooltip EXP scales with the player's own cultivation bonuses — always read from tooltip, never derive."
      }
    }
  },

  "sources": [
    {"name": "Longevity", "category": "book", "rank": "Novice", "tiers": [{"threshold": "maxed (cheapest before Foundation breakthrough)", "effects": [{"target_field": "respira_per_day", "value": 1, "unit": "attempts/day"}]}], "data_status": "known"},
    {"name": "Energy Unification", "category": "book", "rank": "Foundation-era", "tiers": [{"threshold": "on activation", "effects": [{"target_field": "respira_books", "value": 1, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Rejuvenation", "category": "book", "rank": "R2", "tiers": [{"threshold": "completion", "effects": [{"target_field": "pill_effect", "value": 2, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Lifeboom", "category": "book", "rank": "R3", "tiers": [{"threshold": "completion", "effects": [{"target_field": "pill_effect", "value": 1, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Focus", "category": "book", "rank": "R4", "tiers": [{"threshold": "completion", "effects": [{"target_field": "pill_effect", "value": 1, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Golden Core", "category": "book", "rank": "R4", "tiers": [{"threshold": "completion (split +2 and +3)", "effects": [{"target_field": "pill_effect", "value": 5, "unit": "pp"}]}, {"threshold": "? (tier for Respira line not recorded)", "effects": [{"target_field": "respira_books", "value": 1, "unit": "pp"}]}], "data_status": "partial", "gap": "which tier grants the Respira +1%"},
    {"name": "Astrology", "category": "book", "rank": "R4", "tiers": [{"threshold": "? (tier not recorded)", "effects": [{"target_field": "respira_books", "value": 3, "unit": "pp"}]}, {"threshold": "Tier 7 (roadmap-recommended)", "effects": [{"target_field": "?", "value": "?", "unit": "?"}]}], "data_status": "partial", "gap": "T7 payoff unknown; tier of the +3% line unknown"},
    {"name": "Ninefall", "category": "book", "rank": "R5", "tiers": [{"threshold": "completion", "effects": [{"target_field": "pill_effect", "value": 2, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Bloodization", "category": "book", "rank": "R5", "tiers": [{"threshold": "Tier 7 (roadmap-recommended)", "effects": [{"target_field": "?", "value": "?", "unit": "?"}]}], "data_status": "unknown", "gap": "payoff unknown — may be combat-only (no calculator effect)"},
    {"name": "Cosmic Power", "category": "book", "rank": "?", "tiers": [{"threshold": "? (tier not recorded)", "effects": [{"target_field": "respira_per_day", "value": 1, "unit": "attempts/day"}, {"target_field": "respira_books", "value": 3, "unit": "pp"}]}], "data_status": "partial", "gap": "rank and tier thresholds unknown"},
    {"name": "Taiyin Meridian", "category": "book", "rank": "?", "tiers": [{"threshold": "? (tier not recorded)", "effects": [{"target_field": "respira_books", "value": 3, "unit": "pp"}]}], "data_status": "partial", "gap": "rank and tier threshold unknown"},
    {"name": "Dragon Flight (Dragon's Flight)", "category": "book", "rank": "R6", "tiers": [{"threshold": "Tier 3", "effects": [{"target_field": "pill_effect", "value": 2, "unit": "pp"}]}, {"threshold": "Tier 10 (roadmap-recommended)", "effects": [{"target_field": "?", "value": "?", "unit": "?"}]}], "data_status": "partial", "gap": "payoffs above T3 unknown"},
    {"name": "Yin's Grasp", "category": "book", "rank": "R6", "tiers": [{"threshold": "? (tier not recorded)", "effects": [{"target_field": "respira_books", "value": 5, "unit": "pp"}]}, {"threshold": "Tier 10 (roadmap-recommended)", "effects": [{"target_field": "?", "value": "?", "unit": "?"}]}], "data_status": "partial", "gap": "T10 payoff unknown"},
    {"name": "Lion's Roar", "category": "book", "rank": "R6", "prerequisite": "Blazelion pet owned", "tiers": [{"threshold": "on learning", "effects": [{"target_field": "respira_books", "value": 1, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Floral Essence", "category": "book", "rank": "R7", "tiers": [{"threshold": "? (tier not recorded)", "effects": [{"target_field": "respira_books", "value": 3, "unit": "pp"}]}, {"threshold": "Tier 6", "effects": [{"target_field": "pill_effect", "value": 3, "unit": "pp"}]}, {"threshold": "Tier 9", "effects": [{"target_field": "pill_limit", "value": 1, "unit": "attempts/day"}]}], "data_status": "partial", "gap": "tier of the Respira +3% line unknown"},
    {"name": "Great Yang Manual", "category": "book", "rank": "R7", "tiers": [{"threshold": "? (tier not recorded)", "effects": [{"target_field": "respira_books", "value": 5, "unit": "pp"}]}, {"threshold": "Tier 9", "effects": [{"target_field": "pill_effect", "value": 4, "unit": "pp"}]}], "data_status": "partial", "gap": "tier of the Respira +5% line unknown"},
    {"name": "Purify & Cleanse", "category": "book", "rank": "?", "tiers": [{"threshold": "on activation", "effects": [{"target_field": "respira_books", "value": 4, "unit": "pp"}, {"target_field": "respira_per_day", "value": 1, "unit": "attempts/day"}]}, {"threshold": "Tier 9", "effects": [{"target_field": "respira_books", "value": 7, "unit": "pp"}]}], "data_status": "partial", "gap": "rank unknown; also grants complete-all-Respira QoL (no calc effect)"},
    {"name": "Zixiao Sutra", "category": "book", "rank": "R8", "tiers": [{"threshold": "on learning", "effects": [{"target_field": "pill_effect", "value": 1, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Astral Arcanum", "category": "book", "rank": "R8", "tiers": [{"threshold": "Tier 3", "effects": [{"target_field": "pill_effect", "value": 2, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Chroma", "category": "book", "rank": "R8", "tiers": [{"threshold": "on learning", "effects": [{"target_field": "pill_effect", "value": 1, "unit": "pp"}]}, {"threshold": "Tier 3", "effects": [{"target_field": "respira_per_day", "value": 1, "unit": "attempts/day"}]}, {"threshold": "Tier 6", "effects": [{"target_field": "pill_effect", "value": 3, "unit": "pp"}]}, {"threshold": "Tier 12", "effects": [{"target_field": "pill_limit", "value": 1, "unit": "attempts/day"}]}], "data_status": "known"},
    {"name": "Cauldron Refinement", "category": "book", "rank": "R8", "tiers": [{"threshold": "Tier 3", "effects": [{"target_field": "respira_books", "value": 3, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Moon Meru", "category": "book", "rank": "R8", "tiers": [{"threshold": "Tier 12", "effects": [{"target_field": "respira_books", "value": 10, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Tao of Taiqing", "category": "book", "rank": "R8", "tiers": [], "data_status": "partial", "gap": "pill-effect lines: verified NONE (complete coverage); Respira/attempt lines: not explicitly confirmed absent"},
    {"name": "Origin Scripture", "category": "book", "rank": "R8", "tiers": [], "data_status": "partial", "gap": "same as Tao of Taiqing"},
    {"name": "No-Thought Sutra", "category": "book", "rank": "R8", "tiers": [], "data_status": "partial", "gap": "same as Tao of Taiqing"},
    {"name": "Dracophant", "category": "book", "rank": "R8", "tiers": [], "data_status": "partial", "gap": "same as Tao of Taiqing"},
    {"name": "R9 technique books (all)", "category": "book", "rank": "R9", "tiers": [{"threshold": "?", "effects": [{"target_field": "?", "value": "?", "unit": "?"}]}], "data_status": "unknown", "gap": "book list and every effect unknown — roadmap has no R9 picks either"},
    {"name": "Immortal Ascension", "category": "book", "rank": "R10", "tiers": [{"threshold": "Tier 13 (roadmap-recommended)", "effects": [{"target_field": "?", "value": "?", "unit": "?"}]}], "data_status": "unknown", "gap": "payoff unknown"},

    {"name": "Iron Fan", "category": "friend", "tiers": [{"threshold": "level 36", "effects": [{"target_field": "respira_per_day", "value": 1, "unit": "attempts/day"}]}], "data_status": "known"},
    {"name": "Daji", "category": "friend", "tiers": [{"threshold": "level 73", "effects": [{"target_field": "respira_per_day", "value": 1, "unit": "attempts/day"}]}], "data_status": "known"},
    {"name": "Shen Gongbao", "category": "friend", "tiers": [{"threshold": "level 117", "effects": [{"target_field": "respira_per_day", "value": 1, "unit": "attempts/day"}]}], "data_status": "known"},
    {"name": "Macaque", "category": "friend", "tiers": [{"threshold": "level 17", "effects": [{"target_field": "respira_exp", "value": 3, "unit": "pct", "display_embedded": true}]}], "data_status": "known", "flags": ["DISPLAY-EMBEDDED: already inside the in-game Respira EXP tooltip — informational chip only, NEVER added to any input"]},
    {"name": "Crane Boy", "category": "friend", "tiers": [{"threshold": "max level (numeric level = ?)", "effects": [{"target_field": "pill_limit", "value": 1, "unit": "attempts/day"}]}], "data_status": "partial", "gap": "max-level number unknown"},
    {"name": "Jiang Ziya", "category": "friend", "tiers": [{"threshold": "level 116", "effects": [{"target_field": "pill_effect", "value": 3, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Taotie", "category": "friend", "tiers": [{"threshold": "level 117", "effects": [{"target_field": "pill_effect", "value": 3, "unit": "pp"}]}], "data_status": "known"},
    {"name": "White Astra", "category": "friend", "tiers": [{"threshold": "level 31 (roadmap-recommended)", "effects": [{"target_field": "?", "value": "?", "unit": "?"}]}], "data_status": "unknown", "gap": "payoff unknown"},
    {"name": "Princess Adalinda", "category": "friend", "tiers": [{"threshold": "level 81 (roadmap-recommended)", "effects": [{"target_field": "?", "value": "?", "unit": "?"}]}], "data_status": "unknown", "gap": "payoff unknown"},
    {"name": "Leizhenzi", "category": "friend", "tiers": [{"threshold": "level 129 (roadmap-recommended)", "effects": [{"target_field": "?", "value": "?", "unit": "?"}]}], "data_status": "unknown", "gap": "payoff unknown"},

    {"name": "Ascension Virya — Completion tier", "category": "blessing", "per_path": true, "tiers": [{"threshold": "Reach Incarnation (L) Late 100% and break through", "effects": [{"target_field": "none_numeric", "value": "removes realm restriction on Cultivation Pills (enables feeding higher-stage pills to the lower secondary path) + pill auto-transmog privilege + Blessing Rewards +1", "unit": "qualitative"}]}], "data_status": "known", "notes": "No absorption bonus at this tier; matters to a future secondary-path projection (better pill ranks)."},
    {"name": "Ascension Virya — Perfection (C) tier", "category": "blessing", "per_path": true, "tiers": [{"threshold": "primary Incarnation (L) Completion + secondary Nascent Soul (L) Late + clear Amethyst Fiend (Myrimon Wonder)", "effects": [{"target_field": "bless_pp", "value": 20, "unit": "pp"}]}], "data_status": "known", "notes": "Persistent (named for tier, not windowed) per 2-player community model; additive pp per 3rd confirmation. Pending one tooltip-grade in-game verification (40%-band + tier should read 60%, not 48%)."},
    {"name": "Ascension Virya — Perfect tier (gold)", "category": "blessing", "per_path": true, "tiers": [{"threshold": "secondary Incarnation (L) Middle + clear Jade-Eyed Lion (Myrimon Wonder)", "effects": [{"target_field": "bless_pp", "value": 20, "unit": "pp"}, {"target_field": "bless_window_pp", "value": 20, "unit": "pp", "window": "until passing Voidbreak (L) Middle"}]}], "data_status": "known", "notes": "Stacks with Perfection (C) to +40 persistent, +60 total before Voidbreak Middle. Also Blessing Rewards +5 and Second Esotability."},
    {"name": "Ascension Virya — further tiers", "category": "blessing", "tiers": [{"threshold": "?", "effects": [{"target_field": "?", "value": "?", "unit": "?"}]}], "data_status": "unknown", "gap": "whether tiers beyond the three observed exist"},
    {"name": "Post-ascension privileges", "category": "blessing", "tiers": [{"threshold": "? (after ascension to Immortal World)", "effects": [{"target_field": "bless_pp", "value": 200, "unit": "pp"}, {"target_field": "none_numeric", "value": "high-stage pill access", "unit": "qualitative"}]}], "data_status": "partial", "gap": "dump-only; tier structure and exact conditions unknown"},
    {"name": "Virya session (Double, x2 Cosmoapsis)", "category": "blessing", "transient": true, "tiers": [{"threshold": "while session countdown runs", "effects": [{"target_field": "culti_speed", "value": 2, "unit": "x-multiplier", "display_embedded": true}]}], "data_status": "partial", "flags": ["TRANSIENT + DISPLAY-EMBEDDED hazard: shelf should WARN users not to read culti_speed/absorption while a Virya session is active"], "gap": "plausible inference (unclickable Double badge), unverified"},

    {"name": "Yang Spirit Jade", "category": "curio", "rarity": "Epic", "model": {"kind": "star_upgrade", "base": 1.0, "per_upgrade": 0.2, "max_upgrade": 8, "stars": 5, "star_add": [0.0, 0.8, 1.2, 2.2, 3.2]}, "tiers": [{"threshold": "owned, upgrade level 0-8 + star 1-5", "effects": [{"target_field": "pill_effect", "value": "1.0 + 0.2*upgrade + star_add[star]", "unit": "pp", "max": 5.8}]}], "data_status": "known", "notes": "Shelf needs TWO sub-inputs: upgrade level (0-8) and star (1-5). Prompt model already in data/pill_effect_sources.json."},
    {"name": "Dongxuan's Pot", "category": "curio", "rarity": "Special", "tiers": [{"threshold": "owned (no upgrades/stars)", "effects": [{"target_field": "pill_effect", "value": 2, "unit": "pp"}]}], "data_status": "known"},
    {"name": "Other cultivation-bonus curios", "category": "curio", "tiers": [{"threshold": "?", "effects": [{"target_field": "?", "value": "?", "unit": "?"}]}], "data_status": "unknown", "gap": "Reference prose says 'several curios carry cultivation bonuses (pill effect, Respira)' — coverage beyond Yang Spirit Jade + Dongxuan's Pot NOT confirmed complete; any Respira-effect curio would also be display-embedded via respira_exp"},
    {"name": "Aura curios (abode-aura bonus family)", "category": "curio", "tiers": [{"threshold": "varies", "effects": [{"target_field": "abode_aura", "value": "?", "unit": "pct", "display_embedded": true}]}], "data_status": "unknown", "flags": ["DISPLAY-EMBEDDED: inside the entered Abode Aura reading — shelf records ownership for the advisor only, never derives"]},

    {"name": "Starsea Vase", "category": "artifact", "tiers": [{"threshold": "owned", "effects": [{"target_field": "vase", "value": true, "unit": "flag"}]}, {"threshold": "1 star", "effects": [{"target_field": "vase_star", "value": 10, "unit": "pct EXP on refined red pills"}]}, {"threshold": "3 stars", "effects": [{"target_field": "vase_star", "value": 20, "unit": "pct EXP on refined red pills"}]}, {"threshold": "5 stars", "effects": [{"target_field": "vase_star", "value": "15% chance refine consumes no energy", "unit": "proc"}]}], "constants": {"refine_cost_by_rank": "data/breakthrough.json vase_energy_cost (default 100)", "epic_refine_discount_pct": 5, "legendary_refine_discount_pct": 20, "energy_regen_0star": "1 per 15 min", "energy_cap_0star": 200, "daily_charge": "+100 energy for 30 Fateum/Destium"}, "data_status": "partial", "gap": "star 2/4 effects ?; regen/cap per star ?; red-pill tier-unlock structure (which reds Mirror may copy) ?"},
    {"name": "Starsea Vase skin", "category": "skin", "parent": "Starsea Vase", "tiers": [{"threshold": "owned", "effects": [{"target_field": "vase_skin", "value": 8, "unit": "pct EXP on refined red pills"}]}], "data_status": "known"},
    {"name": "Dual-Star Mirror", "category": "artifact", "tiers": [{"threshold": "owned", "effects": [{"target_field": "mirror", "value": true, "unit": "flag"}]}, {"threshold": "1 star", "effects": [{"target_field": "mirror_star", "value": -5, "unit": "pct copy cost"}]}, {"threshold": "3 stars", "effects": [{"target_field": "mirror_star", "value": -10, "unit": "pct copy cost"}]}, {"threshold": "5 stars", "effects": [{"target_field": "mirror_star", "value": "15% chance of extra copy per Duplication", "unit": "proc"}]}], "constants": {"copy_cost_base": 200, "daily_charge": "+100 energy for 30 Fateum/Destium"}, "data_status": "partial", "gap": "star 2/4 effects ?; regen/cap per star ?; whether 1-star -5% and 3-star -10% replace or add ?"},
    {"name": "Dual-Star Mirror skin", "category": "skin", "parent": "Dual-Star Mirror", "tiers": [{"threshold": "owned", "effects": [{"target_field": "mirror_skin", "value": -10, "unit": "pct copy cost"}]}], "data_status": "known"},
    {"name": "Timereversal Pearl", "category": "artifact", "tiers": [{"threshold": "owned", "effects": [{"target_field": "pearl", "value": true, "unit": "flag"}]}, {"threshold": "1 star", "effects": [{"target_field": "pearl_star", "value": 20, "unit": "pct EXP (flat from 1 star, does not grow)"}]}], "constants": {"use_cost": "10 energy", "daily_charge": "+100 energy for 30 Fateum/Destium"}, "data_status": "partial", "gap": "per-star energy-cost discount values ?; star 2-5 effects ?; regen/cap per star ?", "flags": ["pearl_xp_per_10 stays DISPLAY-EMBEDDED (tooltip scales with own culti bonuses — re-read after aura upgrades)"]},
    {"name": "Timereversal Pearl skin", "category": "skin", "parent": "Timereversal Pearl", "tiers": [{"threshold": "owned", "effects": [{"target_field": "pearl_skin", "value": -10, "unit": "pct use cost"}]}], "data_status": "known"},
    {"name": "Artifact daily charges (habit toggles)", "category": "other", "habit": true, "tiers": [{"threshold": "per artifact, per day, 30 Fateum/Destium", "effects": [{"target_field": "vase_charge", "value": 100, "unit": "energy/day"}, {"target_field": "mirror_charge", "value": 100, "unit": "energy/day"}, {"target_field": "pearl_charge", "value": 100, "unit": "energy/day"}]}], "data_status": "known", "notes": "Not ownership — a recurring-spend habit; shelf can host as set-once toggles feeding the existing checkbox inputs."},

    {"name": "Aura Gem", "category": "artifact", "tiers": [{"threshold": "Rare equipped", "effects": [{"target_field": "aura_gem", "value": 16, "unit": "pct culti-speed"}]}, {"threshold": "Epic equipped", "effects": [{"target_field": "aura_gem", "value": 20, "unit": "pct culti-speed"}]}, {"threshold": "Legendary equipped", "effects": [{"target_field": "aura_gem", "value": 24, "unit": "pct culti-speed"}]}], "constants": {"claim_cap_hours": "18-32 by rarity (Legendary = 32, numerically pinned)"}, "data_status": "partial", "gap": "rarities below Rare (exist? values?) ?; per-rarity cap hours between 18 and 32 ?", "notes": "Multiplies cultivation speed ONLY — never pills/Respira. Engine input is the rarity enum, raw-safe."},

    {"name": "Star Marks (quality star marks)", "category": "other", "tiers": [{"threshold": "per color, source-dependent", "effects": [{"target_field": "mark_gold", "value": "?", "unit": "pp (gold pills only)"}, {"target_field": "mark_purple", "value": "?", "unit": "pp (purple pills only)"}, {"target_field": "mark_blue", "value": "?", "unit": "pp (blue pills only)"}]}], "data_status": "unknown", "gap": "which systems grant marks and per-level values ? — currently user-read from tooltips"},
    {"name": "Dao Ancestor (Daozu) treasures", "category": "other", "tiers": [{"threshold": "?", "effects": [{"target_field": "pill_effect", "value": "?", "unit": "pp"}, {"target_field": "mark_gold|mark_purple|mark_blue", "value": "?", "unit": "pp"}]}], "data_status": "unknown", "gap": "Reference prose: 'Dao Ancestor treasures grant it too — read the % from the tooltip'; item list and values ?"},
    {"name": "Lotus Throne", "category": "other", "tiers": [{"threshold": "?", "effects": [{"target_field": "mark_gold|mark_purple|mark_blue", "value": "?", "unit": "pp (quality-specific)"}]}], "data_status": "unknown", "gap": "values and which color(s) ?"},

    {"name": "Aura Extractor tracks", "category": "extractor", "transient": "resets to level 0 on main-Stage breakthrough", "tiers": [{"threshold": "Cultivation track level (lvl_culti)", "effects": [{"target_field": "lvl_culti", "value": "+4 per level", "unit": "pct orb EXP (table in data/breakthrough.json)"}]}, {"threshold": "Quality track level (lvl_quality)", "effects": [{"target_field": "lvl_quality", "value": "raises quality-roll odds (residual-fill model)", "unit": "table"}]}, {"threshold": "Gush track level (lvl_gush)", "effects": [{"target_field": "lvl_gush", "value": "gush_xp multiplier keyed by GUSH level (1.5 base, 2.06 @ lvl 14)", "unit": "table"}]}], "data_status": "known", "notes": "Per-Stage state, not a set-once ownership — shelf should either exclude or mark as per-Stage-resetting section."},
    {"name": "Aura Extractor rarity", "category": "extractor", "transient": "resets to Common on main-Stage breakthrough", "tiers": [{"threshold": "rarity rank Uncommon..Mythic", "effects": [{"target_field": "extractor_rarity", "value": "+20 per rank, cumulative to Mythic (no Common line)", "unit": "pct orb EXP"}]}, {"threshold": "extractor rank matches server's highest Stage", "effects": [{"target_field": "fruit_highest_rank", "value": 50, "unit": "pct base fruit EXP"}]}], "data_status": "known"},

    {"name": "XP elixir stock / tolerance ladder position", "category": "elixir", "tiers": [{"threshold": "per item, lifetime Used count vs ladder", "effects": [{"target_field": "elixir_per_day", "value": "user routine", "unit": "count/day"}, {"target_field": "elixir_effect", "value": "current tier ratio (150/120/100/70/50/30/20/0)", "unit": "pct"}]}], "data_status": "partial", "gap": "XP-elixir ladder widths mostly ? (known: 5R 150%-tier = 20 wide; one 70%-tier = 160 wide observation; 4R 120-tier >= 10); stat-elixir ladders are irrelevant to the calculator"},

    {"name": "Energy Array level", "category": "other", "tiers": [{"threshold": "per level (violetite/frostite/... materials)", "effects": [{"target_field": "abode_aura", "value": "?", "unit": "pct", "display_embedded": true}]}], "data_status": "unknown", "flags": ["DISPLAY-EMBEDDED — inside entered Abode Aura; ownership recorded for advisor only"]},
    {"name": "Sect level bonus", "category": "other", "tiers": [{"threshold": "sect level", "effects": [{"target_field": "abode_aura", "value": "?", "unit": "pct", "display_embedded": true}]}], "data_status": "unknown", "flags": ["DISPLAY-EMBEDDED"]},
    {"name": "Technique-book Base Abode Aura lines", "category": "book", "tiers": [{"threshold": "various books", "effects": [{"target_field": "abode_aura", "value": "deliberately uncataloged", "unit": "pct", "display_embedded": true}]}], "data_status": "known", "flags": ["DISPLAY-EMBEDDED — repo policy: never catalog values (double-count with entered Abode Aura)"]},
    {"name": "Heavenly Power Bonus", "category": "other", "tiers": [{"threshold": "?", "effects": [{"target_field": "culti_speed", "value": "?", "unit": "multiplier", "display_embedded": true}]}], "data_status": "unknown", "flags": ["DISPLAY-EMBEDDED — appears in the official speed formula; values ?"]}
  ],

  "models": [
    {"name": "respira_exp derivation (per-Stage base x books)", "derives": "respira_exp", "formula": "display = stage_base x (1 + respira_books/100), rounded", "stage_bases": {"Nascent Soul": 3157, "Incarnation": 6385, "Voidbreak": "? (predicted base ~12800-12900 if ~2.02 ratio persists — unverified)", "all other Stages": "?"}, "status": "partial — only derivable for Stages with measured bases; otherwise respira_exp stays user-entered. This is the ONLY legal way the shelf touches respira_exp."},
    {"name": "pill EXP composition", "formula": "pill EXP = base[rank][color] x (1 + pill_effect + mark_color [+ vase_star + vase_skin for refined reds])", "status": "known — defines why pill_effect, marks, and vase star/skin are separate additive pp pools"}
  ],

  "excluded_no_calculator_effect": [
    "Pets (explicitly no cultivation effect; Blazelion is only a Lion's Roar prerequisite)",
    "Watering curio set / garden / Elemental Laws (post-Voidbreak damage system, no breakthrough-time input)",
    "Combat gear/affixes/carvings/relics/Immortactic (combat only)",
    "Stat pills and stat elixirs (permanent combat stats only)",
    "Demon Spire, sect dominion, shop currencies (income systems, not calculator inputs)",
    "Event Respira attempts (respira_event stays a transient manual input, not shelf ownership)",
    "Breakthrough elixir packs / Cultivation Bag (consumables, not persistent sources)"
  ],

  "data_gaps": [
    {"item": "Crane Boy max-level number", "need": "the level at which +1 pill attempt lands"},
    {"item": "White Astra 31 / Princess Adalinda 81 / Leizhenzi 129 payoffs", "need": "what each roadmap breakpoint grants"},
    {"item": "Astrology T7, Bloodization T7, Dragon's Flight T10, Yin's Grasp T10, Immortal Ascension (R10) T13 payoffs", "need": "roadmap-recommended tiers with unrecorded effects"},
    {"item": "Tier thresholds for known-value Respira lines", "need": "which tier grants the % for Golden Core/Astrology/Cosmic Power/Taiyin Meridian/Yin's Grasp/Floral Essence/Great Yang Manual (values known, tiers not)"},
    {"item": "Ranks of Cosmic Power / Taiyin Meridian / Purify & Cleanse / Energy Unification", "need": "book rank (affects shelf grouping/advisor cost model)"},
    {"item": "R8 Respira-line completeness", "need": "confirm Tao of Taiqing / Origin Scripture / No-Thought Sutra / Dracophant have no Respira/attempt lines (pill-effect absence IS confirmed)"},
    {"item": "R9 books entirely; more R10 books", "need": "full list + effects"},
    {"item": "Curio coverage", "need": "confirm no cultivation-bonus curios beyond Yang Spirit Jade + Dongxuan's Pot; aura-curio values (display-embedded, advisor-only)"},
    {"item": "Vase/Mirror/Pearl star 2 and 4 effects; per-star energy regen and cap; Pearl per-star cost discounts; Mirror discount stacking semantics (replace vs add)", "need": "artifact screens at each star"},
    {"item": "Vase red-pill tier-unlock structure", "need": "which refined reds exist per Vase tier (gates Mirror copies)"},
    {"item": "Aura Gem below Rare", "need": "do Common/Uncommon gems exist, and per-rarity claim-cap hours"},
    {"item": "Star Mark sources and per-level pp values; Daozu treasure list/values; Lotus Throne values", "need": "currently user-read only"},
    {"item": "Ascension Virya: tiers beyond the three observed; post-ascension privilege structure; tooltip-grade verification that blessing pp are additive (40%-band + 20 should read 60%)", "need": "screenshots"},
    {"item": "Respira per-Stage bases beyond Nascent (3,157) and Incarnation (6,385)", "need": "one display reading per Stage (Voidbreak predicted ~12.8-12.9k)"},
    {"item": "Base Respira attempts per character level (yunqi_limit full table)", "need": "client has 2@lv1 -> 10 default; full ladder unextracted"},
    {"item": "Base daily pill attempt count before bonuses", "need": "what pill_limit is with zero sources owned"},
    {"item": "XP-elixir ladder tier widths (all ranks, all tiers)", "need": "counter screenshots as tiers are crossed"}
  ]
}