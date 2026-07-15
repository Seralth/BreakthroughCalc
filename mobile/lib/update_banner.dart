/// Startup / manual release check and its banner + release dialog UI.
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show Clipboard, ClipboardData;
import 'package:shared_preferences/shared_preferences.dart';

import 'i18n.dart';
import 'update_check.dart';

/// Fallback when the release payload carries no browser URL.
const releasesLatestUrl =
    'https://github.com/Seralth/BreakthroughCalc/releases/latest';

/// Checks GitHub for a newer release. Silent on failure; on startup
/// ([manual] false) it only shows a banner for a not-yet-dismissed newer
/// version, while a manual check also reports "up to date" / failures.
Future<void> checkForUpdates(
    BuildContext context, SharedPreferences prefs, String appVersion,
    {bool manual = false}) async {
  final rel = await fetchLatestRelease(appVersion);
  if (!context.mounted) return;
  final local = parseVersion(appVersion);
  final remote = rel == null ? null : parseVersion(rel.tag);
  if (rel == null || local == null || remote == null || !isNewerVersion(remote, local)) {
    if (manual) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(rel == null
            ? tr('Update check failed — are you online?')
            : '${tr('Up to date')} (v$appVersion)'),
      ));
    }
    return;
  }
  final version = remote.join('.');
  if (!manual && prefs.getString('dismissed_update') == version) return;
  final messenger = ScaffoldMessenger.of(context);
  messenger.hideCurrentMaterialBanner();
  messenger.showMaterialBanner(MaterialBanner(
    content: Text('${tr('Update available')}: v$version'),
    leading: const Icon(Icons.system_update_alt),
    actions: [
      TextButton(
        onPressed: () {
          messenger.hideCurrentMaterialBanner();
          showReleaseDialog(context, version, rel.url);
        },
        child: Text(tr('View')),
      ),
      TextButton(
        onPressed: () {
          messenger.hideCurrentMaterialBanner();
          prefs.setString('dismissed_update', version);
        },
        child: Text(tr('Dismiss')),
      ),
    ],
  ));
}

void showReleaseDialog(BuildContext context, String version, String url) {
  if (!context.mounted) return;
  final effective = url.isEmpty ? releasesLatestUrl : url;
  showDialog<void>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text('${tr('Update available')}: v$version'),
      content: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(tr('Open this link in your browser to download the release:')),
        const SizedBox(height: 8),
        SelectableText(effective),
      ]),
      actions: [
        TextButton(
          onPressed: () {
            Clipboard.setData(ClipboardData(text: effective));
            Navigator.pop(ctx);
            ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(tr('Link copied'))));
          },
          child: Text(tr('Copy link')),
        ),
        TextButton(onPressed: () => Navigator.pop(ctx), child: Text(tr('Close'))),
      ],
    ),
  );
}
