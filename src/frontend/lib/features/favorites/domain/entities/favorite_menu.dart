import 'package:freezed_annotation/freezed_annotation.dart';

part 'favorite_menu.freezed.dart';

@freezed
abstract class FavoriteMenu with _$FavoriteMenu {
  const factory FavoriteMenu({
    required String id,
    required String name,
    String? description,
    required DateTime createdAt,
    required DateTime updatedAt,
    @Default(0) int itemCount,
  }) = _FavoriteMenu;
}

@freezed
abstract class FavoriteMenuItem with _$FavoriteMenuItem {
  const factory FavoriteMenuItem({
    required String id,
    required String recipeId,
    required String recipeName,
    @Default('') String recipeDescription,
    String? mediaUrl,
    required DateTime createdAt,
  }) = _FavoriteMenuItem;
}

@freezed
abstract class FavoriteMenuDetail with _$FavoriteMenuDetail {
  const factory FavoriteMenuDetail({
    required String id,
    required String name,
    String? description,
    required DateTime createdAt,
    required DateTime updatedAt,
    @Default(<FavoriteMenuItem>[]) List<FavoriteMenuItem> items,
  }) = _FavoriteMenuDetail;
}
