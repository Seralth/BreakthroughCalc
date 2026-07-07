/// Version parsing/comparison plus the latest-release fetch.
///
/// The fetch uses dart:io and is swapped for a no-op stub on web builds
/// (a PWA is always served the latest version, so there is nothing to check).
library;

export 'fetch_release_stub.dart' if (dart.library.io) 'fetch_release_io.dart';

/// Parse a version string like "2.7", "v2.7.1" or "2.8.0-rc1" into exactly
/// three numeric parts (missing parts padded with 0, prerelease/build
/// suffixes ignored). Returns null if unparseable.
List<int>? parseVersion(String raw) {
  var s = raw.trim();
  if (s.startsWith('v') || s.startsWith('V')) s = s.substring(1);
  final cut = s.indexOf(RegExp(r'[-+]'));
  if (cut >= 0) s = s.substring(0, cut);
  if (s.isEmpty) return null;
  final parts = s.split('.');
  if (parts.length > 3) return null;
  final nums = <int>[];
  for (final p in parts) {
    final n = int.tryParse(p);
    if (n == null || n < 0) return null;
    nums.add(n);
  }
  while (nums.length < 3) {
    nums.add(0);
  }
  return nums;
}

/// True if [remote] is a strictly newer version than [local].
bool isNewerVersion(List<int> remote, List<int> local) {
  for (var i = 0; i < 3; i++) {
    if (remote[i] != local[i]) return remote[i] > local[i];
  }
  return false;
}
