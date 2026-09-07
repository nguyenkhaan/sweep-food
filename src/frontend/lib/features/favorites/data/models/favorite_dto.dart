import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_menu.dart';
import 'package:sweepfood/features/favorites/domain/entities/favorite_recipe.dart';

part 'favorite_dto.freezed.dart';
part 'favorite_dto.g.dart';

DateTime? _parseDateTime(dynamic v) {
  if (v == null) return null;
  if (v is DateTime) return v;
  return DateTime.tryParse(v.toString());
}

DateTime _parseDateTimeRequired(dynamic v) {
  return _parseDateTime(v) ?? DateTime.now();
}

@freezed
abstract class FavoriteRecipeDto with _$FavoriteRecipeDto {
  const FavoriteRecipeDto._();

  const factory FavoriteRecipeDto({
    @JsonKey(name: 'recipe_id') required String recipeId,
    @JsonKey(name: 'is_favorite') required bool isFavorite,
  }) = _FavoriteRecipeDto;

  factory FavoriteRecipeDto.fromJson(Map<String, dynamic> json) =>
      _$FavoriteRecipeDtoFromJson(json);
}

@freezed
abstract class FavoriteRecipeListItemDto with _$FavoriteRecipeListItemDto {
  const FavoriteRecipeListItemDto._();

  const factory FavoriteRecipeListItemDto({
    @JsonKey(name: 'recipe_id') required String recipeId,
    @JsonKey(name: 'recipe_name') required String recipeName,
    @JsonKey(name: 'recipe_description') @Default('') String recipeDescription,
    @JsonKey(name: 'media_url') String? mediaUrl,
    @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)
    required DateTime createdAt,
  }) = _FavoriteRecipeListItemDto;

  factory FavoriteRecipeListItemDto.fromJson(Map<String, dynamic> json) =>
      _$FavoriteRecipeListItemDtoFromJson(json);

  FavoriteRecipe toEntity() => FavoriteRecipe(
        recipeId: recipeId,
        recipeName: recipeName,
        recipeDescription: recipeDescription,
        mediaUrl: mediaUrl,
        createdAt: createdAt,
      );
}

@freezed
abstract class FavoriteRecipeListDto with _$FavoriteRecipeListDto {
  const FavoriteRecipeListDto._();

  const factory FavoriteRecipeListDto({
    @Default(<FavoriteRecipeListItemDto>[])
    List<FavoriteRecipeListItemDto> items,
    @Default(0) int total,
    @Default(20) int limit,
    @Default(0) int offset,
  }) = _FavoriteRecipeListDto;

  factory FavoriteRecipeListDto.fromJson(Map<String, dynamic> json) =>
      _$FavoriteRecipeListDtoFromJson(json);
}

@freezed
abstract class FavoriteMenuDto with _$FavoriteMenuDto {
  const FavoriteMenuDto._();

  const factory FavoriteMenuDto({
    required String id,
    required String name,
    String? description,
    @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)
    required DateTime createdAt,
    @JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired)
    required DateTime updatedAt,
  }) = _FavoriteMenuDto;

  factory FavoriteMenuDto.fromJson(Map<String, dynamic> json) =>
      _$FavoriteMenuDtoFromJson(json);

  FavoriteMenu toEntity({int itemCount = 0}) => FavoriteMenu(
        id: id,
        name: name,
        description: description,
        createdAt: createdAt,
        updatedAt: updatedAt,
        itemCount: itemCount,
      );
}

@freezed
abstract class FavoriteMenuListDto with _$FavoriteMenuListDto {
  const FavoriteMenuListDto._();

  const factory FavoriteMenuListDto({
    @Default(<FavoriteMenuDto>[]) List<FavoriteMenuDto> items,
    @Default(0) int total,
    @Default(20) int limit,
    @Default(0) int offset,
  }) = _FavoriteMenuListDto;

  factory FavoriteMenuListDto.fromJson(Map<String, dynamic> json) =>
      _$FavoriteMenuListDtoFromJson(json);
}

@freezed
abstract class FavoriteMenuItemDto with _$FavoriteMenuItemDto {
  const FavoriteMenuItemDto._();

  const factory FavoriteMenuItemDto({
    required String id,
    @JsonKey(name: 'recipe_id') required String recipeId,
    @JsonKey(name: 'recipe_name') required String recipeName,
    @JsonKey(name: 'recipe_description') @Default('') String recipeDescription,
    @JsonKey(name: 'media_url') String? mediaUrl,
    @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)
    required DateTime createdAt,
  }) = _FavoriteMenuItemDto;

  factory FavoriteMenuItemDto.fromJson(Map<String, dynamic> json) =>
      _$FavoriteMenuItemDtoFromJson(json);

  FavoriteMenuItem toEntity() => FavoriteMenuItem(
        id: id,
        recipeId: recipeId,
        recipeName: recipeName,
        recipeDescription: recipeDescription,
        mediaUrl: mediaUrl,
        createdAt: createdAt,
      );
}

@freezed
abstract class FavoriteMenuDetailDto with _$FavoriteMenuDetailDto {
  const FavoriteMenuDetailDto._();

  const factory FavoriteMenuDetailDto({
    required String id,
    required String name,
    String? description,
    @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)
    required DateTime createdAt,
    @JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired)
    required DateTime updatedAt,
    @Default(<FavoriteMenuItemDto>[]) List<FavoriteMenuItemDto> items,
  }) = _FavoriteMenuDetailDto;

  factory FavoriteMenuDetailDto.fromJson(Map<String, dynamic> json) =>
      _$FavoriteMenuDetailDtoFromJson(json);

  FavoriteMenuDetail toEntity() => FavoriteMenuDetail(
        id: id,
        name: name,
        description: description,
        createdAt: createdAt,
        updatedAt: updatedAt,
        items: items.map((e) => e.toEntity()).toList(),
      );
}
