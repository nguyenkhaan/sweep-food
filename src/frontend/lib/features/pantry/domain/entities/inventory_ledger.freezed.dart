// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'inventory_ledger.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$InventoryLedgerEntry {

 String get id; String get inventoryBatchId; LedgerEventType get eventType; double get quantityBefore; double get quantityDelta; double get quantityAfter; MeasurementUnit get unit; String? get cookingSessionId; String? get reason; DateTime get createdAt;
/// Create a copy of InventoryLedgerEntry
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InventoryLedgerEntryCopyWith<InventoryLedgerEntry> get copyWith => _$InventoryLedgerEntryCopyWithImpl<InventoryLedgerEntry>(this as InventoryLedgerEntry, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is InventoryLedgerEntry&&(identical(other.id, id) || other.id == id)&&(identical(other.inventoryBatchId, inventoryBatchId) || other.inventoryBatchId == inventoryBatchId)&&(identical(other.eventType, eventType) || other.eventType == eventType)&&(identical(other.quantityBefore, quantityBefore) || other.quantityBefore == quantityBefore)&&(identical(other.quantityDelta, quantityDelta) || other.quantityDelta == quantityDelta)&&(identical(other.quantityAfter, quantityAfter) || other.quantityAfter == quantityAfter)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.cookingSessionId, cookingSessionId) || other.cookingSessionId == cookingSessionId)&&(identical(other.reason, reason) || other.reason == reason)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}


@override
int get hashCode => Object.hash(runtimeType,id,inventoryBatchId,eventType,quantityBefore,quantityDelta,quantityAfter,unit,cookingSessionId,reason,createdAt);

@override
String toString() {
  return 'InventoryLedgerEntry(id: $id, inventoryBatchId: $inventoryBatchId, eventType: $eventType, quantityBefore: $quantityBefore, quantityDelta: $quantityDelta, quantityAfter: $quantityAfter, unit: $unit, cookingSessionId: $cookingSessionId, reason: $reason, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $InventoryLedgerEntryCopyWith<$Res>  {
  factory $InventoryLedgerEntryCopyWith(InventoryLedgerEntry value, $Res Function(InventoryLedgerEntry) _then) = _$InventoryLedgerEntryCopyWithImpl;
@useResult
$Res call({
 String id, String inventoryBatchId, LedgerEventType eventType, double quantityBefore, double quantityDelta, double quantityAfter, MeasurementUnit unit, String? cookingSessionId, String? reason, DateTime createdAt
});




}
/// @nodoc
class _$InventoryLedgerEntryCopyWithImpl<$Res>
    implements $InventoryLedgerEntryCopyWith<$Res> {
  _$InventoryLedgerEntryCopyWithImpl(this._self, this._then);

  final InventoryLedgerEntry _self;
  final $Res Function(InventoryLedgerEntry) _then;

/// Create a copy of InventoryLedgerEntry
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? inventoryBatchId = null,Object? eventType = null,Object? quantityBefore = null,Object? quantityDelta = null,Object? quantityAfter = null,Object? unit = null,Object? cookingSessionId = freezed,Object? reason = freezed,Object? createdAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,inventoryBatchId: null == inventoryBatchId ? _self.inventoryBatchId : inventoryBatchId // ignore: cast_nullable_to_non_nullable
as String,eventType: null == eventType ? _self.eventType : eventType // ignore: cast_nullable_to_non_nullable
as LedgerEventType,quantityBefore: null == quantityBefore ? _self.quantityBefore : quantityBefore // ignore: cast_nullable_to_non_nullable
as double,quantityDelta: null == quantityDelta ? _self.quantityDelta : quantityDelta // ignore: cast_nullable_to_non_nullable
as double,quantityAfter: null == quantityAfter ? _self.quantityAfter : quantityAfter // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,cookingSessionId: freezed == cookingSessionId ? _self.cookingSessionId : cookingSessionId // ignore: cast_nullable_to_non_nullable
as String?,reason: freezed == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [InventoryLedgerEntry].
extension InventoryLedgerEntryPatterns on InventoryLedgerEntry {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _InventoryLedgerEntry value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _InventoryLedgerEntry() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _InventoryLedgerEntry value)  $default,){
final _that = this;
switch (_that) {
case _InventoryLedgerEntry():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _InventoryLedgerEntry value)?  $default,){
final _that = this;
switch (_that) {
case _InventoryLedgerEntry() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String inventoryBatchId,  LedgerEventType eventType,  double quantityBefore,  double quantityDelta,  double quantityAfter,  MeasurementUnit unit,  String? cookingSessionId,  String? reason,  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _InventoryLedgerEntry() when $default != null:
return $default(_that.id,_that.inventoryBatchId,_that.eventType,_that.quantityBefore,_that.quantityDelta,_that.quantityAfter,_that.unit,_that.cookingSessionId,_that.reason,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String inventoryBatchId,  LedgerEventType eventType,  double quantityBefore,  double quantityDelta,  double quantityAfter,  MeasurementUnit unit,  String? cookingSessionId,  String? reason,  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _InventoryLedgerEntry():
return $default(_that.id,_that.inventoryBatchId,_that.eventType,_that.quantityBefore,_that.quantityDelta,_that.quantityAfter,_that.unit,_that.cookingSessionId,_that.reason,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String inventoryBatchId,  LedgerEventType eventType,  double quantityBefore,  double quantityDelta,  double quantityAfter,  MeasurementUnit unit,  String? cookingSessionId,  String? reason,  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _InventoryLedgerEntry() when $default != null:
return $default(_that.id,_that.inventoryBatchId,_that.eventType,_that.quantityBefore,_that.quantityDelta,_that.quantityAfter,_that.unit,_that.cookingSessionId,_that.reason,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc


class _InventoryLedgerEntry extends InventoryLedgerEntry {
  const _InventoryLedgerEntry({required this.id, required this.inventoryBatchId, required this.eventType, required this.quantityBefore, required this.quantityDelta, required this.quantityAfter, required this.unit, this.cookingSessionId, this.reason, required this.createdAt}): super._();
  

@override final  String id;
@override final  String inventoryBatchId;
@override final  LedgerEventType eventType;
@override final  double quantityBefore;
@override final  double quantityDelta;
@override final  double quantityAfter;
@override final  MeasurementUnit unit;
@override final  String? cookingSessionId;
@override final  String? reason;
@override final  DateTime createdAt;

/// Create a copy of InventoryLedgerEntry
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InventoryLedgerEntryCopyWith<_InventoryLedgerEntry> get copyWith => __$InventoryLedgerEntryCopyWithImpl<_InventoryLedgerEntry>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _InventoryLedgerEntry&&(identical(other.id, id) || other.id == id)&&(identical(other.inventoryBatchId, inventoryBatchId) || other.inventoryBatchId == inventoryBatchId)&&(identical(other.eventType, eventType) || other.eventType == eventType)&&(identical(other.quantityBefore, quantityBefore) || other.quantityBefore == quantityBefore)&&(identical(other.quantityDelta, quantityDelta) || other.quantityDelta == quantityDelta)&&(identical(other.quantityAfter, quantityAfter) || other.quantityAfter == quantityAfter)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.cookingSessionId, cookingSessionId) || other.cookingSessionId == cookingSessionId)&&(identical(other.reason, reason) || other.reason == reason)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}


@override
int get hashCode => Object.hash(runtimeType,id,inventoryBatchId,eventType,quantityBefore,quantityDelta,quantityAfter,unit,cookingSessionId,reason,createdAt);

@override
String toString() {
  return 'InventoryLedgerEntry(id: $id, inventoryBatchId: $inventoryBatchId, eventType: $eventType, quantityBefore: $quantityBefore, quantityDelta: $quantityDelta, quantityAfter: $quantityAfter, unit: $unit, cookingSessionId: $cookingSessionId, reason: $reason, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$InventoryLedgerEntryCopyWith<$Res> implements $InventoryLedgerEntryCopyWith<$Res> {
  factory _$InventoryLedgerEntryCopyWith(_InventoryLedgerEntry value, $Res Function(_InventoryLedgerEntry) _then) = __$InventoryLedgerEntryCopyWithImpl;
@override @useResult
$Res call({
 String id, String inventoryBatchId, LedgerEventType eventType, double quantityBefore, double quantityDelta, double quantityAfter, MeasurementUnit unit, String? cookingSessionId, String? reason, DateTime createdAt
});




}
/// @nodoc
class __$InventoryLedgerEntryCopyWithImpl<$Res>
    implements _$InventoryLedgerEntryCopyWith<$Res> {
  __$InventoryLedgerEntryCopyWithImpl(this._self, this._then);

  final _InventoryLedgerEntry _self;
  final $Res Function(_InventoryLedgerEntry) _then;

/// Create a copy of InventoryLedgerEntry
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? inventoryBatchId = null,Object? eventType = null,Object? quantityBefore = null,Object? quantityDelta = null,Object? quantityAfter = null,Object? unit = null,Object? cookingSessionId = freezed,Object? reason = freezed,Object? createdAt = null,}) {
  return _then(_InventoryLedgerEntry(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,inventoryBatchId: null == inventoryBatchId ? _self.inventoryBatchId : inventoryBatchId // ignore: cast_nullable_to_non_nullable
as String,eventType: null == eventType ? _self.eventType : eventType // ignore: cast_nullable_to_non_nullable
as LedgerEventType,quantityBefore: null == quantityBefore ? _self.quantityBefore : quantityBefore // ignore: cast_nullable_to_non_nullable
as double,quantityDelta: null == quantityDelta ? _self.quantityDelta : quantityDelta // ignore: cast_nullable_to_non_nullable
as double,quantityAfter: null == quantityAfter ? _self.quantityAfter : quantityAfter // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,cookingSessionId: freezed == cookingSessionId ? _self.cookingSessionId : cookingSessionId // ignore: cast_nullable_to_non_nullable
as String?,reason: freezed == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}

// dart format on
