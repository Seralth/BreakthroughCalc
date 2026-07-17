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

/// One reminder after 10 launches; "Maybe later" (or dismissing) re-asks
/// in 60 days, Donate / "Don't ask again" never again. Twin of
/// MainWindow._maybe_donation_nag on desktop.
Future<void> maybeShowDonationNag(BuildContext context,
    SharedPreferences prefs, VoidCallback onDonate) async {
  final state = prefs.getString('donate_nag') ?? '';
  if (state == 'never') return;
  final launches = (prefs.getInt('launch_count') ?? 0) + 1;
  await prefs.setInt('launch_count', launches);
  if (launches < 10) return;
  final now = DateTime.now().millisecondsSinceEpoch;
  if (state == 'later' && now < (prefs.getInt('donate_nag_due') ?? 0)) {
    return;
  }
  await prefs.setString('donate_nag', 'later');
  await prefs.setInt(
      'donate_nag_due', now + const Duration(days: 60).inMilliseconds);
  if (!context.mounted) return;
  await showDialog<void>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(tr('Enjoying the calculator?')),
      content: Text(tr(
          'This app is free and always will be. If it has been useful, '
          'you can support development with a donation — sent as an '
          'in-game voucher gift.')),
      actions: [
        TextButton(
          onPressed: () {
            prefs.setString('donate_nag', 'never');
            Navigator.pop(ctx);
            onDonate();
          },
          child: Text(tr('Donate')),
        ),
        TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(tr('Maybe later'))),
        TextButton(
          onPressed: () {
            prefs.setString('donate_nag', 'never');
            Navigator.pop(ctx);
          },
          child: Text(tr("Don't ask again")),
        ),
      ],
    ),
  );
}

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
