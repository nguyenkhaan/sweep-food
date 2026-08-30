import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_summary.dart';
import 'package:frontend/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'home_controller.g.dart';

/// Aggregated data model for H-01 Home Dashboard screen.
class HomeDashboardData {
  const HomeDashboardData({
    required this.summary,
    required this.nearExpiryItems,
    required this.wasteSavedCount,
    this.wasteAvoidedKg = 2.4,
  });

  final PantrySummary summary;
  final List<PantryItem> nearExpiryItems;
  final int wasteSavedCount;
  final double wasteAvoidedKg;
}

/// Controller providing aggregated data for the H-01 Home Dashboard.
@riverpod
Future<HomeDashboardData> homeDashboard(Ref ref) async {
  final summary = await ref.watch(pantrySummaryProvider.future);
  final items = await ref.watch(pantryListControllerProvider.future);

  final nearExpiry = items
      .where((item) => item.isNearExpiry())
      .toList();

  return HomeDashboardData(
    summary: summary,
    nearExpiryItems: nearExpiry,
    wasteSavedCount: summary.wasteReductionCount > 0 ? summary.wasteReductionCount : 12,
    wasteAvoidedKg: summary.wasteAvoidedKg ?? 2.4,
  );
}

