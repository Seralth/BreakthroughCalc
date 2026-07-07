import 'dart:convert';

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show Clipboard, ClipboardData, rootBundle;
import 'package:shared_preferences/shared_preferences.dart';

import 'engine.dart';
import 'i18n.dart';
import 'reference.dart';
import 'update_check.dart';

/// App version. Release tagging must bump this alongside pubspec.yaml's
/// `version:` field — the update checker compares it against the latest
/// GitHub release tag.
const appVersion = '2.8.0';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final raw = await rootBundle.loadString('assets/data/breakthrough.json');
  final engine = Engine(jsonDecode(raw) as Map<String, dynamic>);
  List<dynamic> catalog = [];
  try {
    catalog = jsonDecode(
        await rootBundle.loadString('assets/data/pill_effect_sources.json')) as List;
  } catch (_) {}
  List<dynamic> respiraCatalog = [];
  try {
    respiraCatalog = jsonDecode(
        await rootBundle.loadString('assets/data/respira_sources.json')) as List;
  } catch (_) {}
  final prefs = await SharedPreferences.getInstance();
  final savedLang = prefs.getString('lang');
  if (savedLang != null && langs.containsKey(savedLang)) currentLang = savedLang;
  runApp(BreakthroughApp(engine, catalog, respiraCatalog, prefs));
}

// ---- themes ----------------------------------------------------------------
const _themes = ['Seralth', 'Dark', 'Light', 'System'];

ThemeData _themeData(String name, Brightness platform) {
  Brightness b;
  Color seed;
  switch (name) {
    case 'Light':
      b = Brightness.light;
      seed = const Color(0xFF2A72C8);
      break;
    case 'Dark':
      b = Brightness.dark;
      seed = const Color(0xFF2A82DA);
      break;
    case 'System':
      b = platform;
      seed = const Color(0xFF2A82DA);
      break;
    default: // Seralth
      b = Brightness.dark;
      seed = const Color(0xFF3D6FB5);
  }
  final scheme = ColorScheme.fromSeed(seedColor: seed, brightness: b);
  return ThemeData(
    colorScheme: name == 'Seralth'
        ? scheme.copyWith(surface: const Color(0xFF1E2530))
        : scheme,
    scaffoldBackgroundColor: name == 'Seralth' ? const Color(0xFF1A1F28) : null,
    useMaterial3: true,
    inputDecorationTheme: const InputDecorationTheme(
      border: OutlineInputBorder(),
      isDense: true,
      contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 12),
    ),
  );
}

class BreakthroughApp extends StatefulWidget {
  final Engine engine;
  final List<dynamic> catalog;
  final List<dynamic> respiraCatalog;
  final SharedPreferences prefs;
  const BreakthroughApp(this.engine, this.catalog, this.respiraCatalog, this.prefs,
      {super.key});

  @override
  State<BreakthroughApp> createState() => _BreakthroughAppState();
}

class _BreakthroughAppState extends State<BreakthroughApp> {
  late String theme = widget.prefs.getString('theme') ?? 'Seralth';

  void setTheme(String t) {
    setState(() => theme = t);
    widget.prefs.setString('theme', t);
  }

  void setLang(String l) {
    setState(() => currentLang = l);
    widget.prefs.setString('lang', l);
  }

  @override
  Widget build(BuildContext context) {
    final platform = MediaQuery.platformBrightnessOf(context);
    return MaterialApp(
      title: 'Breakthrough Calculator',
      debugShowCheckedModeBanner: false,
      theme: _themeData(theme, platform),
      home: CalculatorPage(
        engine: widget.engine,
        catalog: widget.catalog,
        respiraCatalog: widget.respiraCatalog,
        prefs: widget.prefs,
        theme: theme,
        onTheme: setTheme,
        onLang: setLang,
      ),
    );
  }
}

// ---- main page -------------------------------------------------------------
class CalculatorPage extends StatefulWidget {
  final Engine engine;
  final List<dynamic> catalog;
  final List<dynamic> respiraCatalog;
  final SharedPreferences prefs;
  final String theme;
  final ValueChanged<String> onTheme;
  final ValueChanged<String> onLang;
  const CalculatorPage({
    super.key,
    required this.engine,
    required this.catalog,
    required this.respiraCatalog,
    required this.prefs,
    required this.theme,
    required this.onTheme,
    required this.onLang,
  });

  @override
  State<CalculatorPage> createState() => _CalculatorPageState();
}

class _CalculatorPageState extends State<CalculatorPage> {
  Inputs inp = Inputs();
  late Results res;
  final _peSources = <List<dynamic>>[]; // [name, percent]
  final _respiraSources = <String>{}; // selected 'attempt' catalog entries
  double _abode = 0; // Abode Aura, the primary input; speed = abode * absorption
  final _speedCtrl = TextEditingController();
  final _abodeCtrl = TextEditingController();
  final _absorbCtrl = TextEditingController();
  final _respiraCtrl = TextEditingController();

  Engine get engine => widget.engine;

  @override
  void dispose() {
    _speedCtrl.dispose();
    _abodeCtrl.dispose();
    _absorbCtrl.dispose();
    _respiraCtrl.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    final stages = engine.stages();
    inp.stage = stages.first;
    inp.phase = engine.phasesFor(inp.stage).first;
    inp.grade = engine.gradesFor(inp.stage, inp.phase).first;
    inp.pillRank = (engine.data['pill_xp'] as Map).keys.first as String;
    _restoreInputs();
    _abode = inp.absorptionRatio > 0 ? inp.cultiSpeed / inp.absorptionRatio : 0;
    _speedCtrl.text = _fmtNum(inp.cultiSpeed);
    _abodeCtrl.text = _fmtNum(_abode);
    _absorbCtrl.text = _fmtNum(inp.absorptionRatio * 100);
    _respiraCtrl.text = _fmtNum(inp.respiraPerDay);
    _recalc();
    if (!kIsWeb) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _checkForUpdates());
    }
  }

  // ---- update check ----
  /// Checks GitHub for a newer release. Silent on failure; on startup
  /// ([manual] false) it only shows a banner for a not-yet-dismissed newer
  /// version, while a manual check also reports "up to date" / failures.
  Future<void> _checkForUpdates({bool manual = false}) async {
    final rel = await fetchLatestRelease(appVersion);
    if (!mounted) return;
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
    if (!manual && widget.prefs.getString('dismissed_update') == version) return;
    final messenger = ScaffoldMessenger.of(context);
    messenger.hideCurrentMaterialBanner();
    messenger.showMaterialBanner(MaterialBanner(
      content: Text('${tr('Update available')}: v$version'),
      leading: const Icon(Icons.system_update_alt),
      actions: [
        TextButton(
          onPressed: () {
            messenger.hideCurrentMaterialBanner();
            _showReleaseDialog(version, rel.url);
          },
          child: Text(tr('View')),
        ),
        TextButton(
          onPressed: () {
            messenger.hideCurrentMaterialBanner();
            widget.prefs.setString('dismissed_update', version);
          },
          child: Text(tr('Dismiss')),
        ),
      ],
    ));
  }

  /// No url_launcher dependency, so instead of opening a browser we show the
  /// release URL as selectable text with a copy button.
  static const _donateUrl =
      'https://www.seagm.com/en-us/overmortal-vouchers-global';
  static const _donateRid = '28953_U1C466A474D1A0000';

  void _showDonateDialog() {
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
            const SelectableText(_donateUrl),
            const SizedBox(height: 8),
            const SelectableText(_donateRid,
                style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Clipboard.setData(const ClipboardData(text: _donateUrl));
              ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(tr('Site link copied'))));
            },
            child: Text(tr('Copy link')),
          ),
          TextButton(
            onPressed: () {
              Clipboard.setData(const ClipboardData(text: _donateRid));
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

  void _showReleaseDialog(String version, String url) {
    if (!mounted) return;
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('${tr('Update available')}: v$version'),
        content: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(tr('Open this link in your browser to download the release:')),
          const SizedBox(height: 8),
          SelectableText(url.isEmpty
              ? 'https://github.com/Seralth/BreakthroughCalc/releases/latest'
              : url),
        ]),
        actions: [
          TextButton(
            onPressed: () {
              Clipboard.setData(ClipboardData(
                  text: url.isEmpty
                      ? 'https://github.com/Seralth/BreakthroughCalc/releases/latest'
                      : url));
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

  void _restoreInputs() {
    final raw = widget.prefs.getString('inputs_v1');
    if (raw == null) return;
    try {
      final m = jsonDecode(raw) as Map<String, dynamic>;
      final restored = Inputs.fromMap(m);
      // Sanity-check the cascading dropdowns against the engine's data.
      if (!engine.stages().contains(restored.stage)) return;
      if (!engine.phasesFor(restored.stage).contains(restored.phase)) {
        restored.phase = engine.phasesFor(restored.stage).first;
      }
      if (!engine.gradesFor(restored.stage, restored.phase).contains(restored.grade)) {
        restored.grade = engine.gradesFor(restored.stage, restored.phase).first;
      }
      inp = restored;
      _peSources
        ..clear()
        ..addAll([
          for (final s in (m['pe_sources'] as List? ?? []))
            [(s as List)[0] as String, (s[1] as num).toDouble()]
        ]);
      _respiraSources
        ..clear()
        ..addAll((m['respira_sources'] as List? ?? []).cast<String>());
    } catch (_) {
      // Corrupt saved state — keep defaults.
    }
  }

  void _saveInputs() {
    widget.prefs.setString('inputs_v1', jsonEncode({
      'stage': inp.stage,
      'phase': inp.phase,
      'grade': inp.grade,
      'grade_completion': inp.gradeCompletion,
      'culti_speed': inp.cultiSpeed,
      'absorption_ratio': inp.absorptionRatio,
      'aura_gem': inp.auraGem,
      'target_stage': inp.targetStage,
      'top_stage': inp.topStage,
      'mature_server': inp.matureServer,
      'dailies_done': inp.dailiesDone,
      'reset_in_hours': inp.resetInHours,
      'respira_per_day': inp.respiraPerDay,
      'respira_event': inp.respiraEvent,
      'respira_exp': inp.respiraExp,
      'pill_rank': inp.pillRank,
      'pill_effect': inp.pillEffect,
      'pill_limit': inp.pillLimit,
      'gold_per_day': inp.goldPerDay,
      'purple_per_day': inp.purplePerDay,
      'blue_per_day': inp.bluePerDay,
      'mark_blue': inp.markBlue,
      'mark_purple': inp.markPurple,
      'mark_gold': inp.markGold,
      'vase': inp.vase,
      'vase_star': inp.vaseStar,
      'vase_skin': inp.vaseSkin,
      'vase_input': inp.vaseInput,
      'mirror': inp.mirror,
      'mirror_star': inp.mirrorStar,
      'mirror_skin': inp.mirrorSkin,
      'pearl': inp.pearl,
      'pearl_star': inp.pearlStar,
      'pearl_skin': inp.pearlSkin,
      'pearl_xp_per_10': inp.pearlXpPer10,
      'vase_charge': inp.vaseCharge,
      'mirror_charge': inp.mirrorCharge,
      'pearl_charge': inp.pearlCharge,
      'fruit_rank': inp.fruitRank,
      'fruit_count': inp.fruitCount,
      'fruit_highest_rank': inp.fruitHighestRank,
      'lvl_culti': inp.lvlCulti,
      'lvl_quality': inp.lvlQuality,
      'lvl_gush': inp.lvlGush,
      'extractor_rarity': inp.extractorRarity,
      'pe_sources': _peSources,
      'respira_sources': _respiraSources.toList(),
    }));
  }

  void _recalc() {
    inp.pillEffect = _peSources.fold(0.0, (a, s) => a + (s[1] as num)) / 100.0;
    setState(() => res = engine.calculate(inp));
    _saveInputs();
  }

  static const _stars = ['0*', '1*', '2*', '3*', '4*', '5*'];

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text(tr('Breakthrough Calculator')),
          bottom: TabBar(tabs: [
            Tab(text: tr('Calculator')),
            Tab(text: tr('Reference')),
            Tab(text: tr('Guide')),
          ]),
          actions: [
            IconButton(
              icon: const Icon(Icons.favorite_outline),
              tooltip: tr('Donate'),
              onPressed: _showDonateDialog,
            ),
            PopupMenuButton<String>(
              icon: const Icon(Icons.palette_outlined),
              tooltip: tr('Theme'),
              initialValue: widget.theme,
              onSelected: widget.onTheme,
              itemBuilder: (_) =>
                  [for (final t in _themes) PopupMenuItem(value: t, child: Text(t))],
            ),
            PopupMenuButton<String>(
              icon: const Icon(Icons.language),
              tooltip: tr('Language'),
              initialValue: currentLang,
              onSelected: widget.onLang,
              itemBuilder: (_) => [
                for (final e in langs.entries)
                  PopupMenuItem(value: e.key, child: Text(e.value)),
              ],
            ),
            if (!kIsWeb)
              PopupMenuButton<String>(
                tooltip: tr('More'),
                onSelected: (v) {
                  if (v == 'check_updates') _checkForUpdates(manual: true);
                },
                itemBuilder: (_) => [
                  PopupMenuItem(
                    value: 'check_updates',
                    child: ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: const Icon(Icons.system_update_alt),
                      title: Text(tr('Check for updates')),
                    ),
                  ),
                ],
              ),
          ],
        ),
        body: TabBarView(children: [_calcTab(), ReferenceTab(engine: engine, catalog: widget.catalog), const GuideTab()]),
      ),
    );
  }

  Widget _calcTab() {
    final gems = (engine.data['gem_bonus'] as Map).keys.cast<String>().toList();
    final ranks = (engine.data['pill_xp'] as Map).keys.cast<String>().toList();
    final fruitRanks = (engine.data['fruit_xp'] as Map).keys.cast<String>().toList();
    final rarities = (engine.data['rarity_names'] as List).cast<String>();
    final stages = engine.stages();

    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        _resultsCard(),
        _group(tr('Cultivation Base'), [
          _dropdown(tr('Stage'), inp.stage, stages, (v) {
            inp.stage = v!;
            inp.phase = engine.phasesFor(v).first;
            inp.grade = engine.gradesFor(v, inp.phase).first;
            if (inp.targetStage.isNotEmpty &&
                stages.indexOf(inp.targetStage) <= stages.indexOf(v)) {
              inp.targetStage = '';
            }
            _recalc();
          }, display: trStage),
          _dropdown(tr('Half-step'), inp.phase, engine.phasesFor(inp.stage), (v) {
            inp.phase = v!;
            inp.grade = engine.gradesFor(inp.stage, v).first;
            _recalc();
          }, display: trPhase),
          _dropdown(tr('Grade'), inp.grade, engine.gradesFor(inp.stage, inp.phase), (v) {
            inp.grade = v!;
            _recalc();
          }),
          _num(tr('Grade progress (%)'), inp.gradeCompletion * 100, (v) {
            inp.gradeCompletion = v.clamp(0, 100) / 100;
            _recalc();
          }),
          _numCtrl(tr('Abode Aura'), _abodeCtrl, (v) {
            _abode = v;
            inp.cultiSpeed = _abode * inp.absorptionRatio;
            _speedCtrl.text = _fmtNum(inp.cultiSpeed);
            _recalc();
          }),
          _numCtrl(tr('Absorption Ratio (%)'), _absorbCtrl, (v) {
            inp.absorptionRatio = v / 100;
            inp.cultiSpeed = _abode * inp.absorptionRatio;
            _speedCtrl.text = _fmtNum(inp.cultiSpeed);
            _recalc();
          }),
          _numCtrl(tr('Cultivation Speed'), _speedCtrl, (v) {
            inp.cultiSpeed = v;
            if (inp.absorptionRatio > 0) {
              _abode = inp.cultiSpeed / inp.absorptionRatio;
              _abodeCtrl.text = _fmtNum(_abode);
            }
            _recalc();
          }),
          _dropdown(tr('Aura Gem'), inp.auraGem, gems, (v) {
            inp.auraGem = v!;
            _recalc();
          }, display: tr),
          _dropdown(tr('Target Stage'), inp.targetStage.isEmpty ? '(none)' : inp.targetStage,
              ['(none)', ...stages.sublist(stages.indexOf(inp.stage) + 1)], (v) {
            inp.targetStage = v == '(none)' ? '' : v!;
            _recalc();
          }, display: trStage),
          _dropdown(tr('Server #1 Stage (Strive)'), inp.topStage.isEmpty ? '(none)' : inp.topStage,
              ['(none)', ...stages], (v) {
            inp.topStage = v == '(none)' ? '' : v!;
            _recalc();
          }, display: trStage),
          _check(tr('Mature server (world 30+)'), inp.matureServer, (v) {
            inp.matureServer = v;
            _recalc();
          }),
          _check(tr("Already used today's pills/respira"), inp.dailiesDone, (v) {
            inp.dailiesDone = v;
            _recalc();
          }),
          if (inp.dailiesDone)
            _num(tr('Reset in (h)'), inp.resetInHours, (v) {
              inp.resetInHours = v.clamp(0, 24);
              _recalc();
            }),
        ]),
        _group(tr('Cultivation Pills'), [
          _dropdown(tr('Pill rank'), inp.pillRank, ranks, (v) {
            inp.pillRank = v!;
            _recalc();
          }),
          _peSourcesEditor(),
          _num(tr('Daily pill attempts'), inp.pillLimit, (v) {
            inp.pillLimit = v;
            _recalc();
          }),
          _num(tr('Legendary (Gold) / day'), inp.goldPerDay, (v) {
            inp.goldPerDay = v;
            _recalc();
          }),
          _num(tr('Epic (Purple) / day'), inp.purplePerDay, (v) {
            inp.purplePerDay = v;
            _recalc();
          }),
          _num(tr('Rare (Blue) / day'), inp.bluePerDay, (v) {
            inp.bluePerDay = v;
            _recalc();
          }),
          _num(tr('Star Mark: Blue (+ratio)'), inp.markBlue, (v) {
            inp.markBlue = v;
            _recalc();
          }),
          _num(tr('Star Mark: Purple (+ratio)'), inp.markPurple, (v) {
            inp.markPurple = v;
            _recalc();
          }),
          _num(tr('Star Mark: Gold (+ratio)'), inp.markGold, (v) {
            inp.markGold = v;
            _recalc();
          }),
        ]),
        _group(tr('Creation Artifacts'), [
          _artifact(tr('Starsea Vase'), inp.vase, inp.vaseStar, inp.vaseSkin, inp.vaseCharge,
              (v) => inp.vase = v, (v) => inp.vaseStar = v, (v) => inp.vaseSkin = v,
              (v) => inp.vaseCharge = v),
          _dropdown(tr('Vase input pill'), inp.vaseInput, ['Blue', 'Purple', 'Gold'], (v) {
            inp.vaseInput = v!;
            _recalc();
          }, display: tr),
          _artifact(tr('Dual-Star Mirror'), inp.mirror, inp.mirrorStar, inp.mirrorSkin,
              inp.mirrorCharge, (v) => inp.mirror = v, (v) => inp.mirrorStar = v,
              (v) => inp.mirrorSkin = v, (v) => inp.mirrorCharge = v),
          _artifact(tr('Timereversal Pearl'), inp.pearl, inp.pearlStar, inp.pearlSkin,
              inp.pearlCharge, (v) => inp.pearl = v, (v) => inp.pearlStar = v,
              (v) => inp.pearlSkin = v, (v) => inp.pearlCharge = v),
          _num(tr('Pearl EXP per 10 energy'), inp.pearlXpPer10, (v) {
            inp.pearlXpPer10 = v;
            _recalc();
          }),
        ]),
        _group(tr('Respira'), [
          Row(children: [
            Expanded(
              child: _numCtrl(tr('Attempts / day'), _respiraCtrl, (v) {
                inp.respiraPerDay = v;
                _recalc();
              }),
            ),
            IconButton(
              icon: const Icon(Icons.list),
              tooltip: tr('Respira sources'),
              onPressed: _pickRespiraSources,
            ),
          ]),
          _num(tr('Extra attempts today'), inp.respiraEvent, (v) {
            inp.respiraEvent = v;
            _recalc();
          }),
          _num(tr('Base EXP / attempt'), inp.respiraExp, (v) {
            inp.respiraExp = v;
            _recalc();
          }),
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text(
              tr("Do a few Respira: most give the same small EXP (the base — enter that); "
                  "some give 2×/5×/10× (crits — ignore, handled automatically)."),
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ),
        ]),
        _group(tr('Myrimon Fruit'), [
          _dropdown(tr('Fruit rank'), inp.fruitRank, fruitRanks, (v) {
            inp.fruitRank = v!;
            _recalc();
          }),
          _check(tr('Highest rank (+50%)'), inp.fruitHighestRank, (v) {
            inp.fruitHighestRank = v;
            _recalc();
          }),
          _num(tr('No. of fruits'), inp.fruitCount, (v) {
            inp.fruitCount = v;
            _recalc();
          }),
          _numInt(tr('Culti level'), inp.lvlCulti, (v) {
            inp.lvlCulti = v;
            _recalc();
          }),
          _numInt(tr('Quality level'), inp.lvlQuality, (v) {
            inp.lvlQuality = v;
            _recalc();
          }),
          _numInt(tr('Gush level'), inp.lvlGush, (v) {
            inp.lvlGush = v;
            _recalc();
          }),
          _dropdown(tr('Extractor quality'), inp.extractorRarity, rarities, (v) {
            inp.extractorRarity = v!;
            _recalc();
          }, display: tr),
        ]),
      ],
    );
  }

  // ---- results ----
  Widget _resultsCard() {
    final t = Theme.of(context);
    Widget row(String label, String value, [List<double>? band, Color? color]) {
      final showBand = band != null && band.length == 2 && (band[1] - band[0]).abs() > 1e-9;
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 3),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Expanded(flex: 5, child: Text(label)),
          Expanded(
            flex: 7,
            child: RichText(
              textAlign: TextAlign.right,
              text: TextSpan(style: t.textTheme.bodyMedium, children: [
                TextSpan(
                    text: value,
                    style: TextStyle(fontWeight: FontWeight.bold, color: color)),
                if (showBand)
                  TextSpan(
                    text: '  (${tr('best')} ${trDuration(fmtDays(band[0]))} / ${tr('worst')} ${trDuration(fmtDays(band[1]))})',
                    style: TextStyle(color: t.hintColor, fontWeight: FontWeight.normal),
                  ),
              ]),
            ),
          ),
        ]),
      );
    }

    return Card(
      color: t.colorScheme.surfaceContainerHighest,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: !res.valid
            ? Text(tr(res.error), style: TextStyle(color: t.colorScheme.error))
            : Column(children: [
                if (res.error.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: Text(tr(res.error), style: TextStyle(color: t.colorScheme.error)),
                  ),
                row(tr('Half-step breakthrough in'), trDuration(fmtDays(res.phaseDays)), res.phaseBand),
                row(tr('Stage breakthrough in'), trDuration(fmtDays(res.stageDays)), res.stageBand),
                if (res.targetValid)
                  row(tr('Target reached in'), trDuration(fmtDays(res.targetDays)), res.targetBand),
                const Divider(),
                row(tr('Abode Aura (implied)'), res.abodeAura.toStringAsFixed(1)),
                row(tr('Cultivation XP / day'), res.baseXpPerDay.toStringAsFixed(0)),
                row(tr('Effective XP / day'), res.effectiveXpPerDay.toStringAsFixed(0)),
                row(tr('Pill XP / day'), res.pillXpPerDay.toStringAsFixed(0)),
                row(
                    tr('Daily XP share (pills+Respira / gem)'),
                    '${res.effectiveXpPerDay > 0 ? ((res.pillXpPerDay + res.respiraXpPerDay) / res.effectiveXpPerDay * 100).toStringAsFixed(1) : '0.0'}%'
                    ' / +${(res.gemSpeedup * 100).round()}% ${tr('speed')}'),
                row(tr('Mythic pills / day'), res.mythicPillsPerDay.toStringAsFixed(2)),
                row(tr('Pearl XP / day'), res.pearlXpPerDay.toStringAsFixed(0)),
                row(tr('Respira XP / day'), res.respiraXpPerDay.toStringAsFixed(0)),
                row(tr('XP from fruits'), res.fruitXp.toStringAsFixed(0)),
                row(tr('Fruit time saved'), trDuration(fmtDays(res.fruitDaysSaved))),
                ..._absorptionRows(row),
              ]),
      ),
    );
  }

  /// Absorption diagnostics: the grade's base absorption and the implied
  /// Strive %, shown only from Nascent Soul on (where Strive exists). Red
  /// when implied Strive exceeds the 120% cap (likely a stale absorption
  /// reading) or absorption is below base (implied negative Strive).
  List<Widget> _absorptionRows(
      Widget Function(String, String, [List<double>?, Color?]) row) {
    final stages = engine.stages();
    final nascentIdx = stages.indexWhere((s) => s.startsWith('Nascent'));
    if (nascentIdx < 0 || stages.indexOf(inp.stage) < nascentIdx) return [];
    final idx = engine.rowIndex(inp.stage, inp.phase, inp.grade);
    if (idx < 0) return [];
    final base = ((engine.rows[idx] as Map)['low'] as num).toDouble();
    final t = Theme.of(context);
    final err = t.colorScheme.error;
    final belowBase = inp.absorptionRatio > 0 && inp.absorptionRatio < base - 1e-9;
    // The 120% Strive cap only holds through the mortal world (Incarnation and
    // earlier); later realms legitimately overcap, so only note it there.
    final incarnIdx = stages.indexWhere((s) => s.startsWith('Incarnation'));
    final mortal = incarnIdx < 0 || stages.indexOf(inp.stage) <= incarnIdx;
    final aboveCap = res.strive > 1.2 + 1e-9;
    final overCap = aboveCap && mortal;
    return [
      const Divider(),
      row(tr('Base absorption (grade)'), '${(base * 100).toStringAsFixed(0)}%',
          null, belowBase ? err : null),
      row(
          tr('Implied Strive'),
          overCap
              ? '${(res.strive * 100).toStringAsFixed(0)}% — ${tr('over 120% cap (stale reading?)')}'
              : belowBase
                  ? '${(res.strive * 100).toStringAsFixed(0)}% — ${tr("below base; Strive can't be negative")}'
                  : '${(res.strive * 100).toStringAsFixed(0)}%',
          null,
          (overCap || belowBase) ? err : null),
      if (aboveCap && !mortal)
        Padding(
          padding: const EdgeInsets.only(top: 2),
          child: Text(
            tr('Strive above 120% — normal in later realms (overcap); '
                'later cap tables not modeled.'),
            style: TextStyle(fontSize: 12, color: t.hintColor),
          ),
        ),
    ];
  }

  // ---- widget helpers ----
  Widget _group(String title, List<Widget> children) => Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(title, style: Theme.of(context).textTheme.titleMedium),
            ),
            ...children,
          ]),
        ),
      );

  /// [display] maps an INTERNAL item key to its localized label; the dropdown
  /// value (and everything persisted) stays the internal key.
  Widget _dropdown(String label, String value, List<String> items, ValueChanged<String?> onChanged,
          {String Function(String)? display}) =>
      Padding(
        padding: const EdgeInsets.symmetric(vertical: 5),
        child: DropdownButtonFormField<String>(
          initialValue: items.contains(value) ? value : items.first,
          isExpanded: true,
          decoration: InputDecoration(labelText: label),
          items: [
            for (final s in items)
              DropdownMenuItem(value: s, child: Text(display == null ? s : display(s)))
          ],
          onChanged: onChanged,
        ),
      );

  Widget _numCtrl(String label, TextEditingController ctrl, ValueChanged<double> onChanged) =>
      Padding(
        padding: const EdgeInsets.symmetric(vertical: 5),
        child: TextField(
          controller: ctrl,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: InputDecoration(labelText: label),
          onChanged: (t) => onChanged(double.tryParse(t) ?? 0),
        ),
      );

  Widget _num(String label, double value, ValueChanged<double> onChanged) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 5),
        child: TextFormField(
          initialValue: _fmtNum(value),
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: InputDecoration(labelText: label),
          onChanged: (t) => onChanged(double.tryParse(t) ?? 0),
        ),
      );

  Widget _numInt(String label, int value, ValueChanged<int> onChanged) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 5),
        child: TextFormField(
          initialValue: value == 0 ? '' : '$value',
          keyboardType: TextInputType.number,
          decoration: InputDecoration(labelText: label),
          onChanged: (t) => onChanged(int.tryParse(t) ?? 0),
        ),
      );

  Widget _check(String label, bool value, ValueChanged<bool> onChanged) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 2),
        child: CheckboxListTile(
          contentPadding: EdgeInsets.zero,
          controlAffinity: ListTileControlAffinity.leading,
          dense: true,
          title: Text(label),
          value: value,
          onChanged: (v) => onChanged(v ?? false),
        ),
      );

  Widget _artifact(String name, bool on, String star, bool skin, bool charge,
      ValueChanged<bool> onOn, ValueChanged<String> onStar, ValueChanged<bool> onSkin,
      ValueChanged<bool> onCharge) {
    // Labeled option so Skin vs Charge are never ambiguous (no hover tooltips
    // on touch). Options only show when the artifact is enabled.
    Widget labeledCheck(String label, bool value, ValueChanged<bool> cb) =>
        InkWell(
          onTap: () { cb(!value); _recalc(); },
          child: Padding(
            padding: const EdgeInsets.only(right: 8),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Checkbox(
                value: value,
                visualDensity: VisualDensity.compact,
                onChanged: (v) { cb(v ?? false); _recalc(); },
              ),
              Text(label),
            ]),
          ),
        );

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Expanded(
            child: Row(children: [
              Checkbox(value: on, onChanged: (v) { onOn(v ?? false); _recalc(); }),
              Expanded(child: Text(name, overflow: TextOverflow.ellipsis)),
            ]),
          ),
          SizedBox(
            width: 78,
            child: DropdownButtonFormField<String>(
              initialValue: star,
              isExpanded: true,
              decoration: InputDecoration(labelText: tr('Star')),
              items: [for (final s in _stars) DropdownMenuItem(value: s, child: Text(s))],
              onChanged: on ? (v) { onStar(v!); _recalc(); } : null,
            ),
          ),
        ]),
        if (on)
          Padding(
            padding: const EdgeInsets.only(left: 24, bottom: 4),
            child: Row(children: [
              labeledCheck(tr('Skin'), skin, onSkin),
              labeledCheck(tr('Daily charge'), charge, onCharge),
            ]),
          ),
      ]),
    );
  }

  // ---- pill-effect sources ----
  Widget _peSourcesEditor() {
    final total = _peSources.fold(0.0, (a, s) => a + (s[1] as num));
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      for (var i = 0; i < _peSources.length; i++)
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 3),
          child: Row(children: [
            Expanded(
              child: TextFormField(
                initialValue: _peSources[i][0] as String,
                decoration: InputDecoration(labelText: tr('Pill-effect source')),
                onChanged: (t) => _peSources[i][0] = t,
              ),
            ),
            const SizedBox(width: 8),
            SizedBox(
              width: 80,
              child: TextFormField(
                initialValue: _fmtNum((_peSources[i][1] as num).toDouble()),
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(labelText: '%'),
                onChanged: (t) { _peSources[i][1] = double.tryParse(t) ?? 0; _recalc(); },
              ),
            ),
            IconButton(
              icon: const Icon(Icons.close),
              onPressed: () { setState(() => _peSources.removeAt(i)); _recalc(); },
            ),
          ]),
        ),
      Row(children: [
        Expanded(child: Text('${tr('Pill effect total')}: ${total.toStringAsFixed(2)}%',
            style: TextStyle(color: Theme.of(context).hintColor))),
        TextButton.icon(
          icon: const Icon(Icons.add),
          label: Text(tr('Add')),
          onPressed: () { setState(() => _peSources.add(['', 0.0])); },
        ),
        TextButton.icon(
          icon: const Icon(Icons.list),
          label: Text(tr('Catalog')),
          onPressed: _pickCatalog,
        ),
      ]),
    ]);
  }

  // ---- respira sources ----
  /// Bottom-sheet catalog of daily Respira attempt sources. 'attempt' entries
  /// toggle and add/subtract from the attempts input; other kinds are shown
  /// read-only so users learn them without double-counting.
  void _pickRespiraSources() {
    showModalBottomSheet<void>(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (ctx, setSheet) => ListView(
          children: [
            for (final s in widget.respiraCatalog.cast<Map<String, dynamic>>())
              if (s['kind'] == 'attempt')
                CheckboxListTile(
                  value: _respiraSources.contains(s['name'] as String),
                  title: Text(s['name'] as String),
                  subtitle: s['note'] != null
                      ? Text(s['note'] as String, style: const TextStyle(fontSize: 11))
                      : null,
                  secondary: Text('+${s['value']}'),
                  onChanged: (v) {
                    final name = s['name'] as String;
                    final delta = (s['value'] as num).toDouble();
                    setSheet(() {
                      if (v == true && _respiraSources.add(name)) {
                        inp.respiraPerDay += delta;
                      } else if (v != true && _respiraSources.remove(name)) {
                        inp.respiraPerDay -= delta;
                        if (inp.respiraPerDay < 0) inp.respiraPerDay = 0;
                      }
                    });
                    _respiraCtrl.text = _fmtNum(inp.respiraPerDay);
                    _recalc();
                  },
                )
              else
                ListTile(
                  enabled: false,
                  title: Text(s['name'] as String),
                  subtitle: s['note'] != null
                      ? Text(s['note'] as String, style: const TextStyle(fontSize: 11))
                      : null,
                  trailing: Text(s['kind'] == 'exp_pct' ? tr('info') : tr('pill input')),
                ),
          ],
        ),
      ),
    );
  }

  void _pickCatalog() async {
    final choice = await showModalBottomSheet<Map<String, dynamic>>(
      context: context,
      builder: (_) => ListView(
        children: [
          for (final s in widget.catalog.cast<Map<String, dynamic>>())
            ListTile(
              title: Text(s['name'] as String),
              trailing: Text(((s['percent'] as num?) ?? 0) == 0 ? tr('varies') : '${s['percent']}%'),
              subtitle: s['note'] != null ? Text(s['note'] as String, style: const TextStyle(fontSize: 11)) : null,
              onTap: () => Navigator.pop(context, s),
            ),
        ],
      ),
    );
    if (choice != null) {
      double? value;
      final prompt = choice['prompt'] as Map<String, dynamic>?;
      if (prompt != null && prompt['kind'] == 'star_upgrade') {
        value = await _askStarUpgrade(choice['name'] as String, prompt);
        if (value == null) return; // user cancelled
      } else {
        value = ((choice['percent'] as num?) ?? 0).toDouble();
      }
      setState(() => _peSources.add([choice['name'], value]));
      _recalc();
    }
  }

  /// Small dialog matching the in-game curio upgrade screen: pick star and
  /// upgrade level, return the computed pill-effect %.
  Future<double?> _askStarUpgrade(String name, Map<String, dynamic> p) {
    final base = (p['base'] as num).toDouble();
    final perUpgrade = (p['per_upgrade'] as num).toDouble();
    final maxUpgrade = p['max_upgrade'] as int;
    final stars = p['stars'] as int;
    final starAdd = (p['star_add'] as List).cast<num>();
    double valueFor(int star, int upgrade) =>
        base + perUpgrade * upgrade + starAdd[star - 1].toDouble();

    var star = 1;
    var upgrade = 0;
    return showDialog<double>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDlg) => AlertDialog(
          title: Text(name),
          content: Column(mainAxisSize: MainAxisSize.min, children: [
            DropdownButtonFormField<int>(
              initialValue: star,
              decoration: InputDecoration(labelText: tr('Star')),
              items: [for (var i = 1; i <= stars; i++) DropdownMenuItem(value: i, child: Text('$i★'))],
              onChanged: (v) => setDlg(() => star = v!),
            ),
            DropdownButtonFormField<int>(
              initialValue: upgrade,
              decoration: InputDecoration(labelText: tr('Upgrade level')),
              items: [for (var i = 0; i <= maxUpgrade; i++) DropdownMenuItem(value: i, child: Text('$i'))],
              onChanged: (v) => setDlg(() => upgrade = v!),
            ),
            const SizedBox(height: 8),
            Text(
              '${tr('Cultivation Pill Effect')}: ${valueFor(star, upgrade).toStringAsFixed(1)}%',
              style: TextStyle(color: Theme.of(ctx).hintColor),
            ),
          ]),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: Text(tr('Cancel'))),
            TextButton(
              onPressed: () => Navigator.pop(
                  ctx, double.parse(valueFor(star, upgrade).toStringAsFixed(1))),
              child: Text(tr('OK')),
            ),
          ],
        ),
      ),
    );
  }

  static String _fmtNum(double v) {
    if (v == 0) return '';
    final r = double.parse(v.toStringAsFixed(4)); // strip float noise
    if (r == r.roundToDouble()) return r.toInt().toString();
    return r.toString();
  }
}
