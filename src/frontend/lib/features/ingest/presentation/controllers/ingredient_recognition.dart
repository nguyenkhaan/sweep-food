import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/pantry/data/datasources/ingredient_match_remote_data_source.dart';
import 'package:sweepfood/features/pantry/presentation/controllers/add_ingredient_controller.dart';

/// Runs [name] through the backend smart parser again (used after the user
/// renames a reviewed food). Returns the match only when the parser recognizes
/// a catalog ingredient; `null` for an unknown food or a failed request.
Future<IngredientMatch?> recognizeIngredient(Ref ref, String name) async {
  final typed = name.trim();
  if (typed.isEmpty) return null;
  try {
    final match = await ref
        .read(ingredientMatchRemoteDataSourceProvider)
        .match(typed);
    return match?.masterIngredientId == null ? null : match;
  } on Object {
    return null;
  }
}
