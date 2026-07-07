import 'dart:convert';
import 'dart:io';

/// Latest GitHub release, or null on any failure (offline, timeout, bad
/// JSON, ...). Never throws.
Future<({String tag, String url})?> fetchLatestRelease(String appVersion) async {
  HttpClient? client;
  try {
    client = HttpClient()..connectionTimeout = const Duration(seconds: 5);
    final req = await client
        .getUrl(Uri.parse(
            'https://api.github.com/repos/Seralth/BreakthroughCalc/releases/latest'))
        .timeout(const Duration(seconds: 5));
    req.headers.set(HttpHeaders.userAgentHeader, 'BreakthroughCalc/$appVersion');
    req.headers.set(HttpHeaders.acceptHeader, 'application/vnd.github+json');
    final resp = await req.close().timeout(const Duration(seconds: 5));
    if (resp.statusCode != 200) return null;
    final body = await resp
        .transform(utf8.decoder)
        .join()
        .timeout(const Duration(seconds: 5));
    final json = jsonDecode(body);
    if (json is! Map<String, dynamic>) return null;
    final tag = json['tag_name'];
    final url = json['html_url'];
    if (tag is! String) return null;
    return (tag: tag, url: url is String ? url : '');
  } catch (_) {
    return null;
  } finally {
    client?.close(force: true);
  }
}
