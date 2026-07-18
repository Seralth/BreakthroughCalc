// One-off: prints a fixed OMV2 code carrying the Vault, for the golden
// decode pin in test/share_codec_test.dart. Run from mobile/:
//   dart run tool/gen_shelf_golden.dart
import 'dart:convert';
import 'dart:io';

import 'package:breakthrough_calc/engine.dart';
import 'package:breakthrough_calc/share_codec.dart';

void main() {
  final e = Engine(jsonDecode(
          File('../data/breakthrough.json').readAsStringSync())
      as Map<String, dynamic>);
  final inp = Inputs.fromMap(<String, dynamic>{});
  inp.stage = 'Incarnation';
  inp.phase = 'LATE';
  inp.grade = 'G5';
  inp.respiraPerDay = 16.0;
  inp.pillLimit = 9.0;
  final code = encodeBuildCode(
      e,
      inp,
      [
        ['Vault (books & curios)', 11.5],
        ['Event buff', 2.0],
      ],
      {},
      shelfOwned: {
        'ascension_virya': 3,
        'crane_boy': -1,
        'yang_spirit_jade': [4, 8],
        'zz_future_source': 7,
      });
  stdout.writeln(code);
}
