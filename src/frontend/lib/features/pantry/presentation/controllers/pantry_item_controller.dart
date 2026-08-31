import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/pantry/domain/entities/pantry_item.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/pantry_list_controller.dart';

part 'pantry_item_controller.g.dart';

/// A single pantry item for the detail screen (K-02), read from the loaded list.
/// Returns `null` if the id isn't in the list (e.g. after it was deleted).
@riverpod
PantryItem? pantryItemById(Ref ref, String id) {
  final items =
      ref.watch(pantryListControllerProvider).asData?.value ?? const [];
  for (final i in items) {
    if (i.id == id) return i;
  }
  return null;
}
