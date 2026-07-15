/// App-level dialogs: donate, force refresh (PWA), and build-code sharing.
///
/// The donate URL/RID and app version literals stay in main.dart —
/// tests/test_consistency.py pins them there against the desktop package —
/// so the dialogs take them as parameters.
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show Clipboard, ClipboardData;

import 'force_refresh_stub.dart'
    if (dart.library.js_interop) 'force_refresh_web.dart';
import 'i18n.dart';

/// Escape hatch for a wedged PWA cache (the auto-update in index.html is
/// not foolproof, notably on iOS): confirm, then unregister service
/// workers, wipe caches, and reload fresh from the network.
void confirmForceRefresh(BuildContext context,
    {required String appVersion, required String buildStamp}) {
  showDialog<void>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(tr('Force refresh?')),
      content: Text(
          '${tr('Reloads the app fresh from the server, clearing the offline '
              'cache. Use this if an update seems stuck. Your inputs are '
              'saved and will survive.')}'
          '\n\n${tr('Current build')}: v$appVersion · $buildStamp'),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(ctx),
          child: Text(tr('Cancel')),
        ),
        FilledButton(
          onPressed: () {
            Navigator.pop(ctx);
            forceRefresh();
          },
          child: Text(tr('Refresh')),
        ),
      ],
    ),
  );
}

/// Copy-based flow kept deliberately (SEAGM has no URL prefill, so the
/// user must paste the RID by hand anyway; a dialog keeps both visible).
void showDonateDialog(BuildContext context,
    {required String donateUrl, required String donateRid}) {
  showDialog<void>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(tr('Support the calculator')),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('${tr('If the calculator saves you time, you can support '
                  'development by gifting in-game vouchers:')}\n\n'
              '${tr('1. Open the SEAGM OverMortal voucher page')}\n'
              '${tr('2. Pick any voucher amount')}\n'
              '${tr("3. Paste the RID below into the site's RID field")}'),
          const SizedBox(height: 12),
          SelectableText(donateUrl),
          const SizedBox(height: 8),
          SelectableText(donateRid,
              style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () {
            Clipboard.setData(ClipboardData(text: donateUrl));
            ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(tr('Site link copied'))));
          },
          child: Text(tr('Copy link')),
        ),
        TextButton(
          onPressed: () {
            Clipboard.setData(ClipboardData(text: donateRid));
            ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(tr('RID copied'))));
          },
          child: Text(tr('Copy RID')),
        ),
        TextButton(onPressed: () => Navigator.pop(ctx), child: Text(tr('Close'))),
      ],
    ),
  );
}

/// Export/import dialog for shareable build codes. [exportCode] produces the
/// current build's code; [importCode] applies a pasted one and reports
/// whether it decoded.
void showShareDialog(BuildContext context,
    {required String Function() exportCode,
    required bool Function(String) importCode}) {
  final importCtrl = TextEditingController();
  showDialog<void>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(tr('Share build')),
      content: Column(mainAxisSize: MainAxisSize.min, children: [
        Text(tr(
            'Export copies a text code of ALL your inputs to the clipboard '
            '— send it to someone and they can import it to see exactly '
            'what you entered.')),
        const SizedBox(height: 12),
        TextField(
          controller: importCtrl,
          decoration: InputDecoration(
            labelText: tr('Paste a build code to import'),
            border: const OutlineInputBorder(),
          ),
          maxLines: 3,
          minLines: 1,
        ),
      ]),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(ctx),
          child: Text(tr('Cancel')),
        ),
        TextButton(
          onPressed: () {
            Clipboard.setData(ClipboardData(text: exportCode()));
            Navigator.pop(ctx);
            ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(tr('Build code copied'))));
          },
          child: Text(tr('Export')),
        ),
        FilledButton(
          onPressed: () {
            final ok = importCode(importCtrl.text);
            Navigator.pop(ctx);
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                content: Text(
                    ok ? tr('Build imported') : tr('Invalid build code'))));
          },
          child: Text(tr('Import')),
        ),
      ],
    ),
  );
}
