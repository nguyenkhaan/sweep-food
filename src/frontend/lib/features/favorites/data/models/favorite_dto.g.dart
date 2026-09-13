// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'favorite_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_FavoriteRecipeDto _$FavoriteRecipeDtoFromJson(Map<String, dynamic> json) =>
    _FavoriteRecipeDto(
      recipeId: json['recipe_id'] as String,
      isFavorite: json['is_favorite'] as bool,
    );

Map<String, dynamic> _$FavoriteRecipeDtoToJson(_FavoriteRecipeDto instance) =>
    <String, dynamic>{
      'recipe_id': instance.recipeId,
      'is_favorite': instance.isFavorite,
    };

_FavoriteRecipeListItemDto _$FavoriteRecipeListItemDtoFromJson(
  Map<String, dynamic> json,
) => _FavoriteRecipeListItemDto(
  recipeId: json['recipe_id'] as String,
  recipeName: json['recipe_name'] as String,
  recipeDescription: json['recipe_description'] as String? ?? '',
  mediaUrl: json['media_url'] as String?,
  createdAt: _parseDateTimeRequired(json['created_at']),
);

Map<String, dynamic> _$FavoriteRecipeListItemDtoToJson(
  _FavoriteRecipeListItemDto instance,
) => <String, dynamic>{
  'recipe_id': instance.recipeId,
  'recipe_name': instance.recipeName,
  'recipe_description': instance.recipeDescription,
  'media_url': instance.mediaUrl,
  'created_at': instance.createdAt.toIso8601String(),
};

_FavoriteRecipeListDto _$FavoriteRecipeListDtoFromJson(
  Map<String, dynamic> json,
) => _FavoriteRecipeListDto(
  items:
      (json['items'] as List<dynamic>?)
          ?.map(
            (e) =>
                FavoriteRecipeListItemDto.fromJson(e as Map<String, dynamic>),
          )
          .toList() ??
      const <FavoriteRecipeListItemDto>[],
  total: (json['total'] as num?)?.toInt() ?? 0,
  limit: (json['limit'] as num?)?.toInt() ?? 20,
  offset: (json['offset'] as num?)?.toInt() ?? 0,
);

Map<String, dynamic> _$FavoriteRecipeListDtoToJson(
  _FavoriteRecipeListDto instance,
) => <String, dynamic>{
  'items': instance.items,
  'total': instance.total,
  'limit': instance.limit,
  'offset': instance.offset,
};

_FavoriteMenuDto _$FavoriteMenuDtoFromJson(Map<String, dynamic> json) =>
    _FavoriteMenuDto(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      createdAt: _parseDateTimeRequired(json['created_at']),
      updatedAt: _parseDateTimeRequired(json['updated_at']),
    );

Map<String, dynamic> _$FavoriteMenuDtoToJson(_FavoriteMenuDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
    };

_FavoriteMenuListDto _$FavoriteMenuListDtoFromJson(Map<String, dynamic> json) =>
    _FavoriteMenuListDto(
      items:
          (json['items'] as List<dynamic>?)
              ?.map((e) => FavoriteMenuDto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <FavoriteMenuDto>[],
      total: (json['total'] as num?)?.toInt() ?? 0,
      limit: (json['limit'] as num?)?.toInt() ?? 20,
      offset: (json['offset'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$FavoriteMenuListDtoToJson(
  _FavoriteMenuListDto instance,
) => <String, dynamic>{
  'items': instance.items,
  'total': instance.total,
  'limit': instance.limit,
  'offset': instance.offset,
};

_FavoriteMenuItemDto _$FavoriteMenuItemDtoFromJson(Map<String, dynamic> json) =>
    _FavoriteMenuItemDto(
      id: json['id'] as String,
      recipeId: json['recipe_id'] as String,
      recipeName: json['recipe_name'] as String,
      recipeDescription: json['recipe_description'] as String? ?? '',
      mediaUrl: json['media_url'] as String?,
      createdAt: _parseDateTimeRequired(json['created_at']),
    );

Map<String, dynamic> _$FavoriteMenuItemDtoToJson(
  _FavoriteMenuItemDto instance,
) => <String, dynamic>{
  'id': instance.id,
  'recipe_id': instance.recipeId,
  'recipe_name': instance.recipeName,
  'recipe_description': instance.recipeDescription,
  'media_url': instance.mediaUrl,
  'created_at': instance.createdAt.toIso8601String(),
};

_FavoriteMenuDetailDto _$FavoriteMenuDetailDtoFromJson(
  Map<String, dynamic> json,
) => _FavoriteMenuDetailDto(
  id: json['id'] as String,
  name: json['name'] as String,
  description: json['description'] as String?,
  createdAt: _parseDateTimeRequired(json['created_at']),
  updatedAt: _parseDateTimeRequired(json['updated_at']),
  items:
      (json['items'] as List<dynamic>?)
          ?.map((e) => FavoriteMenuItemDto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <FavoriteMenuItemDto>[],
);

Map<String, dynamic> _$FavoriteMenuDetailDtoToJson(
  _FavoriteMenuDetailDto instance,
) => <String, dynamic>{
  'id': instance.id,
  'name': instance.name,
  'description': instance.description,
  'created_at': instance.createdAt.toIso8601String(),
  'updated_at': instance.updatedAt.toIso8601String(),
  'items': instance.items,
};
