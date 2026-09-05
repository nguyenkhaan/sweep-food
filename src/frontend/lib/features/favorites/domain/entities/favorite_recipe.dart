import 'package:freezed_annotation/freezed_annotation.dart';

part 'favorite_recipe.freezed.dart';

@freezed
abstract class FavoriteRecipe with _$FavoriteRecipe {
  const factory FavoriteRecipe({
    required String recipeId,
    required String recipeName,
    @Default('') String recipeDescription,
    String? mediaUrl,
    required DateTime createdAt,
  }) = _FavoriteRecipe;
}
