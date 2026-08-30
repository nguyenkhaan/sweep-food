import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_item.dart';
import 'package:frontend/features/pantry/domain/entities/pantry_summary.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';
import 'package:frontend/shared/domain/storage_tier.dart';

part 'pantry_item_dto.freezed.dart';
part 'pantry_item_dto.g.dart';

@freezed
abstract class PantryItemDto with _$PantryItemDto {
  const PantryItemDto._();

  const factory PantryItemDto({
    required String id,
    required String name,
    required String category,
    required double quantity,
    required String unit,
    @JsonKey(name: 'storage_tier') required String storageTier,
    @JsonKey(name: 'added_at') required DateTime addedAt,
    required String source,
    @Default('active') String status,
    @JsonKey(name: 'ingredient_id') String? ingredientId,
    @JsonKey(name: 'packed_date') DateTime? packedDate,
    @JsonKey(name: 'expiry_date') DateTime? expiryDate,
    @JsonKey(name: 'reference_shelf_life_days') int? referenceShelfLifeDays,
    @JsonKey(name: 'price_vnd') int? priceVnd,
  }) = _PantryItemDto;

  factory PantryItemDto.fromJson(Map<String, dynamic> json) =>
      _$PantryItemDtoFromJson(json);

  PantryItem toEntity() => PantryItem(
        id: id,
        name: name,
        category: category,
        quantity: quantity,
        unit: MeasurementUnit.fromWire(unit),
        storageTier: StorageTier.fromWire(storageTier),
        addedAt: addedAt,
        source: PantrySource.fromWire(source),
        status: PantryItemStatus.fromWire(status),
        ingredientId: ingredientId,
        packedDate: packedDate,
        expiryDate: expiryDate,
        referenceShelfLifeDays: referenceShelfLifeDays,
        priceVnd: priceVnd,
      );
}

@freezed
abstract class PantrySummaryDto with _$PantrySummaryDto {
  const PantrySummaryDto._();

  const factory PantrySummaryDto({
    @JsonKey(name: 'total_count') required int totalCount,
    @JsonKey(name: 'count_by_tier') @Default({}) Map<String, int> countByTier,
    @JsonKey(name: 'near_expiry') @Default([]) List<PantryItemDto> nearExpiry,
    @JsonKey(name: 'waste_reduction_count') @Default(0) int wasteReductionCount,
    @JsonKey(name: 'waste_avoided_kg') double? wasteAvoidedKg,
  }) = _PantrySummaryDto;

  factory PantrySummaryDto.fromJson(Map<String, dynamic> json) =>
      _$PantrySummaryDtoFromJson(json);

  PantrySummary toEntity() => PantrySummary(
        totalCount: totalCount,
        countByTier: {
          for (final e in countByTier.entries)
            StorageTier.fromWire(e.key): e.value,
        },
        nearExpiry: nearExpiry.map((d) => d.toEntity()).toList(),
        wasteReductionCount: wasteReductionCount,
        wasteAvoidedKg: wasteAvoidedKg,
      );
}
