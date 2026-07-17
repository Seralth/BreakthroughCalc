/// Startup / manual release check and its banner + release dialog UI.
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show Clipboard, ClipboardData;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

import 'i18n.dart';
import 'update_check.dart';

/// Fallback when the release payload carries no browser URL.
const releasesLatestUrl =
    'https://github.com/Seralth/BreakthroughCalc/releases/latest';

const obtainiumUrl = 'https://obtainium.imranr.dev/';

/// One-time notice that updates can be automated with Obtainium.
/// Sets the prefs flag up front so it can never show twice.
Future<void> maybeShowObtainiumNotice(
    BuildContext context, SharedPreferences prefs) async {
  if (prefs.getBool('obtainium_notice_shown') ?? false) return;
  await prefs.setBool('obtainium_notice_shown', true);
  if (!context.mounted) return;
  await showDialog<void>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(tr('Automatic updates')),
      content: Text(tr(
          'This app can update itself automatically through Obtainium, a '
          'free app that installs new versions straight from this '
          "project's releases. Add this app there once and every update "
          'arrives as a notification — no more manual downloads.')),
      actions: [
        TextButton(
          onPressed: () {
            launchUrl(Uri.parse(obtainiumUrl),
                mode: LaunchMode.externalApplication);
            Navigator.pop(ctx);
          },
          child: Text(tr('Get Obtainium')),
        ),
        TextButton(
            onPressed: () => Navigator.pop(ctx), child: Text(tr('Close'))),
      ],
    ),
  );
}

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
