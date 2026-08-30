import 'package:frontend/features/catalog/data/repositories/ingredient_repository_impl.dart';
import 'package:frontend/features/catalog/domain/entities/ingredient.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'ingredient_search_controller.g.dart';

/// Autocomplete results for [query] (K-03). Empty query → a short popular list.
@riverpod
Future<List<Ingredient>> ingredientSearch(Ref ref, String query) async {
  // Debounce a touch so we don't hit the repo on every keystroke.
  await Future<void>.delayed(const Duration(milliseconds: 200));
  final res = await ref.watch(ingredientRepositoryProvider).search(query);
  return res.fold((f) => throw f, (list) => list);
}
