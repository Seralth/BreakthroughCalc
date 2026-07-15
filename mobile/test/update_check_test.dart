import 'package:flutter_test/flutter_test.dart';

import 'package:breakthrough_calc/update_check.dart';

void main() {
  group('parseVersion', () {
    test('plain and prefixed forms', () {
      expect(parseVersion('2.7'), [2, 7, 0]);
      expect(parseVersion('v2.7.1'), [2, 7, 1]);
      expect(parseVersion('V2.14'), [2, 14, 0]);
      expect(parseVersion('  2.14 '), [2, 14, 0]);
      expect(parseVersion('3'), [3, 0, 0]);
    });

    test('prerelease/build suffixes are ignored', () {
      expect(parseVersion('2.8.0-rc1'), [2, 8, 0]);
      expect(parseVersion('2.14.0+19'), [2, 14, 0]);
      expect(parseVersion('v2.9-beta+5'), [2, 9, 0]);
    });

    test('unparseable returns null', () {
      expect(parseVersion(''), isNull);
      expect(parseVersion('v'), isNull);
      expect(parseVersion('abc'), isNull);
      expect(parseVersion('1.2.3.4'), isNull);
      expect(parseVersion('1..2'), isNull);
      expect(parseVersion('1.-2'), isNull);
    });
  });

  group('isNewerVersion', () {
    test('ordering', () {
      expect(isNewerVersion([2, 14, 0], [2, 12, 0]), isTrue);
      expect(isNewerVersion([2, 12, 0], [2, 14, 0]), isFalse);
      expect(isNewerVersion([2, 14, 0], [2, 14, 0]), isFalse);
      expect(isNewerVersion([3, 0, 0], [2, 99, 99]), isTrue);
      expect(isNewerVersion([2, 14, 1], [2, 14, 0]), isTrue);
    });
  });
}
