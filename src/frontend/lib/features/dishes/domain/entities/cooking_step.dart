import 'package:freezed_annotation/freezed_annotation.dart';

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

  /// "· 5 phút" suffix when the step is timed.
  String get durationLabel => durationMin == null ? '' : '$durationMin phút';
}
