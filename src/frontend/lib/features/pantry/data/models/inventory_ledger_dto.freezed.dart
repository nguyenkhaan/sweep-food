// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'inventory_ledger_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$InventoryLedgerEntryDto {

 String get id;@JsonKey(name: 'inventory_batch_id') String get inventoryBatchId;@JsonKey(name: 'event_type') String get eventType;@JsonKey(name: 'quantity_before', fromJson: _asDouble) double get quantityBefore;@JsonKey(name: 'quantity_delta', fromJson: _asDouble) double get quantityDelta;@JsonKey(name: 'quantity_after', fromJson: _asDouble) double get quantityAfter; String get unit;@JsonKey(name: 'cooking_session_id') String? get cookingSessionId;@JsonKey(name: 'idempotency_key') String? get idempotencyKey; String? get reason;@JsonKey(name: 'created_at') DateTime get createdAt;
/// Create a copy of InventoryLedgerEntryDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InventoryLedgerEntryDtoCopyWith<InventoryLedgerEntryDto> get copyWith => _$InventoryLedgerEntryDtoCopyWithImpl<InventoryLedgerEntryDto>(this as InventoryLedgerEntryDto, _$identity);

  /// Serializes this InventoryLedgerEntryDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is InventoryLedgerEntryDto&&(identical(other.id, id) || other.id == id)&&(identical(other.inventoryBatchId, inventoryBatchId) || other.inventoryBatchId == inventoryBatchId)&&(identical(other.eventType, eventType) || other.eventType == eventType)&&(identical(other.quantityBefore, quantityBefore) || other.quantityBefore == quantityBefore)&&(identical(other.quantityDelta, quantityDelta) || other.quantityDelta == quantityDelta)&&(identical(other.quantityAfter, quantityAfter) || other.quantityAfter == quantityAfter)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.cookingSessionId, cookingSessionId) || other.cookingSessionId == cookingSessionId)&&(identical(other.idempotencyKey, idempotencyKey) || other.idempotencyKey == idempotencyKey)&&(identical(other.reason, reason) || other.reason == reason)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,inventoryBatchId,eventType,quantityBefore,quantityDelta,quantityAfter,unit,cookingSessionId,idempotencyKey,reason,createdAt);

@override
String toString() {
  return 'InventoryLedgerEntryDto(id: $id, inventoryBatchId: $inventoryBatchId, eventType: $eventType, quantityBefore: $quantityBefore, quantityDelta: $quantityDelta, quantityAfter: $quantityAfter, unit: $unit, cookingSessionId: $cookingSessionId, idempotencyKey: $idempotencyKey, reason: $reason, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $InventoryLedgerEntryDtoCopyWith<$Res>  {
  factory $InventoryLedgerEntryDtoCopyWith(InventoryLedgerEntryDto value, $Res Function(InventoryLedgerEntryDto) _then) = _$InventoryLedgerEntryDtoCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'inventory_batch_id') String inventoryBatchId,@JsonKey(name: 'event_type') String eventType,@JsonKey(name: 'quantity_before', fromJson: _asDouble) double quantityBefore,@JsonKey(name: 'quantity_delta', fromJson: _asDouble) double quantityDelta,@JsonKey(name: 'quantity_after', fromJson: _asDouble) double quantityAfter, String unit,@JsonKey(name: 'cooking_session_id') String? cookingSessionId,@JsonKey(name: 'idempotency_key') String? idempotencyKey, String? reason,@JsonKey(name: 'created_at') DateTime createdAt
});




}
/// @nodoc
class _$InventoryLedgerEntryDtoCopyWithImpl<$Res>
    implements $InventoryLedgerEntryDtoCopyWith<$Res> {
  _$InventoryLedgerEntryDtoCopyWithImpl(this._self, this._then);

  final InventoryLedgerEntryDto _self;
  final $Res Function(InventoryLedgerEntryDto) _then;

/// Create a copy of InventoryLedgerEntryDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? inventoryBatchId = null,Object? eventType = null,Object? quantityBefore = null,Object? quantityDelta = null,Object? quantityAfter = null,Object? unit = null,Object? cookingSessionId = freezed,Object? idempotencyKey = freezed,Object? reason = freezed,Object? createdAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,inventoryBatchId: null == inventoryBatchId ? _self.inventoryBatchId : inventoryBatchId // ignore: cast_nullable_to_non_nullable
as String,eventType: null == eventType ? _self.eventType : eventType // ignore: cast_nullable_to_non_nullable
as String,quantityBefore: null == quantityBefore ? _self.quantityBefore : quantityBefore // ignore: cast_nullable_to_non_nullable
as double,quantityDelta: null == quantityDelta ? _self.quantityDelta : quantityDelta // ignore: cast_nullable_to_non_nullable
as double,quantityAfter: null == quantityAfter ? _self.quantityAfter : quantityAfter // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,cookingSessionId: freezed == cookingSessionId ? _self.cookingSessionId : cookingSessionId // ignore: cast_nullable_to_non_nullable
as String?,idempotencyKey: freezed == idempotencyKey ? _self.idempotencyKey : idempotencyKey // ignore: cast_nullable_to_non_nullable
as String?,reason: freezed == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [InventoryLedgerEntryDto].
extension InventoryLedgerEntryDtoPatterns on InventoryLedgerEntryDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _InventoryLedgerEntryDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _InventoryLedgerEntryDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _InventoryLedgerEntryDto value)  $default,){
final _that = this;
switch (_that) {
case _InventoryLedgerEntryDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _InventoryLedgerEntryDto value)?  $default,){
final _that = this;
switch (_that) {
case _InventoryLedgerEntryDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'inventory_batch_id')  String inventoryBatchId, @JsonKey(name: 'event_type')  String eventType, @JsonKey(name: 'quantity_before', fromJson: _asDouble)  double quantityBefore, @JsonKey(name: 'quantity_delta', fromJson: _asDouble)  double quantityDelta, @JsonKey(name: 'quantity_after', fromJson: _asDouble)  double quantityAfter,  String unit, @JsonKey(name: 'cooking_session_id')  String? cookingSessionId, @JsonKey(name: 'idempotency_key')  String? idempotencyKey,  String? reason, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _InventoryLedgerEntryDto() when $default != null:
return $default(_that.id,_that.inventoryBatchId,_that.eventType,_that.quantityBefore,_that.quantityDelta,_that.quantityAfter,_that.unit,_that.cookingSessionId,_that.idempotencyKey,_that.reason,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'inventory_batch_id')  String inventoryBatchId, @JsonKey(name: 'event_type')  String eventType, @JsonKey(name: 'quantity_before', fromJson: _asDouble)  double quantityBefore, @JsonKey(name: 'quantity_delta', fromJson: _asDouble)  double quantityDelta, @JsonKey(name: 'quantity_after', fromJson: _asDouble)  double quantityAfter,  String unit, @JsonKey(name: 'cooking_session_id')  String? cookingSessionId, @JsonKey(name: 'idempotency_key')  String? idempotencyKey,  String? reason, @JsonKey(name: 'created_at')  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _InventoryLedgerEntryDto():
return $default(_that.id,_that.inventoryBatchId,_that.eventType,_that.quantityBefore,_that.quantityDelta,_that.quantityAfter,_that.unit,_that.cookingSessionId,_that.idempotencyKey,_that.reason,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'inventory_batch_id')  String inventoryBatchId, @JsonKey(name: 'event_type')  String eventType, @JsonKey(name: 'quantity_before', fromJson: _asDouble)  double quantityBefore, @JsonKey(name: 'quantity_delta', fromJson: _asDouble)  double quantityDelta, @JsonKey(name: 'quantity_after', fromJson: _asDouble)  double quantityAfter,  String unit, @JsonKey(name: 'cooking_session_id')  String? cookingSessionId, @JsonKey(name: 'idempotency_key')  String? idempotencyKey,  String? reason, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _InventoryLedgerEntryDto() when $default != null:
return $default(_that.id,_that.inventoryBatchId,_that.eventType,_that.quantityBefore,_that.quantityDelta,_that.quantityAfter,_that.unit,_that.cookingSessionId,_that.idempotencyKey,_that.reason,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _InventoryLedgerEntryDto extends InventoryLedgerEntryDto {
  const _InventoryLedgerEntryDto({required this.id, @JsonKey(name: 'inventory_batch_id') required this.inventoryBatchId, @JsonKey(name: 'event_type') this.eventType = 'CORRECTION', @JsonKey(name: 'quantity_before', fromJson: _asDouble) this.quantityBefore = 0, @JsonKey(name: 'quantity_delta', fromJson: _asDouble) this.quantityDelta = 0, @JsonKey(name: 'quantity_after', fromJson: _asDouble) this.quantityAfter = 0, this.unit = 'GRAM', @JsonKey(name: 'cooking_session_id') this.cookingSessionId, @JsonKey(name: 'idempotency_key') this.idempotencyKey, this.reason, @JsonKey(name: 'created_at') required this.createdAt}): super._();
  factory _InventoryLedgerEntryDto.fromJson(Map<String, dynamic> json) => _$InventoryLedgerEntryDtoFromJson(json);

@override final  String id;
@override@JsonKey(name: 'inventory_batch_id') final  String inventoryBatchId;
@override@JsonKey(name: 'event_type') final  String eventType;
@override@JsonKey(name: 'quantity_before', fromJson: _asDouble) final  double quantityBefore;
@override@JsonKey(name: 'quantity_delta', fromJson: _asDouble) final  double quantityDelta;
@override@JsonKey(name: 'quantity_after', fromJson: _asDouble) final  double quantityAfter;
@override@JsonKey() final  String unit;
@override@JsonKey(name: 'cooking_session_id') final  String? cookingSessionId;
@override@JsonKey(name: 'idempotency_key') final  String? idempotencyKey;
@override final  String? reason;
@override@JsonKey(name: 'created_at') final  DateTime createdAt;

/// Create a copy of InventoryLedgerEntryDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InventoryLedgerEntryDtoCopyWith<_InventoryLedgerEntryDto> get copyWith => __$InventoryLedgerEntryDtoCopyWithImpl<_InventoryLedgerEntryDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$InventoryLedgerEntryDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _InventoryLedgerEntryDto&&(identical(other.id, id) || other.id == id)&&(identical(other.inventoryBatchId, inventoryBatchId) || other.inventoryBatchId == inventoryBatchId)&&(identical(other.eventType, eventType) || other.eventType == eventType)&&(identical(other.quantityBefore, quantityBefore) || other.quantityBefore == quantityBefore)&&(identical(other.quantityDelta, quantityDelta) || other.quantityDelta == quantityDelta)&&(identical(other.quantityAfter, quantityAfter) || other.quantityAfter == quantityAfter)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.cookingSessionId, cookingSessionId) || other.cookingSessionId == cookingSessionId)&&(identical(other.idempotencyKey, idempotencyKey) || other.idempotencyKey == idempotencyKey)&&(identical(other.reason, reason) || other.reason == reason)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,inventoryBatchId,eventType,quantityBefore,quantityDelta,quantityAfter,unit,cookingSessionId,idempotencyKey,reason,createdAt);

@override
String toString() {
  return 'InventoryLedgerEntryDto(id: $id, inventoryBatchId: $inventoryBatchId, eventType: $eventType, quantityBefore: $quantityBefore, quantityDelta: $quantityDelta, quantityAfter: $quantityAfter, unit: $unit, cookingSessionId: $cookingSessionId, idempotencyKey: $idempotencyKey, reason: $reason, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$InventoryLedgerEntryDtoCopyWith<$Res> implements $InventoryLedgerEntryDtoCopyWith<$Res> {
  factory _$InventoryLedgerEntryDtoCopyWith(_InventoryLedgerEntryDto value, $Res Function(_InventoryLedgerEntryDto) _then) = __$InventoryLedgerEntryDtoCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'inventory_batch_id') String inventoryBatchId,@JsonKey(name: 'event_type') String eventType,@JsonKey(name: 'quantity_before', fromJson: _asDouble) double quantityBefore,@JsonKey(name: 'quantity_delta', fromJson: _asDouble) double quantityDelta,@JsonKey(name: 'quantity_after', fromJson: _asDouble) double quantityAfter, String unit,@JsonKey(name: 'cooking_session_id') String? cookingSessionId,@JsonKey(name: 'idempotency_key') String? idempotencyKey, String? reason,@JsonKey(name: 'created_at') DateTime createdAt
});




}
/// @nodoc
class __$InventoryLedgerEntryDtoCopyWithImpl<$Res>
    implements _$InventoryLedgerEntryDtoCopyWith<$Res> {
  __$InventoryLedgerEntryDtoCopyWithImpl(this._self, this._then);

  final _InventoryLedgerEntryDto _self;
  final $Res Function(_InventoryLedgerEntryDto) _then;

/// Create a copy of InventoryLedgerEntryDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? inventoryBatchId = null,Object? eventType = null,Object? quantityBefore = null,Object? quantityDelta = null,Object? quantityAfter = null,Object? unit = null,Object? cookingSessionId = freezed,Object? idempotencyKey = freezed,Object? reason = freezed,Object? createdAt = null,}) {
  return _then(_InventoryLedgerEntryDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,inventoryBatchId: null == inventoryBatchId ? _self.inventoryBatchId : inventoryBatchId // ignore: cast_nullable_to_non_nullable
as String,eventType: null == eventType ? _self.eventType : eventType // ignore: cast_nullable_to_non_nullable
as String,quantityBefore: null == quantityBefore ? _self.quantityBefore : quantityBefore // ignore: cast_nullable_to_non_nullable
as double,quantityDelta: null == quantityDelta ? _self.quantityDelta : quantityDelta // ignore: cast_nullable_to_non_nullable
as double,quantityAfter: null == quantityAfter ? _self.quantityAfter : quantityAfter // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,cookingSessionId: freezed == cookingSessionId ? _self.cookingSessionId : cookingSessionId // ignore: cast_nullable_to_non_nullable
as String?,idempotencyKey: freezed == idempotencyKey ? _self.idempotencyKey : idempotencyKey // ignore: cast_nullable_to_non_nullable
as String?,reason: freezed == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}


/// @nodoc
mixin _$InventoryLedgerListDto {

 List<InventoryLedgerEntryDto> get items; int get total; int get page;@JsonKey(name: 'per_page') int get perPage;
/// Create a copy of InventoryLedgerListDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InventoryLedgerListDtoCopyWith<InventoryLedgerListDto> get copyWith => _$InventoryLedgerListDtoCopyWithImpl<InventoryLedgerListDto>(this as InventoryLedgerListDto, _$identity);

  /// Serializes this InventoryLedgerListDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is InventoryLedgerListDto&&const DeepCollectionEquality().equals(other.items, items)&&(identical(other.total, total) || other.total == total)&&(identical(other.page, page) || other.page == page)&&(identical(other.perPage, perPage) || other.perPage == perPage));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(items),total,page,perPage);

@override
String toString() {
  return 'InventoryLedgerListDto(items: $items, total: $total, page: $page, perPage: $perPage)';
}


}

/// @nodoc
abstract mixin class $InventoryLedgerListDtoCopyWith<$Res>  {
  factory $InventoryLedgerListDtoCopyWith(InventoryLedgerListDto value, $Res Function(InventoryLedgerListDto) _then) = _$InventoryLedgerListDtoCopyWithImpl;
@useResult
$Res call({
 List<InventoryLedgerEntryDto> items, int total, int page,@JsonKey(name: 'per_page') int perPage
});




}
/// @nodoc
class _$InventoryLedgerListDtoCopyWithImpl<$Res>
    implements $InventoryLedgerListDtoCopyWith<$Res> {
  _$InventoryLedgerListDtoCopyWithImpl(this._self, this._then);

  final InventoryLedgerListDto _self;
  final $Res Function(InventoryLedgerListDto) _then;

/// Create a copy of InventoryLedgerListDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? items = null,Object? total = null,Object? page = null,Object? perPage = null,}) {
  return _then(_self.copyWith(
items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<InventoryLedgerEntryDto>,total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,page: null == page ? _self.page : page // ignore: cast_nullable_to_non_nullable
as int,perPage: null == perPage ? _self.perPage : perPage // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [InventoryLedgerListDto].
extension InventoryLedgerListDtoPatterns on InventoryLedgerListDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _InventoryLedgerListDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _InventoryLedgerListDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _InventoryLedgerListDto value)  $default,){
final _that = this;
switch (_that) {
case _InventoryLedgerListDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _InventoryLedgerListDto value)?  $default,){
final _that = this;
switch (_that) {
case _InventoryLedgerListDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<InventoryLedgerEntryDto> items,  int total,  int page, @JsonKey(name: 'per_page')  int perPage)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _InventoryLedgerListDto() when $default != null:
return $default(_that.items,_that.total,_that.page,_that.perPage);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<InventoryLedgerEntryDto> items,  int total,  int page, @JsonKey(name: 'per_page')  int perPage)  $default,) {final _that = this;
switch (_that) {
case _InventoryLedgerListDto():
return $default(_that.items,_that.total,_that.page,_that.perPage);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<InventoryLedgerEntryDto> items,  int total,  int page, @JsonKey(name: 'per_page')  int perPage)?  $default,) {final _that = this;
switch (_that) {
case _InventoryLedgerListDto() when $default != null:
return $default(_that.items,_that.total,_that.page,_that.perPage);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _InventoryLedgerListDto implements InventoryLedgerListDto {
  const _InventoryLedgerListDto({final  List<InventoryLedgerEntryDto> items = const <InventoryLedgerEntryDto>[], this.total = 0, this.page = 1, @JsonKey(name: 'per_page') this.perPage = 20}): _items = items;
  factory _InventoryLedgerListDto.fromJson(Map<String, dynamic> json) => _$InventoryLedgerListDtoFromJson(json);

 final  List<InventoryLedgerEntryDto> _items;
@override@JsonKey() List<InventoryLedgerEntryDto> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}

@override@JsonKey() final  int total;
@override@JsonKey() final  int page;
@override@JsonKey(name: 'per_page') final  int perPage;

/// Create a copy of InventoryLedgerListDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InventoryLedgerListDtoCopyWith<_InventoryLedgerListDto> get copyWith => __$InventoryLedgerListDtoCopyWithImpl<_InventoryLedgerListDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$InventoryLedgerListDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _InventoryLedgerListDto&&const DeepCollectionEquality().equals(other._items, _items)&&(identical(other.total, total) || other.total == total)&&(identical(other.page, page) || other.page == page)&&(identical(other.perPage, perPage) || other.perPage == perPage));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_items),total,page,perPage);

@override
String toString() {
  return 'InventoryLedgerListDto(items: $items, total: $total, page: $page, perPage: $perPage)';
}


}

/// @nodoc
abstract mixin class _$InventoryLedgerListDtoCopyWith<$Res> implements $InventoryLedgerListDtoCopyWith<$Res> {
  factory _$InventoryLedgerListDtoCopyWith(_InventoryLedgerListDto value, $Res Function(_InventoryLedgerListDto) _then) = __$InventoryLedgerListDtoCopyWithImpl;
@override @useResult
$Res call({
 List<InventoryLedgerEntryDto> items, int total, int page,@JsonKey(name: 'per_page') int perPage
});




}
/// @nodoc
class __$InventoryLedgerListDtoCopyWithImpl<$Res>
    implements _$InventoryLedgerListDtoCopyWith<$Res> {
  __$InventoryLedgerListDtoCopyWithImpl(this._self, this._then);

  final _InventoryLedgerListDto _self;
  final $Res Function(_InventoryLedgerListDto) _then;

/// Create a copy of InventoryLedgerListDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? items = null,Object? total = null,Object? page = null,Object? perPage = null,}) {
  return _then(_InventoryLedgerListDto(
items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<InventoryLedgerEntryDto>,total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,page: null == page ? _self.page : page // ignore: cast_nullable_to_non_nullable
as int,perPage: null == perPage ? _self.perPage : perPage // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on
