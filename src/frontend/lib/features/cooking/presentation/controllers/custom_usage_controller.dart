import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_preview.dart';

part 'custom_usage_controller.g.dart';

/// D-04 — per-batch "how much did you actually use" sliders, keyed by
/// `recipe_ingredient_id|batch_id` (a recipe ingredient can be split across
/// more than one matched batch). Seeded from the preview's proposed
/// deductions; the sheet edits each entry.
@riverpod
class CustomUsageController extends _$CustomUsageController {
  @override
  Map<String, double> build(CookingPreview preview) => {
        for (final d in preview.proposedDeductions) _key(d): d.quantity,
      };

  static String _key(ProposedDeduction d) =>
      '${d.recipeIngredientId}|${d.batchId}';

  double usageFor(ProposedDeduction d) => state[_key(d)] ?? d.quantity;

  void setUsage(ProposedDeduction d, double quantity) =>
      state = {...state, _key(d): quantity < 0 ? 0 : quantity};
}
