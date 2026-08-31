import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/l10n/app_localizations.dart';

part 'score_breakdown.freezed.dart';

/// The four weighted components of a dish's suitability score (spec 6.3.3, S-02).
///
/// `total = 0.4·E + 0.3·A + 0.2·P + 0.1·U`, each component normalised to `0..1`.
@freezed
abstract class ScoreBreakdown with _$ScoreBreakdown {
  const ScoreBreakdown._();

  const factory ScoreBreakdown({
    /// E — how much near-expiry stock the dish uses up.
    @Default(0) double e,

    /// A — share of ingredients already in the pantry.
    @Default(0) double a,

    /// P — fit with servings, nutrition target and preferences.
    @Default(0) double p,

    /// U — how little extra shopping it needs.
    @Default(0) double u,
  }) = _ScoreBreakdown;

  static const weights = (e: 0.4, a: 0.3, p: 0.2, u: 0.1);

  /// Weighted total in `0..1`.
  double get total => 0.4 * e + 0.3 * a + 0.2 * p + 0.1 * u;

  /// Total as the 0–100 figure shown on the card badge.
  int get scoreOutOf100 => (total * 100).round();

  /// The rows the S-02 sheet renders, top-weighted first.
  List<ScoreComponent> components(AppL10n l10n) => [
    ScoreComponent(
      letter: 'E',
      name: l10n.scoreCompE,
      weightLabel: '40%',
      value: e,
    ),
    ScoreComponent(
      letter: 'A',
      name: l10n.scoreCompA,
      weightLabel: '30%',
      value: a,
    ),
    ScoreComponent(
      letter: 'P',
      name: l10n.scoreCompP,
      weightLabel: '20%',
      value: p,
    ),
    ScoreComponent(
      letter: 'U',
      name: l10n.scoreCompU,
      weightLabel: '10%',
      value: u,
    ),
  ];
}

/// One display row for the score-breakdown sheet.
class ScoreComponent {
  const ScoreComponent({
    required this.letter,
    required this.name,
    required this.weightLabel,
    required this.value,
  });

  final String letter;
  final String name;
  final String weightLabel;

  /// `0..1`.
  final double value;
}
