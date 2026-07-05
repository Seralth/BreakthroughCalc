import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;

import 'engine.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final raw = await rootBundle.loadString('assets/data/breakthrough.json');
  final engine = Engine(jsonDecode(raw) as Map<String, dynamic>);
  runApp(BreakthroughApp(engine));
}

class BreakthroughApp extends StatelessWidget {
  final Engine engine;
  const BreakthroughApp(this.engine, {super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Breakthrough Calculator',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF3D6FB5),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: CalculatorPage(engine),
    );
  }
}

class CalculatorPage extends StatefulWidget {
  final Engine engine;
  const CalculatorPage(this.engine, {super.key});

  @override
  State<CalculatorPage> createState() => _CalculatorPageState();
}

class _CalculatorPageState extends State<CalculatorPage> {
  final inp = Inputs();
  late Results res;

  @override
  void initState() {
    super.initState();
    final stages = widget.engine.stages();
    inp.stage = stages.contains('Nascent') ? 'Nascent' : stages.first;
    inp.phase = widget.engine.phasesFor(inp.stage).first;
    inp.grade = widget.engine.gradesFor(inp.stage, inp.phase).first;
    inp.cultiSpeed = 58.84;
    inp.absorptionRatio = 0.275;
    _recalc();
  }

  void _recalc() => setState(() => res = widget.engine.calculate(inp));

  @override
  Widget build(BuildContext context) {
    final engine = widget.engine;
    final stages = engine.stages();
    final phases = engine.phasesFor(inp.stage);
    final grades = engine.gradesFor(inp.stage, inp.phase);

    return Scaffold(
      appBar: AppBar(title: const Text('Breakthrough Calculator')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _dropdown('Stage', inp.stage, stages, (v) {
            inp.stage = v!;
            inp.phase = engine.phasesFor(v).first;
            inp.grade = engine.gradesFor(v, inp.phase).first;
            _recalc();
          }),
          _dropdown('Half-step', inp.phase, phases, (v) {
            inp.phase = v!;
            inp.grade = engine.gradesFor(inp.stage, v).first;
            _recalc();
          }),
          _dropdown('Grade', inp.grade, grades, (v) {
            inp.grade = v!;
            _recalc();
          }),
          _number('Abode Aura', inp.absorptionRatio == 0 ? 0 : inp.cultiSpeed / inp.absorptionRatio,
              (v) { if (inp.absorptionRatio > 0) { inp.cultiSpeed = v * inp.absorptionRatio; } _recalc(); }),
          _number('Absorption Ratio (%)', inp.absorptionRatio * 100,
              (v) { inp.absorptionRatio = v / 100; _recalc(); }),
          _number('Cultivation Speed', inp.cultiSpeed, (v) { inp.cultiSpeed = v; _recalc(); }),
          const Divider(height: 32),
          if (!res.valid)
            Text(res.error, style: const TextStyle(color: Colors.redAccent))
          else ...[
            _result('Half-step breakthrough in', fmtDays(res.phaseDays), res.phaseBand),
            _result('Stage breakthrough in', fmtDays(res.stageDays), res.stageBand),
            _resultPlain('Cultivation XP / day', res.baseXpPerDay.toStringAsFixed(0)),
            _resultPlain('Effective XP / day', res.effectiveXpPerDay.toStringAsFixed(0)),
            _resultPlain('Implied Abode Aura', res.abodeAura.toStringAsFixed(1)),
          ],
        ],
      ),
    );
  }

  Widget _dropdown(String label, String value, List<String> items,
      ValueChanged<String?> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: DropdownButtonFormField<String>(
        initialValue: value,
        decoration: InputDecoration(labelText: label, border: const OutlineInputBorder()),
        items: [for (final s in items) DropdownMenuItem(value: s, child: Text(s))],
        onChanged: onChanged,
      ),
    );
  }

  Widget _number(String label, double value, ValueChanged<double> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: TextFormField(
        initialValue: value == 0 ? '' : value.toString(),
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(labelText: label, border: const OutlineInputBorder()),
        onChanged: (t) => onChanged(double.tryParse(t) ?? 0),
      ),
    );
  }

  Widget _result(String label, String value, List<double> band) {
    final showBand = band.length == 2 && (band[1] - band[0]).abs() > 1e-9;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
        Text(label),
        Expanded(
          child: Text(
            showBand ? '$value  (best ${fmtDays(band[0])} / worst ${fmtDays(band[1])})' : value,
            textAlign: TextAlign.right,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
      ]),
    );
  }

  Widget _resultPlain(String label, String value) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
          Text(label),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ]),
      );
}
