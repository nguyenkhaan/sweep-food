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

 String get id;@JsonKey(name: 'master_ingredient_id') String? get masterIngredientId;@JsonKey(name: 'custom_name') String? get customName;@JsonKey(name: 'ingredient_name') String get ingredientName;@JsonKey(name: 'current_quantity') double get currentQuantity; String get unit;@JsonKey(name: 'storage_mode') String get storageMode; String get status;@JsonKey(name: 'source') String get source;@JsonKey(name: 'purchased_at') DateTime? get purchasedAt;@JsonKey(name: 'packaged_at') DateTime? get packagedAt;@JsonKey(name: 'expires_at') DateTime? get expiresAt;@JsonKey(name: 'unit_cost') num? get unitCost;@JsonKey(name: 'created_at') DateTime get createdAt;
/// Create a copy of PantryItemDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PantryItemDtoCopyWith<PantryItemDto> get copyWith => _$PantryItemDtoCopyWithImpl<PantryItemDto>(this as PantryItemDto, _$identity);

  /// Serializes this PantryItemDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PantryItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId)&&(identical(other.customName, customName) || other.customName == customName)&&(identical(other.ingredientName, ingredientName) || other.ingredientName == ingredientName)&&(identical(other.currentQuantity, currentQuantity) || other.currentQuantity == currentQuantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageMode, storageMode) || other.storageMode == storageMode)&&(identical(other.status, status) || other.status == status)&&(identical(other.source, source) || other.source == source)&&(identical(other.purchasedAt, purchasedAt) || other.purchasedAt == purchasedAt)&&(identical(other.packagedAt, packagedAt) || other.packagedAt == packagedAt)&&(identical(other.expiresAt, expiresAt) || other.expiresAt == expiresAt)&&(identical(other.unitCost, unitCost) || other.unitCost == unitCost)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,masterIngredientId,customName,ingredientName,currentQuantity,unit,storageMode,status,source,purchasedAt,packagedAt,expiresAt,unitCost,createdAt);

@override
String toString() {
  return 'PantryItemDto(id: $id, masterIngredientId: $masterIngredientId, customName: $customName, ingredientName: $ingredientName, currentQuantity: $currentQuantity, unit: $unit, storageMode: $storageMode, status: $status, source: $source, purchasedAt: $purchasedAt, packagedAt: $packagedAt, expiresAt: $expiresAt, unitCost: $unitCost, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $PantryItemDtoCopyWith<$Res>  {
  factory $PantryItemDtoCopyWith(PantryItemDto value, $Res Function(PantryItemDto) _then) = _$PantryItemDtoCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'master_ingredient_id') String? masterIngredientId,@JsonKey(name: 'custom_name') String? customName,@JsonKey(name: 'ingredient_name') String ingredientName,@JsonKey(name: 'current_quantity') double currentQuantity, String unit,@JsonKey(name: 'storage_mode') String storageMode, String status,@JsonKey(name: 'source') String source,@JsonKey(name: 'purchased_at') DateTime? purchasedAt,@JsonKey(name: 'packaged_at') DateTime? packagedAt,@JsonKey(name: 'expires_at') DateTime? expiresAt,@JsonKey(name: 'unit_cost') num? unitCost,@JsonKey(name: 'created_at') DateTime createdAt
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
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? masterIngredientId = freezed,Object? customName = freezed,Object? ingredientName = null,Object? currentQuantity = null,Object? unit = null,Object? storageMode = null,Object? status = null,Object? source = null,Object? purchasedAt = freezed,Object? packagedAt = freezed,Object? expiresAt = freezed,Object? unitCost = freezed,Object? createdAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,customName: freezed == customName ? _self.customName : customName // ignore: cast_nullable_to_non_nullable
as String?,ingredientName: null == ingredientName ? _self.ingredientName : ingredientName // ignore: cast_nullable_to_non_nullable
as String,currentQuantity: null == currentQuantity ? _self.currentQuantity : currentQuantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,storageMode: null == storageMode ? _self.storageMode : storageMode // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,source: null == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as String,purchasedAt: freezed == purchasedAt ? _self.purchasedAt : purchasedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,packagedAt: freezed == packagedAt ? _self.packagedAt : packagedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,expiresAt: freezed == expiresAt ? _self.expiresAt : expiresAt // ignore: cast_nullable_to_non_nullable
as DateTime?,unitCost: freezed == unitCost ? _self.unitCost : unitCost // ignore: cast_nullable_to_non_nullable
as num?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId, @JsonKey(name: 'custom_name')  String? customName, @JsonKey(name: 'ingredient_name')  String ingredientName, @JsonKey(name: 'current_quantity')  double currentQuantity,  String unit, @JsonKey(name: 'storage_mode')  String storageMode,  String status, @JsonKey(name: 'source')  String source, @JsonKey(name: 'purchased_at')  DateTime? purchasedAt, @JsonKey(name: 'packaged_at')  DateTime? packagedAt, @JsonKey(name: 'expires_at')  DateTime? expiresAt, @JsonKey(name: 'unit_cost')  num? unitCost, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PantryItemDto() when $default != null:
return $default(_that.id,_that.masterIngredientId,_that.customName,_that.ingredientName,_that.currentQuantity,_that.unit,_that.storageMode,_that.status,_that.source,_that.purchasedAt,_that.packagedAt,_that.expiresAt,_that.unitCost,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId, @JsonKey(name: 'custom_name')  String? customName, @JsonKey(name: 'ingredient_name')  String ingredientName, @JsonKey(name: 'current_quantity')  double currentQuantity,  String unit, @JsonKey(name: 'storage_mode')  String storageMode,  String status, @JsonKey(name: 'source')  String source, @JsonKey(name: 'purchased_at')  DateTime? purchasedAt, @JsonKey(name: 'packaged_at')  DateTime? packagedAt, @JsonKey(name: 'expires_at')  DateTime? expiresAt, @JsonKey(name: 'unit_cost')  num? unitCost, @JsonKey(name: 'created_at')  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _PantryItemDto():
return $default(_that.id,_that.masterIngredientId,_that.customName,_that.ingredientName,_that.currentQuantity,_that.unit,_that.storageMode,_that.status,_that.source,_that.purchasedAt,_that.packagedAt,_that.expiresAt,_that.unitCost,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId, @JsonKey(name: 'custom_name')  String? customName, @JsonKey(name: 'ingredient_name')  String ingredientName, @JsonKey(name: 'current_quantity')  double currentQuantity,  String unit, @JsonKey(name: 'storage_mode')  String storageMode,  String status, @JsonKey(name: 'source')  String source, @JsonKey(name: 'purchased_at')  DateTime? purchasedAt, @JsonKey(name: 'packaged_at')  DateTime? packagedAt, @JsonKey(name: 'expires_at')  DateTime? expiresAt, @JsonKey(name: 'unit_cost')  num? unitCost, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _PantryItemDto() when $default != null:
return $default(_that.id,_that.masterIngredientId,_that.customName,_that.ingredientName,_that.currentQuantity,_that.unit,_that.storageMode,_that.status,_that.source,_that.purchasedAt,_that.packagedAt,_that.expiresAt,_that.unitCost,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _PantryItemDto extends PantryItemDto {
  const _PantryItemDto({required this.id, @JsonKey(name: 'master_ingredient_id') this.masterIngredientId, @JsonKey(name: 'custom_name') this.customName, @JsonKey(name: 'ingredient_name') required this.ingredientName, @JsonKey(name: 'current_quantity') required this.currentQuantity, required this.unit, @JsonKey(name: 'storage_mode') required this.storageMode, this.status = 'ACTIVE', @JsonKey(name: 'source') this.source = 'MANUAL', @JsonKey(name: 'purchased_at') this.purchasedAt, @JsonKey(name: 'packaged_at') this.packagedAt, @JsonKey(name: 'expires_at') this.expiresAt, @JsonKey(name: 'unit_cost') this.unitCost, @JsonKey(name: 'created_at') required this.createdAt}): super._();
  factory _PantryItemDto.fromJson(Map<String, dynamic> json) => _$PantryItemDtoFromJson(json);

@override final  String id;
@override@JsonKey(name: 'master_ingredient_id') final  String? masterIngredientId;
@override@JsonKey(name: 'custom_name') final  String? customName;
@override@JsonKey(name: 'ingredient_name') final  String ingredientName;
@override@JsonKey(name: 'current_quantity') final  double currentQuantity;
@override final  String unit;
@override@JsonKey(name: 'storage_mode') final  String storageMode;
@override@JsonKey() final  String status;
@override@JsonKey(name: 'source') final  String source;
@override@JsonKey(name: 'purchased_at') final  DateTime? purchasedAt;
@override@JsonKey(name: 'packaged_at') final  DateTime? packagedAt;
@override@JsonKey(name: 'expires_at') final  DateTime? expiresAt;
@override@JsonKey(name: 'unit_cost') final  num? unitCost;
@override@JsonKey(name: 'created_at') final  DateTime createdAt;

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _PantryItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId)&&(identical(other.customName, customName) || other.customName == customName)&&(identical(other.ingredientName, ingredientName) || other.ingredientName == ingredientName)&&(identical(other.currentQuantity, currentQuantity) || other.currentQuantity == currentQuantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageMode, storageMode) || other.storageMode == storageMode)&&(identical(other.status, status) || other.status == status)&&(identical(other.source, source) || other.source == source)&&(identical(other.purchasedAt, purchasedAt) || other.purchasedAt == purchasedAt)&&(identical(other.packagedAt, packagedAt) || other.packagedAt == packagedAt)&&(identical(other.expiresAt, expiresAt) || other.expiresAt == expiresAt)&&(identical(other.unitCost, unitCost) || other.unitCost == unitCost)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,masterIngredientId,customName,ingredientName,currentQuantity,unit,storageMode,status,source,purchasedAt,packagedAt,expiresAt,unitCost,createdAt);

@override
String toString() {
  return 'PantryItemDto(id: $id, masterIngredientId: $masterIngredientId, customName: $customName, ingredientName: $ingredientName, currentQuantity: $currentQuantity, unit: $unit, storageMode: $storageMode, status: $status, source: $source, purchasedAt: $purchasedAt, packagedAt: $packagedAt, expiresAt: $expiresAt, unitCost: $unitCost, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$PantryItemDtoCopyWith<$Res> implements $PantryItemDtoCopyWith<$Res> {
  factory _$PantryItemDtoCopyWith(_PantryItemDto value, $Res Function(_PantryItemDto) _then) = __$PantryItemDtoCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'master_ingredient_id') String? masterIngredientId,@JsonKey(name: 'custom_name') String? customName,@JsonKey(name: 'ingredient_name') String ingredientName,@JsonKey(name: 'current_quantity') double currentQuantity, String unit,@JsonKey(name: 'storage_mode') String storageMode, String status,@JsonKey(name: 'source') String source,@JsonKey(name: 'purchased_at') DateTime? purchasedAt,@JsonKey(name: 'packaged_at') DateTime? packagedAt,@JsonKey(name: 'expires_at') DateTime? expiresAt,@JsonKey(name: 'unit_cost') num? unitCost,@JsonKey(name: 'created_at') DateTime createdAt
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? masterIngredientId = freezed,Object? customName = freezed,Object? ingredientName = null,Object? currentQuantity = null,Object? unit = null,Object? storageMode = null,Object? status = null,Object? source = null,Object? purchasedAt = freezed,Object? packagedAt = freezed,Object? expiresAt = freezed,Object? unitCost = freezed,Object? createdAt = null,}) {
  return _then(_PantryItemDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,customName: freezed == customName ? _self.customName : customName // ignore: cast_nullable_to_non_nullable
as String?,ingredientName: null == ingredientName ? _self.ingredientName : ingredientName // ignore: cast_nullable_to_non_nullable
as String,currentQuantity: null == currentQuantity ? _self.currentQuantity : currentQuantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,storageMode: null == storageMode ? _self.storageMode : storageMode // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,source: null == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as String,purchasedAt: freezed == purchasedAt ? _self.purchasedAt : purchasedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,packagedAt: freezed == packagedAt ? _self.packagedAt : packagedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,expiresAt: freezed == expiresAt ? _self.expiresAt : expiresAt // ignore: cast_nullable_to_non_nullable
as DateTime?,unitCost: freezed == unitCost ? _self.unitCost : unitCost // ignore: cast_nullable_to_non_nullable
as num?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}

// dart format on
