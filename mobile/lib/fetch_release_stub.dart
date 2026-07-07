/// Web build: no update check — a PWA always serves the latest version.
Future<({String tag, String url})?> fetchLatestRelease(String appVersion) async =>
    null;
