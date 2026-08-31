// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'shopping_list_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ShoppingListItemDto _$ShoppingListItemDtoFromJson(Map<String, dynamic> json) =>
    _ShoppingListItemDto(
      id: json['id'] as String,
      name: json['name'] as String,
      quantity: (json['quantity'] as num).toDouble(),
      unit: json['unit'] as String,
      category: json['category'] as String? ?? 'Khác',
      isChecked: json['checked'] as bool? ?? false,
      alreadyInPantry: json['already_in_pantry'] as bool? ?? false,
      fromDishIds: (json['from_dish_ids'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const <String>[],
      estPriceVnd: (json['est_price_vnd'] as num?)?.toInt(),
    );

Map<String, dynamic> _$ShoppingListItemDtoToJson(
        _ShoppingListItemDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'quantity': instance.quantity,
      'unit': instance.unit,
      'category': instance.category,
      'checked': instance.isChecked,
      'already_in_pantry': instance.alreadyInPantry,
      'from_dish_ids': instance.fromDishIds,
      'est_price_vnd': instance.estPriceVnd,
    };

_ShoppingListDto _$ShoppingListDtoFromJson(Map<String, dynamic> json) =>
    _ShoppingListDto(
      id: json['id'] as String,
      sourceLabel: json['source_label'] as String?,
      items: (json['items'] as List<dynamic>?)
              ?.map((e) =>
                  ShoppingListItemDto.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const <ShoppingListItemDto>[],
    );

Map<String, dynamic> _$ShoppingListDtoToJson(_ShoppingListDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'source_label': instance.sourceLabel,
      'items': instance.items,
    };
