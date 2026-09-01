import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_summary.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/presentation/controllers/suggestion_list_controller.dart';

part 'home_controller.g.dart';

/// How many dishes the Home "Gợi ý cho bạn" preview shows (full list is S-01).
const _homePreviewSuggestions = 2;

/// Aggregated data model for the H-01 Home Dashboard screen.
class HomeDashboardData {
  const HomeDashboardData({
    required this.summary,
    required this.nearExpiryItems,
    required this.suggestions,
    required this.suggestionCount,
  });

  final PantrySummary summary;
  final List<PantryItem> nearExpiryItems;

  /// Top scored dishes for the current pantry — a trimmed slice of the S-01
  /// list, so Home and the full Gợi ý screen never disagree.
  final List<DishSuggestion> suggestions;

  /// How many dishes the full S-01 list would show (for the grid tile count).
  final int suggestionCount;

  /// Ingredients used before expiry this period — the Home waste pill number.
  int get wasteSavedCount => summary.wasteReductionCount;

  /// Optional kilograms-avoided line on the pill; `null` hides that line.
  double? get wasteAvoidedKg => summary.wasteAvoidedKg;

  /// Pantry has no items — Home shows the "add your first ingredient" CTA.
  bool get isEmpty => summary.isEmpty;
}

/// Controller providing aggregated data for the H-01 Home Dashboard.
@riverpod
Future<HomeDashboardData> homeDashboard(Ref ref) async {
  final summary = await ref.watch(pantrySummaryProvider.future);
  final items = await ref.watch(pantryListControllerProvider.future);

  final nearExpiry = items.where((item) => item.isNearExpiry()).toList();

  // Reuse the S-01 controller so the preview matches the full list. An empty
  // pantry has nothing to suggest, and a suggestions failure should degrade to
  // "no preview" rather than blanking the whole dashboard.
  var suggestions = const <DishSuggestion>[];
  var suggestionCount = 0;
  if (!summary.isEmpty) {
    try {
      final ranked = await ref.watch(suggestionListControllerProvider.future);
      suggestionCount = ranked.length;
      suggestions = ranked.take(_homePreviewSuggestions).toList();
    } catch (_) {
      suggestions = const [];
    }
  }

  return HomeDashboardData(
    summary: summary,
    nearExpiryItems: nearExpiry,
    suggestions: suggestions,
    suggestionCount: suggestionCount,
  );
}
