// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'pantry_item_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$PantryItemDto {

 String get id; String get name; String get category; double get quantity; String get unit;@JsonKey(name: 'storage_tier') String get storageTier;@JsonKey(name: 'added_at') DateTime get addedAt; String get source; String get status;@JsonKey(name: 'ingredient_id') String? get ingredientId;@JsonKey(name: 'packed_date') DateTime? get packedDate;@JsonKey(name: 'expiry_date') DateTime? get expiryDate;@JsonKey(name: 'reference_shelf_life_days') int? get referenceShelfLifeDays;@JsonKey(name: 'price_vnd') int? get priceVnd;
/// Create a copy of PantryItemDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PantryItemDtoCopyWith<PantryItemDto> get copyWith => _$PantryItemDtoCopyWithImpl<PantryItemDto>(this as PantryItemDto, _$identity);

  /// Serializes this PantryItemDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PantryItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageTier, storageTier) || other.storageTier == storageTier)&&(identical(other.addedAt, addedAt) || other.addedAt == addedAt)&&(identical(other.source, source) || other.source == source)&&(identical(other.status, status) || other.status == status)&&(identical(other.ingredientId, ingredientId) || other.ingredientId == ingredientId)&&(identical(other.packedDate, packedDate) || other.packedDate == packedDate)&&(identical(other.expiryDate, expiryDate) || other.expiryDate == expiryDate)&&(identical(other.referenceShelfLifeDays, referenceShelfLifeDays) || other.referenceShelfLifeDays == referenceShelfLifeDays)&&(identical(other.priceVnd, priceVnd) || other.priceVnd == priceVnd));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,category,quantity,unit,storageTier,addedAt,source,status,ingredientId,packedDate,expiryDate,referenceShelfLifeDays,priceVnd);

@override
String toString() {
  return 'PantryItemDto(id: $id, name: $name, category: $category, quantity: $quantity, unit: $unit, storageTier: $storageTier, addedAt: $addedAt, source: $source, status: $status, ingredientId: $ingredientId, packedDate: $packedDate, expiryDate: $expiryDate, referenceShelfLifeDays: $referenceShelfLifeDays, priceVnd: $priceVnd)';
}


}

/// @nodoc
abstract mixin class $PantryItemDtoCopyWith<$Res>  {
  factory $PantryItemDtoCopyWith(PantryItemDto value, $Res Function(PantryItemDto) _then) = _$PantryItemDtoCopyWithImpl;
@useResult
$Res call({
 String id, String name, String category, double quantity, String unit,@JsonKey(name: 'storage_tier') String storageTier,@JsonKey(name: 'added_at') DateTime addedAt, String source, String status,@JsonKey(name: 'ingredient_id') String? ingredientId,@JsonKey(name: 'packed_date') DateTime? packedDate,@JsonKey(name: 'expiry_date') DateTime? expiryDate,@JsonKey(name: 'reference_shelf_life_days') int? referenceShelfLifeDays,@JsonKey(name: 'price_vnd') int? priceVnd
});




}
/// @nodoc
class _$PantryItemDtoCopyWithImpl<$Res>
    implements $PantryItemDtoCopyWith<$Res> {
  _$PantryItemDtoCopyWithImpl(this._self, this._then);

  final PantryItemDto _self;
  final $Res Function(PantryItemDto) _then;

/// Create a copy of PantryItemDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? category = null,Object? quantity = null,Object? unit = null,Object? storageTier = null,Object? addedAt = null,Object? source = null,Object? status = null,Object? ingredientId = freezed,Object? packedDate = freezed,Object? expiryDate = freezed,Object? referenceShelfLifeDays = freezed,Object? priceVnd = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,storageTier: null == storageTier ? _self.storageTier : storageTier // ignore: cast_nullable_to_non_nullable
as String,addedAt: null == addedAt ? _self.addedAt : addedAt // ignore: cast_nullable_to_non_nullable
as DateTime,source: null == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,ingredientId: freezed == ingredientId ? _self.ingredientId : ingredientId // ignore: cast_nullable_to_non_nullable
as String?,packedDate: freezed == packedDate ? _self.packedDate : packedDate // ignore: cast_nullable_to_non_nullable
as DateTime?,expiryDate: freezed == expiryDate ? _self.expiryDate : expiryDate // ignore: cast_nullable_to_non_nullable
as DateTime?,referenceShelfLifeDays: freezed == referenceShelfLifeDays ? _self.referenceShelfLifeDays : referenceShelfLifeDays // ignore: cast_nullable_to_non_nullable
as int?,priceVnd: freezed == priceVnd ? _self.priceVnd : priceVnd // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [PantryItemDto].
extension PantryItemDtoPatterns on PantryItemDto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PantryItemDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PantryItemDto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PantryItemDto value)  $default,){
final _that = this;
switch (_that) {
case _PantryItemDto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PantryItemDto value)?  $default,){
final _that = this;
switch (_that) {
case _PantryItemDto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String category,  double quantity,  String unit, @JsonKey(name: 'storage_tier')  String storageTier, @JsonKey(name: 'added_at')  DateTime addedAt,  String source,  String status, @JsonKey(name: 'ingredient_id')  String? ingredientId, @JsonKey(name: 'packed_date')  DateTime? packedDate, @JsonKey(name: 'expiry_date')  DateTime? expiryDate, @JsonKey(name: 'reference_shelf_life_days')  int? referenceShelfLifeDays, @JsonKey(name: 'price_vnd')  int? priceVnd)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PantryItemDto() when $default != null:
return $default(_that.id,_that.name,_that.category,_that.quantity,_that.unit,_that.storageTier,_that.addedAt,_that.source,_that.status,_that.ingredientId,_that.packedDate,_that.expiryDate,_that.referenceShelfLifeDays,_that.priceVnd);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String category,  double quantity,  String unit, @JsonKey(name: 'storage_tier')  String storageTier, @JsonKey(name: 'added_at')  DateTime addedAt,  String source,  String status, @JsonKey(name: 'ingredient_id')  String? ingredientId, @JsonKey(name: 'packed_date')  DateTime? packedDate, @JsonKey(name: 'expiry_date')  DateTime? expiryDate, @JsonKey(name: 'reference_shelf_life_days')  int? referenceShelfLifeDays, @JsonKey(name: 'price_vnd')  int? priceVnd)  $default,) {final _that = this;
switch (_that) {
case _PantryItemDto():
return $default(_that.id,_that.name,_that.category,_that.quantity,_that.unit,_that.storageTier,_that.addedAt,_that.source,_that.status,_that.ingredientId,_that.packedDate,_that.expiryDate,_that.referenceShelfLifeDays,_that.priceVnd);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String category,  double quantity,  String unit, @JsonKey(name: 'storage_tier')  String storageTier, @JsonKey(name: 'added_at')  DateTime addedAt,  String source,  String status, @JsonKey(name: 'ingredient_id')  String? ingredientId, @JsonKey(name: 'packed_date')  DateTime? packedDate, @JsonKey(name: 'expiry_date')  DateTime? expiryDate, @JsonKey(name: 'reference_shelf_life_days')  int? referenceShelfLifeDays, @JsonKey(name: 'price_vnd')  int? priceVnd)?  $default,) {final _that = this;
switch (_that) {
case _PantryItemDto() when $default != null:
return $default(_that.id,_that.name,_that.category,_that.quantity,_that.unit,_that.storageTier,_that.addedAt,_that.source,_that.status,_that.ingredientId,_that.packedDate,_that.expiryDate,_that.referenceShelfLifeDays,_that.priceVnd);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PantryItemDto extends PantryItemDto {
  const _PantryItemDto({required this.id, required this.name, required this.category, required this.quantity, required this.unit, @JsonKey(name: 'storage_tier') required this.storageTier, @JsonKey(name: 'added_at') required this.addedAt, required this.source, this.status = 'active', @JsonKey(name: 'ingredient_id') this.ingredientId, @JsonKey(name: 'packed_date') this.packedDate, @JsonKey(name: 'expiry_date') this.expiryDate, @JsonKey(name: 'reference_shelf_life_days') this.referenceShelfLifeDays, @JsonKey(name: 'price_vnd') this.priceVnd}): super._();
  factory _PantryItemDto.fromJson(Map<String, dynamic> json) => _$PantryItemDtoFromJson(json);

@override final  String id;
@override final  String name;
@override final  String category;
@override final  double quantity;
@override final  String unit;
@override@JsonKey(name: 'storage_tier') final  String storageTier;
@override@JsonKey(name: 'added_at') final  DateTime addedAt;
@override final  String source;
@override@JsonKey() final  String status;
@override@JsonKey(name: 'ingredient_id') final  String? ingredientId;
@override@JsonKey(name: 'packed_date') final  DateTime? packedDate;
@override@JsonKey(name: 'expiry_date') final  DateTime? expiryDate;
@override@JsonKey(name: 'reference_shelf_life_days') final  int? referenceShelfLifeDays;
@override@JsonKey(name: 'price_vnd') final  int? priceVnd;

/// Create a copy of PantryItemDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PantryItemDtoCopyWith<_PantryItemDto> get copyWith => __$PantryItemDtoCopyWithImpl<_PantryItemDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PantryItemDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _PantryItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageTier, storageTier) || other.storageTier == storageTier)&&(identical(other.addedAt, addedAt) || other.addedAt == addedAt)&&(identical(other.source, source) || other.source == source)&&(identical(other.status, status) || other.status == status)&&(identical(other.ingredientId, ingredientId) || other.ingredientId == ingredientId)&&(identical(other.packedDate, packedDate) || other.packedDate == packedDate)&&(identical(other.expiryDate, expiryDate) || other.expiryDate == expiryDate)&&(identical(other.referenceShelfLifeDays, referenceShelfLifeDays) || other.referenceShelfLifeDays == referenceShelfLifeDays)&&(identical(other.priceVnd, priceVnd) || other.priceVnd == priceVnd));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,category,quantity,unit,storageTier,addedAt,source,status,ingredientId,packedDate,expiryDate,referenceShelfLifeDays,priceVnd);

@override
String toString() {
  return 'PantryItemDto(id: $id, name: $name, category: $category, quantity: $quantity, unit: $unit, storageTier: $storageTier, addedAt: $addedAt, source: $source, status: $status, ingredientId: $ingredientId, packedDate: $packedDate, expiryDate: $expiryDate, referenceShelfLifeDays: $referenceShelfLifeDays, priceVnd: $priceVnd)';
}


}

/// @nodoc
abstract mixin class _$PantryItemDtoCopyWith<$Res> implements $PantryItemDtoCopyWith<$Res> {
  factory _$PantryItemDtoCopyWith(_PantryItemDto value, $Res Function(_PantryItemDto) _then) = __$PantryItemDtoCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String category, double quantity, String unit,@JsonKey(name: 'storage_tier') String storageTier,@JsonKey(name: 'added_at') DateTime addedAt, String source, String status,@JsonKey(name: 'ingredient_id') String? ingredientId,@JsonKey(name: 'packed_date') DateTime? packedDate,@JsonKey(name: 'expiry_date') DateTime? expiryDate,@JsonKey(name: 'reference_shelf_life_days') int? referenceShelfLifeDays,@JsonKey(name: 'price_vnd') int? priceVnd
});




}
/// @nodoc
class __$PantryItemDtoCopyWithImpl<$Res>
    implements _$PantryItemDtoCopyWith<$Res> {
  __$PantryItemDtoCopyWithImpl(this._self, this._then);

  final _PantryItemDto _self;
  final $Res Function(_PantryItemDto) _then;

/// Create a copy of PantryItemDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? category = null,Object? quantity = null,Object? unit = null,Object? storageTier = null,Object? addedAt = null,Object? source = null,Object? status = null,Object? ingredientId = freezed,Object? packedDate = freezed,Object? expiryDate = freezed,Object? referenceShelfLifeDays = freezed,Object? priceVnd = freezed,}) {
  return _then(_PantryItemDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,storageTier: null == storageTier ? _self.storageTier : storageTier // ignore: cast_nullable_to_non_nullable
as String,addedAt: null == addedAt ? _self.addedAt : addedAt // ignore: cast_nullable_to_non_nullable
as DateTime,source: null == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,ingredientId: freezed == ingredientId ? _self.ingredientId : ingredientId // ignore: cast_nullable_to_non_nullable
as String?,packedDate: freezed == packedDate ? _self.packedDate : packedDate // ignore: cast_nullable_to_non_nullable
as DateTime?,expiryDate: freezed == expiryDate ? _self.expiryDate : expiryDate // ignore: cast_nullable_to_non_nullable
as DateTime?,referenceShelfLifeDays: freezed == referenceShelfLifeDays ? _self.referenceShelfLifeDays : referenceShelfLifeDays // ignore: cast_nullable_to_non_nullable
as int?,priceVnd: freezed == priceVnd ? _self.priceVnd : priceVnd // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}


/// @nodoc
mixin _$PantrySummaryDto {

@JsonKey(name: 'total_count') int get totalCount;@JsonKey(name: 'count_by_tier') Map<String, int> get countByTier;@JsonKey(name: 'near_expiry') List<PantryItemDto> get nearExpiry;@JsonKey(name: 'waste_reduction_count') int get wasteReductionCount;@JsonKey(name: 'waste_avoided_kg') double? get wasteAvoidedKg;
/// Create a copy of PantrySummaryDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PantrySummaryDtoCopyWith<PantrySummaryDto> get copyWith => _$PantrySummaryDtoCopyWithImpl<PantrySummaryDto>(this as PantrySummaryDto, _$identity);

  /// Serializes this PantrySummaryDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PantrySummaryDto&&(identical(other.totalCount, totalCount) || other.totalCount == totalCount)&&const DeepCollectionEquality().equals(other.countByTier, countByTier)&&const DeepCollectionEquality().equals(other.nearExpiry, nearExpiry)&&(identical(other.wasteReductionCount, wasteReductionCount) || other.wasteReductionCount == wasteReductionCount)&&(identical(other.wasteAvoidedKg, wasteAvoidedKg) || other.wasteAvoidedKg == wasteAvoidedKg));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,totalCount,const DeepCollectionEquality().hash(countByTier),const DeepCollectionEquality().hash(nearExpiry),wasteReductionCount,wasteAvoidedKg);

@override
String toString() {
  return 'PantrySummaryDto(totalCount: $totalCount, countByTier: $countByTier, nearExpiry: $nearExpiry, wasteReductionCount: $wasteReductionCount, wasteAvoidedKg: $wasteAvoidedKg)';
}


}

/// @nodoc
abstract mixin class $PantrySummaryDtoCopyWith<$Res>  {
  factory $PantrySummaryDtoCopyWith(PantrySummaryDto value, $Res Function(PantrySummaryDto) _then) = _$PantrySummaryDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'total_count') int totalCount,@JsonKey(name: 'count_by_tier') Map<String, int> countByTier,@JsonKey(name: 'near_expiry') List<PantryItemDto> nearExpiry,@JsonKey(name: 'waste_reduction_count') int wasteReductionCount,@JsonKey(name: 'waste_avoided_kg') double? wasteAvoidedKg
});




}
/// @nodoc
class _$PantrySummaryDtoCopyWithImpl<$Res>
    implements $PantrySummaryDtoCopyWith<$Res> {
  _$PantrySummaryDtoCopyWithImpl(this._self, this._then);

  final PantrySummaryDto _self;
  final $Res Function(PantrySummaryDto) _then;

/// Create a copy of PantrySummaryDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? totalCount = null,Object? countByTier = null,Object? nearExpiry = null,Object? wasteReductionCount = null,Object? wasteAvoidedKg = freezed,}) {
  return _then(_self.copyWith(
totalCount: null == totalCount ? _self.totalCount : totalCount // ignore: cast_nullable_to_non_nullable
as int,countByTier: null == countByTier ? _self.countByTier : countByTier // ignore: cast_nullable_to_non_nullable
as Map<String, int>,nearExpiry: null == nearExpiry ? _self.nearExpiry : nearExpiry // ignore: cast_nullable_to_non_nullable
as List<PantryItemDto>,wasteReductionCount: null == wasteReductionCount ? _self.wasteReductionCount : wasteReductionCount // ignore: cast_nullable_to_non_nullable
as int,wasteAvoidedKg: freezed == wasteAvoidedKg ? _self.wasteAvoidedKg : wasteAvoidedKg // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}

}


/// Adds pattern-matching-related methods to [PantrySummaryDto].
extension PantrySummaryDtoPatterns on PantrySummaryDto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PantrySummaryDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PantrySummaryDto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PantrySummaryDto value)  $default,){
final _that = this;
switch (_that) {
case _PantrySummaryDto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PantrySummaryDto value)?  $default,){
final _that = this;
switch (_that) {
case _PantrySummaryDto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'total_count')  int totalCount, @JsonKey(name: 'count_by_tier')  Map<String, int> countByTier, @JsonKey(name: 'near_expiry')  List<PantryItemDto> nearExpiry, @JsonKey(name: 'waste_reduction_count')  int wasteReductionCount, @JsonKey(name: 'waste_avoided_kg')  double? wasteAvoidedKg)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PantrySummaryDto() when $default != null:
return $default(_that.totalCount,_that.countByTier,_that.nearExpiry,_that.wasteReductionCount,_that.wasteAvoidedKg);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'total_count')  int totalCount, @JsonKey(name: 'count_by_tier')  Map<String, int> countByTier, @JsonKey(name: 'near_expiry')  List<PantryItemDto> nearExpiry, @JsonKey(name: 'waste_reduction_count')  int wasteReductionCount, @JsonKey(name: 'waste_avoided_kg')  double? wasteAvoidedKg)  $default,) {final _that = this;
switch (_that) {
case _PantrySummaryDto():
return $default(_that.totalCount,_that.countByTier,_that.nearExpiry,_that.wasteReductionCount,_that.wasteAvoidedKg);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'total_count')  int totalCount, @JsonKey(name: 'count_by_tier')  Map<String, int> countByTier, @JsonKey(name: 'near_expiry')  List<PantryItemDto> nearExpiry, @JsonKey(name: 'waste_reduction_count')  int wasteReductionCount, @JsonKey(name: 'waste_avoided_kg')  double? wasteAvoidedKg)?  $default,) {final _that = this;
switch (_that) {
case _PantrySummaryDto() when $default != null:
return $default(_that.totalCount,_that.countByTier,_that.nearExpiry,_that.wasteReductionCount,_that.wasteAvoidedKg);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PantrySummaryDto extends PantrySummaryDto {
  const _PantrySummaryDto({@JsonKey(name: 'total_count') required this.totalCount, @JsonKey(name: 'count_by_tier') final  Map<String, int> countByTier = const {}, @JsonKey(name: 'near_expiry') final  List<PantryItemDto> nearExpiry = const [], @JsonKey(name: 'waste_reduction_count') this.wasteReductionCount = 0, @JsonKey(name: 'waste_avoided_kg') this.wasteAvoidedKg}): _countByTier = countByTier,_nearExpiry = nearExpiry,super._();
  factory _PantrySummaryDto.fromJson(Map<String, dynamic> json) => _$PantrySummaryDtoFromJson(json);

@override@JsonKey(name: 'total_count') final  int totalCount;
 final  Map<String, int> _countByTier;
@override@JsonKey(name: 'count_by_tier') Map<String, int> get countByTier {
  if (_countByTier is EqualUnmodifiableMapView) return _countByTier;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_countByTier);
}

 final  List<PantryItemDto> _nearExpiry;
@override@JsonKey(name: 'near_expiry') List<PantryItemDto> get nearExpiry {
  if (_nearExpiry is EqualUnmodifiableListView) return _nearExpiry;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_nearExpiry);
}

@override@JsonKey(name: 'waste_reduction_count') final  int wasteReductionCount;
@override@JsonKey(name: 'waste_avoided_kg') final  double? wasteAvoidedKg;

/// Create a copy of PantrySummaryDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PantrySummaryDtoCopyWith<_PantrySummaryDto> get copyWith => __$PantrySummaryDtoCopyWithImpl<_PantrySummaryDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PantrySummaryDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _PantrySummaryDto&&(identical(other.totalCount, totalCount) || other.totalCount == totalCount)&&const DeepCollectionEquality().equals(other._countByTier, _countByTier)&&const DeepCollectionEquality().equals(other._nearExpiry, _nearExpiry)&&(identical(other.wasteReductionCount, wasteReductionCount) || other.wasteReductionCount == wasteReductionCount)&&(identical(other.wasteAvoidedKg, wasteAvoidedKg) || other.wasteAvoidedKg == wasteAvoidedKg));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,totalCount,const DeepCollectionEquality().hash(_countByTier),const DeepCollectionEquality().hash(_nearExpiry),wasteReductionCount,wasteAvoidedKg);

@override
String toString() {
  return 'PantrySummaryDto(totalCount: $totalCount, countByTier: $countByTier, nearExpiry: $nearExpiry, wasteReductionCount: $wasteReductionCount, wasteAvoidedKg: $wasteAvoidedKg)';
}


}

/// @nodoc
abstract mixin class _$PantrySummaryDtoCopyWith<$Res> implements $PantrySummaryDtoCopyWith<$Res> {
  factory _$PantrySummaryDtoCopyWith(_PantrySummaryDto value, $Res Function(_PantrySummaryDto) _then) = __$PantrySummaryDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'total_count') int totalCount,@JsonKey(name: 'count_by_tier') Map<String, int> countByTier,@JsonKey(name: 'near_expiry') List<PantryItemDto> nearExpiry,@JsonKey(name: 'waste_reduction_count') int wasteReductionCount,@JsonKey(name: 'waste_avoided_kg') double? wasteAvoidedKg
});




}
/// @nodoc
class __$PantrySummaryDtoCopyWithImpl<$Res>
    implements _$PantrySummaryDtoCopyWith<$Res> {
  __$PantrySummaryDtoCopyWithImpl(this._self, this._then);

  final _PantrySummaryDto _self;
  final $Res Function(_PantrySummaryDto) _then;

/// Create a copy of PantrySummaryDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? totalCount = null,Object? countByTier = null,Object? nearExpiry = null,Object? wasteReductionCount = null,Object? wasteAvoidedKg = freezed,}) {
  return _then(_PantrySummaryDto(
totalCount: null == totalCount ? _self.totalCount : totalCount // ignore: cast_nullable_to_non_nullable
as int,countByTier: null == countByTier ? _self._countByTier : countByTier // ignore: cast_nullable_to_non_nullable
as Map<String, int>,nearExpiry: null == nearExpiry ? _self._nearExpiry : nearExpiry // ignore: cast_nullable_to_non_nullable
as List<PantryItemDto>,wasteReductionCount: null == wasteReductionCount ? _self.wasteReductionCount : wasteReductionCount // ignore: cast_nullable_to_non_nullable
as int,wasteAvoidedKg: freezed == wasteAvoidedKg ? _self.wasteAvoidedKg : wasteAvoidedKg // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}


}

// dart format on
