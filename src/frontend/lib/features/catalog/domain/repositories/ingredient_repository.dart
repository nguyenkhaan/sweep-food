import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/catalog/domain/entities/ingredient.dart';

abstract interface class IngredientRepository {
  /// Autocomplete search (K-03). Empty [query] returns a short "popular" list.
  Future<Result<List<Ingredient>>> search(String query);

  Future<Result<Ingredient>> byId(String id);
}
