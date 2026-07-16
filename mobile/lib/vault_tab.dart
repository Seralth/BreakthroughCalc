/// The Vault: set-once ownership home (Dart twin of the desktop Vault in
/// breakthrough_calc/shelf_ui.py). Library = technique books on rank
/// shelves, Treasury = curios, Companions = immortal friends + blessings
/// plus the residual base values. Pure UI over shelf.dart's derive();
/// state lives with the caller (main.dart) and persists via prefs.
library;

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;

import 'form_widgets.dart';
import 'i18n.dart';

/// Load the shelf catalog (a JSON object, unlike the legacy list catalogs);
/// missing or corrupt assets yield {} (an empty Vault).
Future<Map<String, dynamic>> loadShelfCatalog(String asset) async {
  try {
    return jsonDecode(await rootBundle.loadString(asset))
        as Map<String, dynamic>;
  } catch (_) {
    return {};
  }
}

/// Mutable Vault state: what the player owns, the residual bases for
/// base:"user" targets, and whether derived values auto-fill the
/// calculator fields. Persisted as the 'shelf_v1' prefs blob.
class VaultState {
  Map<String, dynamic> owned;
  Map<String, double> bases;
  bool auto;
  VaultState({Map<String, dynamic>? owned, Map<String, double>? bases,
      this.auto = false})
      : owned = owned ?? {},
        bases = bases ?? {'respira_attempts': 10.0, 'pill_attempts': 0.0};

  Map<String, dynamic> toMap() =>
      {'owned': owned, 'bases': bases, 'auto': auto};

  static VaultState fromMap(Map<String, dynamic> m) => VaultState(
        owned: Map<String, dynamic>.from(m['owned'] as Map? ?? {}),
        bases: {
          for (final e in (m['bases'] as Map? ?? {}).entries)
            e.key as String: (e.value as num).toDouble()
        },
        auto: m['auto'] == true,
      );
}

/// Full-screen route around [VaultTab] — the Vault is reached from the
/// Calculator (summary card + app-bar shortcut), not the top TabBar.
class VaultPage extends StatelessWidget {
  final Map<String, dynamic> catalog;
  final VaultState state;
  final VoidCallback onChanged;
  const VaultPage(
      {super.key,
      required this.catalog,
      required this.state,
      required this.onChanged});

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: Text(tr('Vault'))),
        body: VaultTab(catalog: catalog, state: state, onChanged: onChanged),
      );
}

class VaultTab extends StatefulWidget {
  final Map<String, dynamic> catalog;
  final VaultState state;
  final VoidCallback onChanged;
  const VaultTab(
      {super.key,
      required this.catalog,
      required this.state,
      required this.onChanged});

  @override
  State<VaultTab> createState() => _VaultTabState();
}

class _VaultTabState extends State<VaultTab> {
  VaultState get st => widget.state;

  List<Map> _byCategory(String cat) => [
        for (final s in (widget.catalog['sources'] ?? []) as List)
          if ((s as Map)['category'] == cat) s
      ];

  void _edit(void Function() f) {
    setState(f);
    widget.onChanged();
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Column(children: [
        TabBar(tabs: [
          Tab(text: tr('Library')),
          Tab(text: tr('Treasury')),
          Tab(text: tr('Companions')),
        ]),
        Expanded(
          child: TabBarView(children: [
            _library(context),
            _treasury(context),
            _companions(context),
          ]),
        ),
      ]),
    );
  }

  // ---- Library: rank shelves of technique books --------------------------
  Widget _library(BuildContext context) {
    final books = _byCategory('technique_book');
    final byRank = <String, List<Map>>{};
    for (final b in books) {
      byRank.putIfAbsent((b['rank'] ?? '?') as String, () => []).add(b);
    }
    final ranks = byRank.keys.toList()..sort();
    return DefaultTabController(
      length: 2,
      child: Column(children: [
        TabBar(tabs: [
          Tab(text: tr('Universal')),
          Tab(text: tr('Exclusive')),
        ]),
        Expanded(
          child: TabBarView(children: [
            ListView(padding: const EdgeInsets.all(8), children: [
              Padding(
                padding: const EdgeInsets.all(8),
                child: Text(
                  tr('Set each book\'s tier once; the bonuses it has '
                      'unlocked flow to the calculator on their own. Dots '
                      'show the book\'s chapter bonuses: filled ones are '
                      'active at your tier.'),
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ),
              for (final rank in ranks) ...[
                Padding(
                  padding: const EdgeInsets.fromLTRB(8, 4, 8, 0),
                  child: Row(children: [
                    Expanded(
                      child: Text(rank,
                          style: Theme.of(context).textTheme.titleMedium),
                    ),
                    TextButton(
                      onPressed: () => _edit(() {
                        for (final b in byRank[rank]!) {
                          final lv = b['levels'] as Map;
                          st.owned[b['id'] as String] = lv['kind'] == 'binary'
                              ? 1
                              : ((lv['max'] as num?)?.toInt() ?? 1);
                        }
                      }),
                      child: Text(tr('Max shelf'),
                          style: const TextStyle(fontSize: 12)),
                    ),
                  ]),
                ),
                for (final b in byRank[rank]!) _bookRow(context, b),
              ],
            ]),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(tr(
                  'Exclusive technique manuals give combat stats only, so '
                  'they are not tracked yet. This shelf will fill in '
                  'later.')),
            ),
          ]),
        ),
      ]),
    );
  }

  Widget _bookRow(BuildContext context, Map entry) {
    final id = entry['id'] as String;
    final levels = entry['levels'] as Map;
    final owned = st.owned[id];
    final effects = (entry['effects'] ?? []) as List;
    final thresholds = <int>{
      for (final e in effects)
        (e as Map)['min_level'] is int ? e['min_level'] as int : 1
    }.toList()
      ..sort();
    final lvl = owned == null
        ? null
        : (owned == -1 ? 1 << 30 : (owned as num).toInt());
    final dots = [
      for (final ml in thresholds) (lvl != null && lvl >= ml) ? '●' : '○'
    ].join(' ');
    final isBinary = levels['kind'] == 'binary';
    final max = isBinary ? 1 : ((levels['max'] as num?)?.toInt() ?? 99);
    final cur = owned == null ? 0 : (owned as num).toInt();
    return ListTile(
      dense: true,
      title: Text(entry['name'] as String),
      subtitle: Text(
          '$dots${entry['data_status'] != 'exact' ? '  *' : ''}',
          style: const TextStyle(fontSize: 12)),
      onTap: () => _showChapters(context, entry, lvl),
      trailing: Row(mainAxisSize: MainAxisSize.min, children: [
        IconButton(
          icon: const Icon(Icons.remove, size: 18),
          onPressed: cur > 0
              ? () => _edit(() {
                    final v = cur - 1;
                    if (v <= 0) {
                      st.owned.remove(id);
                    } else {
                      st.owned[id] = v;
                    }
                  })
              : null,
        ),
        SizedBox(
          width: 52,
          child: Text(
            cur == 0
                ? '—'
                : isBinary
                    ? tr('Max')
                    : '${tr('T')}$cur/$max',
            textAlign: TextAlign.center,
          ),
        ),
        IconButton(
          icon: const Icon(Icons.add, size: 18),
          onPressed: cur < max ? () => _edit(() => st.owned[id] = cur + 1) : null,
        ),
      ]),
    );
  }

  void _showChapters(BuildContext context, Map entry, int? _) {
    final id = entry['id'] as String;
    final levels = entry['levels'] as Map;
    final isBinary = levels['kind'] == 'binary';
    final max = isBinary ? 1 : ((levels['max'] as num?)?.toInt() ?? 15);
    showModalBottomSheet<void>(
      context: context,
      builder: (_) => StatefulBuilder(builder: (context, setSheet) {
        final cur =
            st.owned[id] == null ? 0 : (st.owned[id] as num).toInt();
        void setTier(int v) {
          setSheet(() {});
          _edit(() {
            if (v <= 0) {
              st.owned.remove(id);
            } else {
              st.owned[id] = v;
            }
          });
        }

        return SafeArea(
          child: ListView(
            shrinkWrap: true,
            padding: const EdgeInsets.all(12),
            children: [
              Row(children: [
                Expanded(
                  child: Text(entry['name'] as String,
                      style: Theme.of(context).textTheme.titleLarge),
                ),
                TextButton(
                  onPressed: cur > 0 ? () => setTier(0) : null,
                  child: Text(tr('Not learned')),
                ),
                FilledButton(
                  onPressed: cur < max ? () => setTier(max) : null,
                  child: Text(tr('Max')),
                ),
              ]),
              if (!isBinary)
                Row(children: [
                  Text(cur == 0 ? '—' : '${tr('T')}$cur',
                      style: const TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 13)),
                  Expanded(
                    child: Slider(
                      value: cur.toDouble(),
                      min: 0,
                      max: max.toDouble(),
                      divisions: max,
                      label: cur == 0 ? '—' : '$cur',
                      onChanged: (v) => setTier(v.round()),
                    ),
                  ),
                  Text('${tr('T')}$max',
                      style: const TextStyle(fontSize: 12)),
                ]),
              for (final e in (entry['effects'] ?? []) as List)
                ListTile(
                  dense: true,
                  leading: Icon(
                    cur > 0 &&
                            (cur == -1 ||
                                cur >=
                                    ((e as Map)['min_level'] is int
                                        ? e['min_level'] as int
                                        : 1))
                        ? Icons.check_circle
                        : Icons.radio_button_unchecked,
                    size: 18,
                  ),
                  title: Text(((e as Map)['note'] ?? '') as String,
                      style: const TextStyle(fontSize: 13)),
                ),
            ],
          ),
        );
      }),
    );
  }

  // ---- Treasury: curios ---------------------------------------------------
  Widget _treasury(BuildContext context) {
    return ListView(padding: const EdgeInsets.all(8), children: [
      for (final c in _byCategory('curio')) _curioRow(context, c),
    ]);
  }

  Widget _curioRow(BuildContext context, Map entry) {
    final id = entry['id'] as String;
    final levels = entry['levels'] as Map;
    final owned = st.owned[id];
    final notes = [
      for (final e in (entry['effects'] ?? []) as List)
        if (((e as Map)['note'] ?? '') != '') e['note'] as String
    ].join('\n');
    if (levels['kind'] == 'custom') {
      final params = (levels['params'] as List).cast<Map>();
      final vals = owned is List
          ? owned.cast<num>().map((v) => v.toInt()).toList()
          : [for (final p in params) (p['min'] as num).toInt()];
      return Column(children: [
        SwitchListTile(
          dense: true,
          title: Text(entry['name'] as String),
          subtitle: Text(notes,
              style: const TextStyle(fontSize: 12), maxLines: 2,
              overflow: TextOverflow.ellipsis),
          value: owned != null,
          onChanged: (v) => _edit(() {
            if (v) {
              st.owned[id] = vals;
            } else {
              st.owned.remove(id);
            }
          }),
        ),
        if (owned != null)
          Padding(
            padding: const EdgeInsets.only(left: 16, right: 16),
            child: Row(children: [
              for (var i = 0; i < params.length; i++) ...[
                Expanded(
                  child: numIntField(tr(params[i]['label'] as String), vals[i],
                      (v) {
                    final lo = (params[i]['min'] as num).toInt();
                    final hi = (params[i]['max'] as num).toInt();
                    _edit(() {
                      vals[i] = v.clamp(lo, hi);
                      st.owned[id] = List<int>.from(vals);
                    });
                  }),
                ),
                if (i < params.length - 1) const SizedBox(width: 8),
              ],
            ]),
          ),
      ]);
    }
    return SwitchListTile(
      dense: true,
      title: Text(entry['name'] as String),
      subtitle: Text(notes,
          style: const TextStyle(fontSize: 12), maxLines: 2,
          overflow: TextOverflow.ellipsis),
      value: owned != null,
      onChanged: (v) => _edit(() {
        if (v) {
          st.owned[id] = 1;
        } else {
          st.owned.remove(id);
        }
      }),
    );
  }

  // ---- Companions: friends + blessings + bases + auto switch --------------
  Widget _companions(BuildContext context) {
    final friends = _byCategory('immortal_friend');
    final blessings = _byCategory('blessing');
    return ListView(padding: const EdgeInsets.all(8), children: [
      SwitchListTile(
        dense: true,
        title: Text(tr('Auto-fill calculator fields')),
        subtitle: Text(
            tr('Writes the Vault\'s totals into pill effect, attempts and '
                'Respira fields whenever the Vault changes.'),
            style: const TextStyle(fontSize: 12)),
        value: st.auto,
        onChanged: (v) => _edit(() => st.auto = v),
      ),
      formGroup(context, tr('Base values (before sources)'), [
        numField(tr('Respira attempts / day'),
            st.bases['respira_attempts'] ?? 10.0, (v) {
          _edit(() => st.bases['respira_attempts'] = v);
        }),
        numField(tr('Daily pill limit'), st.bases['pill_attempts'] ?? 0.0,
            (v) {
          _edit(() => st.bases['pill_attempts'] = v);
        }),
      ]),
      Padding(
        padding: const EdgeInsets.fromLTRB(8, 12, 8, 4),
        child: Text(tr('Immortal friends'),
            style: Theme.of(context).textTheme.titleMedium),
      ),
      for (final f in friends) _friendRow(context, f),
      Padding(
        padding: const EdgeInsets.fromLTRB(8, 12, 8, 4),
        child: Text(tr('Ascension blessings'),
            style: Theme.of(context).textTheme.titleMedium),
      ),
      for (final b in blessings) _ladderRow(context, b),
    ]);
  }

  Widget _friendRow(BuildContext context, Map entry) {
    final id = entry['id'] as String;
    final owned = st.owned[id];
    final maxed = owned == -1;
    final level = owned == null || maxed ? 0 : (owned as num).toInt();
    final notes = [
      for (final e in (entry['effects'] ?? []) as List)
        if (((e as Map)['note'] ?? '') != '') e['note'] as String
    ].join('\n');
    return ListTile(
      dense: true,
      title: Text(entry['name'] as String),
      subtitle: Text(notes,
          style: const TextStyle(fontSize: 12), maxLines: 2,
          overflow: TextOverflow.ellipsis),
      trailing: Row(mainAxisSize: MainAxisSize.min, children: [
        SizedBox(
          width: 72,
          child: numIntField(tr('lv'), level, (v) {
            _edit(() {
              if (v <= 0) {
                st.owned.remove(id);
              } else {
                st.owned[id] = v;
              }
            });
          }),
        ),
        const SizedBox(width: 4),
        Text(tr('Max'), style: const TextStyle(fontSize: 12)),
        Checkbox(
          value: maxed,
          onChanged: (v) => _edit(() {
            if (v == true) {
              st.owned[id] = -1;
            } else if (level > 0) {
              st.owned[id] = level;
            } else {
              st.owned.remove(id);
            }
          }),
        ),
      ]),
    );
  }

  Widget _ladderRow(BuildContext context, Map entry) {
    final id = entry['id'] as String;
    final labels = ((entry['levels'] as Map)['labels'] as List).cast<String>();
    final owned = st.owned[id];
    final current =
        owned == null ? '—' : labels[(owned as num).toInt().clamp(1, labels.length) - 1];
    return ListTile(
      dense: true,
      title: Text(entry['name'] as String),
      trailing: DropdownButton<String>(
        value: current,
        items: [
          const DropdownMenuItem(value: '—', child: Text('—')),
          for (final l in labels) DropdownMenuItem(value: l, child: Text(l)),
        ],
        onChanged: (v) => _edit(() {
          if (v == null || v == '—') {
            st.owned.remove(id);
          } else {
            st.owned[id] = labels.indexOf(v) + 1;
          }
        }),
      ),
    );
  }
}
