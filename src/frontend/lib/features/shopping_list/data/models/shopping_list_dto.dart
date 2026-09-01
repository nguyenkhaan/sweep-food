import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list.dart';
import 'package:sweepfood/features/shopping_list/domain/entities/shopping_list_item.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

part 'shopping_list_dto.freezed.dart';
part 'shopping_list_dto.g.dart';

@freezed
abstract class ShoppingListItemDto with _$ShoppingListItemDto {
  const ShoppingListItemDto._();

  const factory ShoppingListItemDto({
    required String id,
    required String name,
    required double quantity,
    required String unit,
    @Default('Khác') String category,
    @JsonKey(name: 'checked') @Default(false) bool isChecked,
    @JsonKey(name: 'already_in_pantry') @Default(false) bool alreadyInPantry,
    @JsonKey(name: 'from_dish_ids') @Default(<String>[]) List<String> fromDishIds,
    @JsonKey(name: 'est_price_vnd') int? estPriceVnd,
  }) = _ShoppingListItemDto;

  factory ShoppingListItemDto.fromJson(Map<String, dynamic> json) =>
      _$ShoppingListItemDtoFromJson(json);

  ShoppingListItem toEntity() => ShoppingListItem(
        id: id,
        name: name,
        quantity: quantity,
        unit: MeasurementUnit.fromWire(unit),
        category: category,
        checked: isChecked,
        alreadyInPantry: alreadyInPantry,
        fromDishIds: fromDishIds,
        estPriceVnd: estPriceVnd,
      );
}

@freezed
abstract class ShoppingListDto with _$ShoppingListDto {
  const ShoppingListDto._();

  const factory ShoppingListDto({
    required String id,
    @JsonKey(name: 'source_label') String? sourceLabel,
    @Default(<ShoppingListItemDto>[]) List<ShoppingListItemDto> items,
  }) = _ShoppingListDto;

  factory ShoppingListDto.fromJson(Map<String, dynamic> json) =>
      _$ShoppingListDtoFromJson(json);

  ShoppingList toEntity() => ShoppingList(
        id: id,
        sourceLabel: sourceLabel,
        items: [for (final i in items) i.toEntity()],
      );
}
