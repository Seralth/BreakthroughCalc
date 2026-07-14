import 'dart:js_interop';

@JS('forceRefresh')
external void _forceRefresh();

/// Unregisters service workers, wipes CacheStorage, and reloads cache-busted.
/// Implemented in web/index.html (window.forceRefresh).
void forceRefresh() => _forceRefresh();
