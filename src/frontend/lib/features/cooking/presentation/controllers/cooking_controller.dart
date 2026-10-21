import 'dart:async';

import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/cooking/data/repositories/cooking_repository_impl.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_confirmation.dart';
import 'package:sweepfood/features/cooking/domain/entities/cook_result.dart';
import 'package:sweepfood/features/cooking/domain/entities/cooking_preview.dart';
import 'package:sweepfood/features/dishes/domain/entities/local_dishes.dart';
import 'package:sweepfood/features/meal_plan/data/repositories/meal_plan_repository_impl.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan.dart';
import 'package:sweepfood/features/meal_plan/domain/entities/meal_plan_entry.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

part 'cooking_controller.g.dart';

/// Drives the post-cook flow: preview → session → complete → expose the
/// [CookResult] for the D-05 / D-07 screen. Applying the result also
/// refreshes the pantry list, so the Home waste count picks it up.
///
/// Kept alive: the confirming widget (a bottom sheet) only `read`s this, so an
/// auto-dispose provider would be torn down mid-request.
@Riverpod(keepAlive: true)
class CookingController extends _$CookingController {
  @override
  CookResult? build() => null;

  /// The backend's `/cooking/*` endpoints only accept a `meal_plan_item_id` —
  /// there's no "cook this recipe right now" without one. The Dish-detail
  /// "Đã nấu món này" button has no meal-plan step in its UI, so this
  /// transparently creates a hidden item in today's plan first. **This is an
  /// unreviewed product assumption** — see IMPLEMENTATION_PLAN.md (an open
  /// question was raised with the backend team on whether auto-creating
  /// hidden meal-plan items this way is acceptable for reporting/stats).
  Future<CookingPreview> previewForDish({
    required String dishId,
    required double servings,
  }) async {
    if (!isUuid(dishId)) {
      return _buildLocalPreview(dishId, servings);
    }

    final mealPlanRepo = ref.read(mealPlanRepositoryProvider);
    final weekStart = MealPlan.weekStartOf(DateTime.now());
    final planRes = await mealPlanRepo.forWeek(weekStart);
    final plan = planRes.fold((f) => throw f, (p) => p);
    final today = DateTime.now();

    // Reuse this dish's still-planned item from today instead of stacking a
    // new hidden one on every tap; otherwise take a free slot (never overwrite
    // a meal the user planned themselves).
    MealPlanEntry? entry;
    var created = false;
    for (final slot in _slotsFromNow()) {
      final existing = plan.entryAt(today, slot);
      if (existing != null &&
          existing.dishId == dishId &&
          existing.status == MealPlanItemStatus.planned) {
        entry = existing;
        break;
      }
    }
    if (entry != null) {
      if (entry.servings != servings) {
        final updated = await mealPlanRepo.updateEntry(
          weekStart: plan.weekStart,
          itemId: entry.id,
          dishId: dishId,
          servings: servings,
        );
        entry = updated.fold((f) => throw f, (e) => e);
      }
    } else {
      final freeSlot = _slotsFromNow()
          .where((s) => plan.entryAt(today, s) == null)
          .firstOrNull;
      if (freeSlot == null) {
        throw StateError('Hôm nay đã kín các bữa trong thực đơn.');
      }
      final entryRes = await mealPlanRepo.addEntry(
        weekStart: plan.weekStart,
        date: today,
        slot: freeSlot,
        dishId: dishId,
        servings: servings,
      );
      entry = entryRes.fold((f) => throw f, (e) => e);
      created = true;
    }

    final preview = await previewForItem(entry.id);
    if (created && preview.hasMissingIngredients) {
      // Not cookable: don't leave a phantom planned meal behind.
      await mealPlanRepo.removeEntry(
        weekStart: plan.weekStart,
        itemId: entry.id,
      );
    }
    return preview;
  }

  /// Same as [previewForDish] but for an existing meal-plan item (M-01 →
  /// "Đã nấu" on a planned slot — not wired to any screen yet).
  Future<CookingPreview> previewForItem(String mealPlanItemId) async {
    final res = await ref.read(cookingRepositoryProvider).preview(mealPlanItemId);
    return res.fold((f) => throw f, (p) => p);
  }

  Future<CookingPreview> _buildLocalPreview(String dishId, double servings) async {
    final dish = getLocalDish(dishId).scaledTo(servings.toInt());
    List<PantryItem> pantryItems;
    try {
      pantryItems = await ref.read(pantryListControllerProvider.future);
    } catch (_) {
      pantryItems =
          ref.read(pantryListControllerProvider).asData?.value ?? const [];
    }
    final activePantry = pantryItems
        .where((p) => p.status == PantryItemStatus.active && p.quantity > 0)
        .toList();

    final missing = <MissingIngredientPreview>[];
    final deductions = <ProposedDeduction>[];

    for (final ing in dish.ingredients) {
      if (ing.isSeasoning) continue;
      final norm = ing.name.toLowerCase().trim();
      final batches = activePantry.where((p) {
        final pNorm = p.name.toLowerCase().trim();
        return pNorm == norm || pNorm.contains(norm) || norm.contains(pNorm);
      }).toList();

      final totalAvailable =
          batches.fold<double>(0, (sum, p) => sum + p.quantity);
      if (totalAvailable >= ing.quantity) {
        if (batches.isNotEmpty) {
          deductions.add(ProposedDeduction(
            recipeIngredientId: '',
            batchId: batches.first.id,
            quantity: ing.quantity,
            unit: ing.unit,
          ));
        }
      } else {
        missing.add(MissingIngredientPreview(
          recipeIngredientId: '',
          ingredientName: ing.name,
          missingQuantity: ing.quantity - totalAvailable,
          unit: ing.unit,
        ));
      }
    }

    return CookingPreview(
      mealPlanItemId: 'local-$dishId',
      recipeId: dishId,
      recipeName: dish.name,
      servings: servings,
      proposedDeductions: deductions,
      missingIngredients: missing,
    );
  }

  /// Today's slots, the one matching the current hour first.
  static List<MealSlot> _slotsFromNow() {
    final first = _slotForNow();
    return [first, ...MealSlot.values.where((s) => s != first)];
  }

  static MealSlot _slotForNow() {
    final h = DateTime.now().hour;
    if (h < 10) return MealSlot.breakfast;
    if (h < 15) return MealSlot.lunch;
    if (h < 20) return MealSlot.dinner;
    return MealSlot.snack;
  }

  Future<CookResult> confirm({
    required CookingPreview preview,
    required CookMode mode,
    required String dishName,
    List<ConsumptionLine>? consumptions,
  }) async {
    String sessionId;
    if (!isUuid(preview.recipeId)) {
      sessionId = 'local-${DateTime.now().millisecondsSinceEpoch}';
    } else {
      final repo = ref.read(cookingRepositoryProvider);
      final sessionRes = await repo.createSession(preview.mealPlanItemId);
      sessionId = sessionRes.fold((f) => throw f, (id) => id);

      final completeRes =
          await repo.complete(sessionId, mode, consumptions: consumptions);
      completeRes.fold((f) => throw f, (_) {});
    }

    final result = _buildResult(
      preview: preview,
      mode: mode,
      consumptions: consumptions,
      sessionId: sessionId,
      dishName: dishName,
    );

    ref.read(pantryListControllerProvider.notifier).applyCookChanges(
          updated: result.updatedPantryItems,
          depletedIds: result.depletedItemIds,
        );
    if (isUuid(preview.recipeId)) {
      ref.invalidate(pantryListControllerProvider);
    }

    state = result;
    return result;
  }

  /// The backend doesn't document a `/complete` response body, so the
  /// before/after breakdown is derived from [preview]'s `proposed_deductions`
  /// cross-referenced against the pantry list already loaded in the app.
  CookResult _buildResult({
    required CookingPreview preview,
    required CookMode mode,
    List<ConsumptionLine>? consumptions,
    required String sessionId,
    required String dishName,
  }) {
    final pantryItems =
        ref.read(pantryListControllerProvider).asData?.value ?? const [];
    final byId = {for (final i in pantryItems) i.id: i};

    final changes = <PantryChange>[];
    for (final d in preview.proposedDeductions) {
      final item = byId[d.batchId];
      final before = item?.quantity ?? d.quantity;
      final used = switch (mode) {
        CookMode.exact => d.quantity,
        CookMode.half => d.quantity / 2,
        CookMode.all => before, // "use all matched" — drains the whole batch
        CookMode.custom => _customQuantity(consumptions, d) ?? d.quantity,
      };
      final after = (before - used).clamp(0, double.infinity).toDouble();
      changes.add(
        PantryChange(
          name: item?.name ?? 'Nguyên liệu',
          unit: item?.unit ?? d.unit,
          before: before,
          after: after,
          nearExpiryUsed: item?.isNearExpiry() ?? false,
          pantryItemId: d.batchId,
        ),
      );
    }

    final updatedPantryItems = <PantryItem>[];
    final depletedIds = <String>[];
    for (final c in changes) {
      final item = c.pantryItemId == null ? null : byId[c.pantryItemId];
      if (item == null) continue;
      if (c.after <= 0) {
        depletedIds.add(item.id);
      } else {
        updatedPantryItems.add(item.copyWith(quantity: c.after));
      }
    }

    final nearExpiryUsedCount = changes.where((c) => c.nearExpiryUsed).length;
    final wasteAvoidedGrams = changes
        .where((c) => c.nearExpiryUsed && c.unit.isWeight)
        .fold<double>(
          0,
          (sum, c) =>
              sum +
              (c.before - c.after) *
                  (c.unit == MeasurementUnit.kilogram ? 1000 : 1),
        );

    return CookResult(
      dishId: preview.recipeId,
      dishName: dishName.isEmpty ? preview.recipeName : dishName,
      sessionId: sessionId,
      changes: changes,
      updatedPantryItems: updatedPantryItems,
      depletedItemIds: depletedIds,
      nearExpiryUsedCount: nearExpiryUsedCount,
      wasteAvoidedGrams: wasteAvoidedGrams,
    );
  }

  double? _customQuantity(
    List<ConsumptionLine>? consumptions,
    ProposedDeduction d,
  ) {
    if (consumptions == null) return null;
    for (final c in consumptions) {
      if (c.batchId == d.batchId && c.recipeIngredientId == d.recipeIngredientId) {
        return c.quantity;
      }
    }
    return null;
  }
}
