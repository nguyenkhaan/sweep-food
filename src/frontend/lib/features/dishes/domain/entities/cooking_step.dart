import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/l10n/app_localizations.dart';

part 'cooking_step.freezed.dart';

/// One numbered step in a recipe (D-01 "Cách làm", D-02 immersive later).
@freezed
abstract class CookingStep with _$CookingStep {
  const CookingStep._();

  const factory CookingStep({
    required int order,
    required String text,
    int? durationMin,
  }) = _CookingStep;

  /// "5 phút" label when the step is timed.
  String durationLabel(AppL10n l10n) =>
      durationMin == null ? '' : l10n.minutesLabel(durationMin!);
}
