import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/entitlements/entitlements.dart';
import 'package:sweepfood/core/entitlements/premium_flag.dart';

part 'entitlements_provider.g.dart';

/// The current user's [Entitlements].
///
/// While [kPremiumEnabled] is `false` this is always [Entitlements.allUnlocked].
/// When gating goes live, back this with the `/subscription` response.
@Riverpod(keepAlive: true)
Entitlements entitlements(Ref ref) {
  if (!kPremiumEnabled) return Entitlements.allUnlocked;
  // TODO(v2): return ref.watch(subscriptionControllerProvider).entitlements;
  return Entitlements.allUnlocked;
}

/// Whether [feature] is available right now.
@riverpod
bool featureAllowed(Ref ref, Feature feature) {
  final e = ref.watch(entitlementsProvider);
  return switch (feature) {
    Feature.ingredientQuota => e.hasUnlimitedIngredients,
    Feature.scanQuota => e.hasUnlimitedScans,
    Feature.weeklyPlanner => e.weeklyPlanner,
    Feature.nutritionGoals => e.nutritionGoals,
    Feature.reports => e.reports,
    Feature.pantrySharing => e.pantrySharing,
    Feature.dishHistory => e.dishHistory,
    Feature.customReminders => e.customReminders,
  };
}
