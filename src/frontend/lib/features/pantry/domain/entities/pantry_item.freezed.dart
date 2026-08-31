// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'pantry_item.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$PantryItem {

 String get id; String get name; String get category; double get quantity; MeasurementUnit get unit; StorageTier get storageTier; DateTime get addedAt; PantrySource get source; PantryItemStatus get status; String? get ingredientId; DateTime? get packedDate; DateTime? get expiryDate; int? get referenceShelfLifeDays; int? get priceVnd;
/// Create a copy of PantryItem
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PantryItemCopyWith<PantryItem> get copyWith => _$PantryItemCopyWithImpl<PantryItem>(this as PantryItem, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PantryItem&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageTier, storageTier) || other.storageTier == storageTier)&&(identical(other.addedAt, addedAt) || other.addedAt == addedAt)&&(identical(other.source, source) || other.source == source)&&(identical(other.status, status) || other.status == status)&&(identical(other.ingredientId, ingredientId) || other.ingredientId == ingredientId)&&(identical(other.packedDate, packedDate) || other.packedDate == packedDate)&&(identical(other.expiryDate, expiryDate) || other.expiryDate == expiryDate)&&(identical(other.referenceShelfLifeDays, referenceShelfLifeDays) || other.referenceShelfLifeDays == referenceShelfLifeDays)&&(identical(other.priceVnd, priceVnd) || other.priceVnd == priceVnd));
}


@override
int get hashCode => Object.hash(runtimeType,id,name,category,quantity,unit,storageTier,addedAt,source,status,ingredientId,packedDate,expiryDate,referenceShelfLifeDays,priceVnd);

@override
String toString() {
  return 'PantryItem(id: $id, name: $name, category: $category, quantity: $quantity, unit: $unit, storageTier: $storageTier, addedAt: $addedAt, source: $source, status: $status, ingredientId: $ingredientId, packedDate: $packedDate, expiryDate: $expiryDate, referenceShelfLifeDays: $referenceShelfLifeDays, priceVnd: $priceVnd)';
}


}

/// @nodoc
abstract mixin class $PantryItemCopyWith<$Res>  {
  factory $PantryItemCopyWith(PantryItem value, $Res Function(PantryItem) _then) = _$PantryItemCopyWithImpl;
@useResult
$Res call({
 String id, String name, String category, double quantity, MeasurementUnit unit, StorageTier storageTier, DateTime addedAt, PantrySource source, PantryItemStatus status, String? ingredientId, DateTime? packedDate, DateTime? expiryDate, int? referenceShelfLifeDays, int? priceVnd
});




}
/// @nodoc
class _$PantryItemCopyWithImpl<$Res>
    implements $PantryItemCopyWith<$Res> {
  _$PantryItemCopyWithImpl(this._self, this._then);

  final PantryItem _self;
  final $Res Function(PantryItem) _then;

/// Create a copy of PantryItem
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? category = null,Object? quantity = null,Object? unit = null,Object? storageTier = null,Object? addedAt = null,Object? source = null,Object? status = null,Object? ingredientId = freezed,Object? packedDate = freezed,Object? expiryDate = freezed,Object? referenceShelfLifeDays = freezed,Object? priceVnd = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,storageTier: null == storageTier ? _self.storageTier : storageTier // ignore: cast_nullable_to_non_nullable
as StorageTier,addedAt: null == addedAt ? _self.addedAt : addedAt // ignore: cast_nullable_to_non_nullable
as DateTime,source: null == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as PantrySource,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as PantryItemStatus,ingredientId: freezed == ingredientId ? _self.ingredientId : ingredientId // ignore: cast_nullable_to_non_nullable
as String?,packedDate: freezed == packedDate ? _self.packedDate : packedDate // ignore: cast_nullable_to_non_nullable
as DateTime?,expiryDate: freezed == expiryDate ? _self.expiryDate : expiryDate // ignore: cast_nullable_to_non_nullable
as DateTime?,referenceShelfLifeDays: freezed == referenceShelfLifeDays ? _self.referenceShelfLifeDays : referenceShelfLifeDays // ignore: cast_nullable_to_non_nullable
as int?,priceVnd: freezed == priceVnd ? _self.priceVnd : priceVnd // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [PantryItem].
extension PantryItemPatterns on PantryItem {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PantryItem value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PantryItem() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PantryItem value)  $default,){
final _that = this;
switch (_that) {
case _PantryItem():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PantryItem value)?  $default,){
final _that = this;
switch (_that) {
case _PantryItem() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String category,  double quantity,  MeasurementUnit unit,  StorageTier storageTier,  DateTime addedAt,  PantrySource source,  PantryItemStatus status,  String? ingredientId,  DateTime? packedDate,  DateTime? expiryDate,  int? referenceShelfLifeDays,  int? priceVnd)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PantryItem() when $default != null:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String category,  double quantity,  MeasurementUnit unit,  StorageTier storageTier,  DateTime addedAt,  PantrySource source,  PantryItemStatus status,  String? ingredientId,  DateTime? packedDate,  DateTime? expiryDate,  int? referenceShelfLifeDays,  int? priceVnd)  $default,) {final _that = this;
switch (_that) {
case _PantryItem():
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String category,  double quantity,  MeasurementUnit unit,  StorageTier storageTier,  DateTime addedAt,  PantrySource source,  PantryItemStatus status,  String? ingredientId,  DateTime? packedDate,  DateTime? expiryDate,  int? referenceShelfLifeDays,  int? priceVnd)?  $default,) {final _that = this;
switch (_that) {
case _PantryItem() when $default != null:
return $default(_that.id,_that.name,_that.category,_that.quantity,_that.unit,_that.storageTier,_that.addedAt,_that.source,_that.status,_that.ingredientId,_that.packedDate,_that.expiryDate,_that.referenceShelfLifeDays,_that.priceVnd);case _:
  return null;

}
}

}

/// @nodoc


class _PantryItem extends PantryItem {
  const _PantryItem({required this.id, required this.name, required this.category, required this.quantity, required this.unit, required this.storageTier, required this.addedAt, required this.source, required this.status, this.ingredientId, this.packedDate, this.expiryDate, this.referenceShelfLifeDays, this.priceVnd}): super._();
  

@override final  String id;
@override final  String name;
@override final  String category;
@override final  double quantity;
@override final  MeasurementUnit unit;
@override final  StorageTier storageTier;
@override final  DateTime addedAt;
@override final  PantrySource source;
@override final  PantryItemStatus status;
@override final  String? ingredientId;
@override final  DateTime? packedDate;
@override final  DateTime? expiryDate;
@override final  int? referenceShelfLifeDays;
@override final  int? priceVnd;

/// Create a copy of PantryItem
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PantryItemCopyWith<_PantryItem> get copyWith => __$PantryItemCopyWithImpl<_PantryItem>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _PantryItem&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageTier, storageTier) || other.storageTier == storageTier)&&(identical(other.addedAt, addedAt) || other.addedAt == addedAt)&&(identical(other.source, source) || other.source == source)&&(identical(other.status, status) || other.status == status)&&(identical(other.ingredientId, ingredientId) || other.ingredientId == ingredientId)&&(identical(other.packedDate, packedDate) || other.packedDate == packedDate)&&(identical(other.expiryDate, expiryDate) || other.expiryDate == expiryDate)&&(identical(other.referenceShelfLifeDays, referenceShelfLifeDays) || other.referenceShelfLifeDays == referenceShelfLifeDays)&&(identical(other.priceVnd, priceVnd) || other.priceVnd == priceVnd));
}


@override
int get hashCode => Object.hash(runtimeType,id,name,category,quantity,unit,storageTier,addedAt,source,status,ingredientId,packedDate,expiryDate,referenceShelfLifeDays,priceVnd);

@override
String toString() {
  return 'PantryItem(id: $id, name: $name, category: $category, quantity: $quantity, unit: $unit, storageTier: $storageTier, addedAt: $addedAt, source: $source, status: $status, ingredientId: $ingredientId, packedDate: $packedDate, expiryDate: $expiryDate, referenceShelfLifeDays: $referenceShelfLifeDays, priceVnd: $priceVnd)';
}


}

/// @nodoc
abstract mixin class _$PantryItemCopyWith<$Res> implements $PantryItemCopyWith<$Res> {
  factory _$PantryItemCopyWith(_PantryItem value, $Res Function(_PantryItem) _then) = __$PantryItemCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String category, double quantity, MeasurementUnit unit, StorageTier storageTier, DateTime addedAt, PantrySource source, PantryItemStatus status, String? ingredientId, DateTime? packedDate, DateTime? expiryDate, int? referenceShelfLifeDays, int? priceVnd
});




}
/// @nodoc
class __$PantryItemCopyWithImpl<$Res>
    implements _$PantryItemCopyWith<$Res> {
  __$PantryItemCopyWithImpl(this._self, this._then);

  final _PantryItem _self;
  final $Res Function(_PantryItem) _then;

/// Create a copy of PantryItem
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? category = null,Object? quantity = null,Object? unit = null,Object? storageTier = null,Object? addedAt = null,Object? source = null,Object? status = null,Object? ingredientId = freezed,Object? packedDate = freezed,Object? expiryDate = freezed,Object? referenceShelfLifeDays = freezed,Object? priceVnd = freezed,}) {
  return _then(_PantryItem(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,storageTier: null == storageTier ? _self.storageTier : storageTier // ignore: cast_nullable_to_non_nullable
as StorageTier,addedAt: null == addedAt ? _self.addedAt : addedAt // ignore: cast_nullable_to_non_nullable
as DateTime,source: null == source ? _self.source : source // ignore: cast_nullable_to_non_nullable
as PantrySource,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as PantryItemStatus,ingredientId: freezed == ingredientId ? _self.ingredientId : ingredientId // ignore: cast_nullable_to_non_nullable
as String?,packedDate: freezed == packedDate ? _self.packedDate : packedDate // ignore: cast_nullable_to_non_nullable
as DateTime?,expiryDate: freezed == expiryDate ? _self.expiryDate : expiryDate // ignore: cast_nullable_to_non_nullable
as DateTime?,referenceShelfLifeDays: freezed == referenceShelfLifeDays ? _self.referenceShelfLifeDays : referenceShelfLifeDays // ignore: cast_nullable_to_non_nullable
as int?,priceVnd: freezed == priceVnd ? _self.priceVnd : priceVnd // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}

// dart format on
