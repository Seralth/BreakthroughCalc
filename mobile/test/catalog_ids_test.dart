// Append-only guard for catalog source ids (the Dart twin of
// tests/test_shelf.py's KNOWN_IDS / test_id_set_is_append_only).
//
// Once shelf/Vault build codes ship, a source id travels inside the OMV2
// share code (see share_codec.dart's S carry) — so renaming or removing an
// id silently breaks every previously shared build that referenced it. The
// set below is APPEND-ONLY: a red here means an id was renamed or dropped,
// never that a newly added id is missing.
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

// Representative anchor ids across every catalog category. Not exhaustive
// (~800 curios exist) — a durable spine that catches a rename/removal.
const knownIds = <String>[
  // technique_book
  'longevity', 'energy_unification', 'rejuvenation', 'lifeboom', 'focus',
  'golden_core', 'astrology', 'ninefall', 'cosmic_power', 'taiyin_meridian',
  'dragon_flight', 'yins_grasp', 'lions_roar', 'floral_essence',
  'great_yang_manual', 'purify_cleanse', 'zixiao_sutra', 'astral_arcanum',
  'chroma', 'cauldron_refinement', 'moon_meru',
  // immortal_friend
  'princess_iron_fan', 'daji', 'shen_gongbao', 'six_eared_macaque',
  'jiang_ziya', 'taotie', 'crane_boy', 'white_astra', 'princess_adalinda',
  'leizhenzi',
  // blessing
  'ascension_virya',
  // curio
  'yang_spirit_jade', 'dongxuans_pot', 'pisces_pendant', 'dongxuans_lantern',
  'dongxuans_cushion', 'northern_mirror', 'spirit_seal_bowl',
  'spirit_seal_gourd',
];

Map loadCatalog() =>
    jsonDecode(File('../data/sources.json').readAsStringSync()) as Map;

void main() {
  final catalog = loadCatalog();

  test('known source ids are all present (append-only wire guard)', () {
    final ids = {
      for (final s in (catalog['sources'] as List)) (s as Map)['id'] as String
    };
    for (final known in knownIds) {
      expect(ids, contains(known),
          reason: 'source id "$known" is missing — ids are OMV2 wire data, '
              'append-only; a rename/removal breaks shared build codes');
    }
  });
}
