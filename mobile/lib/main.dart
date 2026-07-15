import 'dart:convert';

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:shared_preferences/shared_preferences.dart';

import 'app_dialogs.dart';
import 'doc_nav.dart';
import 'engine.dart';
import 'form_widgets.dart';
import 'guide_tab.dart';
import 'i18n.dart';
import 'input_store.dart';
import 'reference_tab.dart';
import 'results_card.dart';
import 'share_codec.dart';
import 'source_pickers.dart';
import 'theme.dart';
import 'update_banner.dart';

/// App version. Release tagging must bump this alongside pubspec.yaml's
/// `version:` field — the update checker compares it against the latest
/// GitHub release tag.
const appVersion = '2.14';

/// Commit + date stamped by CI (--dart-define=BUILD_STAMP=...); 'dev' locally.
/// Shown in-app so it's obvious whether a deploy has actually been picked up.
const buildStamp = String.fromEnvironment('BUILD_STAMP', defaultValue: 'dev');

/// Donation constants. They live HERE (not in app_dialogs.dart) because
/// tests/test_consistency.py pins these literals in main.dart against the
/// desktop package's DONATE_URL/DONATE_RID.
const donateUrl = 'https://www.seagm.com/en-us/overmortal-vouchers-global';
const donateRid = '28953_U1C466A474D1A0000';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final raw = await rootBundle.loadString('assets/data/breakthrough.json');
  final engine = Engine(jsonDecode(raw) as Map<String, dynamic>);
  final catalog = await loadCatalog('assets/data/pill_effect_sources.json');
  final respiraCatalog = await loadCatalog('assets/data/respira_sources.json');
  final prefs = await SharedPreferences.getInstance();
  final savedLang = prefs.getString('lang');
  if (savedLang != null && langs.containsKey(savedLang)) currentLang = savedLang;
  runApp(BreakthroughApp(engine, catalog, respiraCatalog, prefs));
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
      theme: themeData(theme, platform),
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

class _CalculatorPageState extends State<CalculatorPage>
    with SingleTickerProviderStateMixin {
  late final TabController _topTabs = TabController(length: 3, vsync: this);
  Inputs inp = Inputs();
  late Results res;
  late final InputStore _store = InputStore(widget.prefs, engine);
  final _peSources = <List<dynamic>>[]; // [name, percent]
  // Stable identity per _peSources row (parallel list, NOT persisted): the
  // row widgets are initialValue-driven TextFormFields, so without a stable
  // key, deleting row 0 of 2 would leave the survivor displaying the deleted
  // row's text while editing the other entry's data.
  final _peIds = <int>[];
  int _peNextId = 0;
  // Bumped whenever inputs are bulk-replaced (prefs restore / build-code
  // import) and used as the form ListView's key, remounting every
  // initialValue-driven field so it re-reads the new inputs. The four
  // controller-backed fields are covered by _syncControllers instead.
  int _formGeneration = 0;
  final _respiraSources = <String>{}; // selected 'attempt' catalog entries
  double _abode = 0; // Abode Aura, the primary input; speed = abode * absorption
  final _speedCtrl = TextEditingController();
  final _abodeCtrl = TextEditingController();
  final _absorbCtrl = TextEditingController();
  final _respiraCtrl = TextEditingController();
  final _respiraExpCtrl = TextEditingController();
  late double _respiraBooksPct =
      widget.prefs.getDouble('respira_books_pct') ?? 0.0;

  Engine get engine => widget.engine;
  final _nav = DocNavigator.instance;

  // Cross-reference links ([[ref:...]]) request a top-level tab switch here;
  // the target tab's own controller handles the sub-tab jump.
  void _onDocLink() {
    final req = _nav.pendingLink.value;
    if (req != null) _topTabs.animateTo(req.tab);
  }

  @override
  void dispose() {
    _nav.pendingLink.removeListener(_onDocLink);
    _topTabs.dispose();
    _speedCtrl.dispose();
    _abodeCtrl.dispose();
    _absorbCtrl.dispose();
    _respiraCtrl.dispose();
    _respiraExpCtrl.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    _topTabs.addListener(() => _nav.topTab = _topTabs.index);
    _nav.pendingLink.addListener(_onDocLink);
    final stages = engine.stages();
    inp.stage = stages.first;
    inp.phase = engine.phasesFor(inp.stage).first;
    inp.grade = engine.gradesFor(inp.stage, inp.phase).first;
    inp.pillRank = (engine.data['pill_xp'] as Map).keys.first as String;
    _restoreInputs();
    _syncControllers();
    _recalc();
    if (!kIsWeb) {
      WidgetsBinding.instance.addPostFrameCallback(
          (_) => checkForUpdates(context, widget.prefs, appVersion));
    }
  }

  // ---- input state (persistence in InputStore) ----
  void _restoreInputs() {
    final restored = _store.restore(_peSources, _respiraSources);
    if (restored != null) _afterBulkReplace(restored);
  }

  bool _applyInputsMap(Map<String, dynamic> m) {
    final restored = _store.apply(m, _peSources, _respiraSources);
    if (restored == null) return false;
    _afterBulkReplace(restored);
    return true;
  }

  void _afterBulkReplace(Inputs restored) {
    inp = restored;
    _peIds
      ..clear()
      ..addAll([for (final _ in _peSources) _peNextId++]);
    _formGeneration++;
  }

  void _addPeSource(String name, double percent) {
    _peSources.add([name, percent]);
    _peIds.add(_peNextId++);
  }

  void _removePeSource(int i) {
    _peSources.removeAt(i);
    _peIds.removeAt(i);
  }

  void _syncControllers() {
    _abode = inp.absorptionRatio > 0 ? inp.cultiSpeed / inp.absorptionRatio : 0;
    _speedCtrl.text = fmtNum(inp.cultiSpeed);
    _abodeCtrl.text = fmtNum(_abode);
    _absorbCtrl.text = fmtNum(inp.absorptionRatio * 100);
    _respiraCtrl.text = fmtNum(inp.respiraPerDay);
    _respiraExpCtrl.text = fmtNum(inp.respiraExp);
  }

  // ---- shareable build string -------------------------------------------
  // Compact copy-paste export of every input, so users can share their
  // setup for troubleshooting. See share_codec.dart for the format.
  String _exportString() => encodeBuildCode(engine, inp, _peSources, _respiraSources);

  bool _importString(String s) {
    final m = decodeBuildCode(engine, s);
    if (m == null || !_applyInputsMap(m)) return false;
    _syncControllers();
    _recalc();
    return true;
  }

  void _recalc() {
    inp.pillEffect = _peSources.fold(0.0, (a, s) => a + (s[1] as num)) / 100.0;
    setState(() => res = engine.calculate(inp));
    _store.save(inp, _peSources, _respiraSources);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: Text(tr('Breakthrough Calculator')),
          bottom: TabBar(controller: _topTabs, tabs: [
            Tab(text: tr('Calculator')),
            Tab(text: tr('Reference')),
            Tab(text: tr('Guide')),
          ]),
          actions: [
            IconButton(
              icon: const Icon(Icons.favorite_outline),
              tooltip: tr('Donate'),
              onPressed: () => showDonateDialog(context,
                  donateUrl: donateUrl, donateRid: donateRid),
            ),
            PopupMenuButton<String>(
              icon: const Icon(Icons.palette_outlined),
              tooltip: tr('Theme'),
              initialValue: widget.theme,
              onSelected: widget.onTheme,
              itemBuilder: (_) =>
                  [for (final t in themes) PopupMenuItem(value: t, child: Text(t))],
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
            IconButton(
              icon: const Icon(Icons.ios_share),
              tooltip: tr('Share build'),
              onPressed: () => showShareDialog(context,
                  exportCode: _exportString, importCode: _importString),
            ),
            if (kIsWeb)
              IconButton(
                icon: const Icon(Icons.refresh),
                tooltip: tr('Force refresh'),
                onPressed: () => confirmForceRefresh(context,
                    appVersion: appVersion, buildStamp: buildStamp),
              ),
            if (!kIsWeb)
              PopupMenuButton<String>(
                tooltip: tr('More'),
                onSelected: (v) {
                  if (v == 'check_updates') {
                    checkForUpdates(context, widget.prefs, appVersion,
                        manual: true);
                  }
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
        body: TabBarView(controller: _topTabs, children: [_calcTab(), ReferenceTab(engine: engine, catalog: widget.catalog), const GuideTab()]),
      );
  }

  Widget _calcTab() {
    final gems = (engine.data['gem_bonus'] as Map).keys.cast<String>().toList();
    final ranks = (engine.data['pill_xp'] as Map).keys.cast<String>().toList();
    final fruitRanks = (engine.data['fruit_xp'] as Map).keys.cast<String>().toList();
    final rarities = (engine.data['rarity_names'] as List).cast<String>();
    final stages = engine.stages();

    return ListView(
      key: ValueKey(_formGeneration),
      padding: const EdgeInsets.all(12),
      children: [
        ResultsCard(engine: engine, inp: inp, res: res),
        formGroup(context, tr('Cultivation Base'), [
          formDropdown(tr('Stage'), inp.stage, stages, (v) {
            inp.stage = v!;
            inp.phase = engine.phasesFor(v).first;
            inp.grade = engine.gradesFor(v, inp.phase).first;
            if (inp.targetStage.isNotEmpty &&
                stages.indexOf(inp.targetStage) < stages.indexOf(v)) {
              inp.targetStage = '';
              inp.targetPhase = '';
              inp.targetGrade = '';
            }
            _recalc();
          }, display: trStage),
          formDropdown(tr('Half-step'), inp.phase, engine.phasesFor(inp.stage), (v) {
            inp.phase = v!;
            inp.grade = engine.gradesFor(inp.stage, v).first;
            _recalc();
          }, display: trPhase),
          formDropdown(tr('Grade'), inp.grade, engine.gradesFor(inp.stage, inp.phase), (v) {
            inp.grade = v!;
            _recalc();
          }),
          numField(tr('Grade progress (%)'), inp.gradeCompletion * 100, (v) {
            inp.gradeCompletion = v.clamp(0, 100) / 100;
            _recalc();
          }),
          numCtrlField(tr('Abode Aura'), _abodeCtrl, (v) {
            _abode = v;
            inp.cultiSpeed = _abode * inp.absorptionRatio;
            _speedCtrl.text = fmtNum(inp.cultiSpeed);
            _recalc();
          }),
          numCtrlField(tr('Absorption Ratio (%)'), _absorbCtrl, (v) {
            inp.absorptionRatio = v / 100;
            inp.cultiSpeed = _abode * inp.absorptionRatio;
            _speedCtrl.text = fmtNum(inp.cultiSpeed);
            _recalc();
          }),
          numField(tr('Ascension blessing (%)'), inp.blessPp * 100, (v) {
            inp.blessPp = v / 100;
            _recalc();
          }),
          numField(tr('Blessing before Voidbreak Middle (%)'),
              inp.blessWindowPp * 100, (v) {
            inp.blessWindowPp = v / 100;
            _recalc();
          }),
          numCtrlField(tr('Cultivation Speed'), _speedCtrl, (v) {
            inp.cultiSpeed = v;
            if (inp.absorptionRatio > 0) {
              _abode = inp.cultiSpeed / inp.absorptionRatio;
              _abodeCtrl.text = fmtNum(_abode);
            }
            _recalc();
          }),
          formDropdown(tr('Aura Gem'), inp.auraGem, gems, (v) {
            inp.auraGem = v!;
            _recalc();
          }, display: tr),
          formDropdown(tr('Target Stage'), inp.targetStage.isEmpty ? '(none)' : inp.targetStage,
              ['(none)', ...stages.sublist(stages.indexOf(inp.stage))], (v) {
            inp.targetStage = v == '(none)' ? '' : v!;
            inp.targetPhase = '';
            inp.targetGrade = '';
            _recalc();
          }, display: trStage),
          if (inp.targetStage.isNotEmpty)
            formDropdown(tr('Target half-step'), inp.targetPhase.isEmpty ? '(none)' : inp.targetPhase,
                ['(none)', ...engine.phasesFor(inp.targetStage)], (v) {
              inp.targetPhase = v == '(none)' ? '' : v!;
              inp.targetGrade = '';
              _recalc();
            }, display: trPhase),
          if (inp.targetStage.isNotEmpty && inp.targetPhase.isNotEmpty)
            formDropdown(tr('Target grade'), inp.targetGrade.isEmpty ? '(none)' : inp.targetGrade,
                ['(none)', ...engine.gradesFor(inp.targetStage, inp.targetPhase)], (v) {
              inp.targetGrade = v == '(none)' ? '' : v!;
              _recalc();
            }),
          if (inp.targetStage.isNotEmpty)
            numField(tr('Timegate lifts in (days)'), inp.timegateDays, (v) {
              inp.timegateDays = v.clamp(0, 1000);
              _recalc();
            }),
          formDropdown(tr('Server #1 Stage (Strive)'), inp.topStage.isEmpty ? '(none)' : inp.topStage,
              ['(none)', ...stages], (v) {
            inp.topStage = v == '(none)' ? '' : v!;
            _recalc();
          }, display: trStage),
          checkField(tr('Mature server (world 30+)'), inp.matureServer, (v) {
            inp.matureServer = v;
            _recalc();
          }),
          checkField(tr("Already used today's pills/respira"), inp.dailiesDone, (v) {
            inp.dailiesDone = v;
            _recalc();
          }),
          if (inp.dailiesDone)
            numField(tr('Reset in (h)'), inp.resetInHours, (v) {
              inp.resetInHours = v.clamp(0, 24);
              _recalc();
            }),
        ]),
        formGroup(context, tr('Cultivation Pills'), [
          formDropdown(tr('Pill rank'), inp.pillRank, ranks, (v) {
            inp.pillRank = v!;
            _recalc();
          }),
          peSourcesEditor(context, _peSources, _peIds,
              recalc: _recalc,
              onRemove: (i) {
                setState(() => _removePeSource(i));
                _recalc();
              },
              onAdd: () => setState(() => _addPeSource('', 0.0)),
              onCatalog: _pickCatalog),
          numField(tr('Daily pill attempts'), inp.pillLimit, (v) {
            inp.pillLimit = v;
            _recalc();
          }),
          numField(tr('Legendary (Gold) / day'), inp.goldPerDay, (v) {
            inp.goldPerDay = v;
            _recalc();
          }),
          numField(tr('Epic (Purple) / day'), inp.purplePerDay, (v) {
            inp.purplePerDay = v;
            _recalc();
          }),
          numField(tr('Rare (Blue) / day'), inp.bluePerDay, (v) {
            inp.bluePerDay = v;
            _recalc();
          }),
          numField(tr('Star Mark: Blue (+ratio)'), inp.markBlue, (v) {
            inp.markBlue = v;
            _recalc();
          }),
          numField(tr('Star Mark: Purple (+ratio)'), inp.markPurple, (v) {
            inp.markPurple = v;
            _recalc();
          }),
          numField(tr('Star Mark: Gold (+ratio)'), inp.markGold, (v) {
            inp.markGold = v;
            _recalc();
          }),
        ]),
        formGroup(context, tr('Creation Artifacts'), [
          artifactField(tr('Starsea Vase'), inp.vase, inp.vaseStar, inp.vaseSkin, inp.vaseCharge,
              (v) => inp.vase = v, (v) => inp.vaseStar = v, (v) => inp.vaseSkin = v,
              (v) => inp.vaseCharge = v, recalc: _recalc),
          formDropdown(tr('Vase input pill'), inp.vaseInput, vaseInputKinds, (v) {
            inp.vaseInput = v!;
            _recalc();
          }, display: tr),
          artifactField(tr('Dual-Star Mirror'), inp.mirror, inp.mirrorStar, inp.mirrorSkin,
              inp.mirrorCharge, (v) => inp.mirror = v, (v) => inp.mirrorStar = v,
              (v) => inp.mirrorSkin = v, (v) => inp.mirrorCharge = v, recalc: _recalc),
          artifactField(tr('Timereversal Pearl'), inp.pearl, inp.pearlStar, inp.pearlSkin,
              inp.pearlCharge, (v) => inp.pearl = v, (v) => inp.pearlStar = v,
              (v) => inp.pearlSkin = v, (v) => inp.pearlCharge = v, recalc: _recalc),
          numField(tr('Pearl EXP per 10 energy'), inp.pearlXpPer10, (v) {
            inp.pearlXpPer10 = v;
            _recalc();
          }),
        ]),
        formGroup(context, tr('Respira'), [
          Row(children: [
            Expanded(
              child: numCtrlField(tr('Attempts / day'), _respiraCtrl, (v) {
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
          numField(tr('Extra attempts today'), inp.respiraEvent, (v) {
            inp.respiraEvent = v;
            _recalc();
          }),
          Row(children: [
            Expanded(
              child: numCtrlField(tr('Base EXP / attempt'), _respiraExpCtrl,
                  (v) {
                inp.respiraExp = v;
                _recalc();
              }),
            ),
            IconButton(
              icon: const Icon(Icons.auto_fix_high),
              tooltip: tr('Auto-fill from Stage'),
              onPressed: () {
                final base = engine.respiraBaseEstimate(inp.stage);
                if (base == null) return;
                setState(() {
                  inp.respiraExp =
                      (base * (1 + _respiraBooksPct / 100)).roundToDouble();
                  _respiraExpCtrl.text = fmtNum(inp.respiraExp);
                });
                _recalc();
              },
            ),
          ]),
          numField(tr('Respira Effect books (%)'), _respiraBooksPct, (v) {
            _respiraBooksPct = v;
            widget.prefs.setDouble('respira_books_pct', v);
          }),
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text(
              tr("Base attempt limit is 10/day (from game data); add permanent bonuses. "
                  "Do a few Respira: most give the same small EXP (the base — enter that); "
                  "some give 2×/5×/10× (crits — ignore, handled automatically)."),
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ),
          numField(tr('XP elixirs / day'), inp.elixirPerDay, (v) {
            inp.elixirPerDay = v;
            _recalc();
          }),
          numField(tr('EXP per elixir'), inp.elixirExp, (v) {
            inp.elixirExp = v;
            _recalc();
          }),
          numField(tr('Elixir effectiveness (%)'), inp.elixirEffect * 100, (v) {
            inp.elixirEffect = v / 100;
            _recalc();
          }),
        ]),
        formGroup(context, tr('Myrimon Fruit'), [
          formDropdown(tr('Fruit rank'), inp.fruitRank, fruitRanks, (v) {
            inp.fruitRank = v!;
            _recalc();
          }),
          checkField(tr('Highest rank (+50%)'), inp.fruitHighestRank, (v) {
            inp.fruitHighestRank = v;
            _recalc();
          }),
          numField(tr('No. of fruits'), inp.fruitCount, (v) {
            inp.fruitCount = v;
            _recalc();
          }),
          numIntField(tr('Culti level'), inp.lvlCulti, (v) {
            inp.lvlCulti = v;
            _recalc();
          }),
          numIntField(tr('Quality level'), inp.lvlQuality, (v) {
            inp.lvlQuality = v;
            _recalc();
          }),
          numIntField(tr('Gush level'), inp.lvlGush, (v) {
            inp.lvlGush = v;
            _recalc();
          }),
          formDropdown(tr('Extractor quality'), inp.extractorRarity, rarities, (v) {
            inp.extractorRarity = v!;
            _recalc();
          }, display: tr),
        ]),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Center(
            child: Text(
              'v$appVersion · $buildStamp',
              style: TextStyle(
                  fontSize: 11, color: Theme.of(context).hintColor),
            ),
          ),
        ),
      ],
    );
  }

  // ---- source pickers (state wiring; UI in source_pickers.dart) ----
  void _pickCatalog() {
    pickCatalogSource(context, widget.catalog, _peSources,
        onPicked: (name, value) {
      setState(() => _addPeSource(name, value));
      _recalc();
    });
  }

  void _pickRespiraSources() {
    pickRespiraSources(context, widget.respiraCatalog, _respiraSources,
        inp: inp, respiraCtrl: _respiraCtrl, recalc: _recalc);
  }
}
