// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'cooked_leftover_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$CookedLeftoverDto {

@JsonKey(name: 'batch_id') String get batchId;@JsonKey(name: 'cooking_session_id') String get cookingSessionId; double get quantity; String get unit;@JsonKey(name: 'storage_mode') String get storageMode;@JsonKey(name: 'expires_at') DateTime? get expiresAt;@JsonKey(name: 'created_at') DateTime get createdAt;
/// Create a copy of CookedLeftoverDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookedLeftoverDtoCopyWith<CookedLeftoverDto> get copyWith => _$CookedLeftoverDtoCopyWithImpl<CookedLeftoverDto>(this as CookedLeftoverDto, _$identity);

  /// Serializes this CookedLeftoverDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookedLeftoverDto&&(identical(other.batchId, batchId) || other.batchId == batchId)&&(identical(other.cookingSessionId, cookingSessionId) || other.cookingSessionId == cookingSessionId)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageMode, storageMode) || other.storageMode == storageMode)&&(identical(other.expiresAt, expiresAt) || other.expiresAt == expiresAt)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,batchId,cookingSessionId,quantity,unit,storageMode,expiresAt,createdAt);

@override
String toString() {
  return 'CookedLeftoverDto(batchId: $batchId, cookingSessionId: $cookingSessionId, quantity: $quantity, unit: $unit, storageMode: $storageMode, expiresAt: $expiresAt, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $CookedLeftoverDtoCopyWith<$Res>  {
  factory $CookedLeftoverDtoCopyWith(CookedLeftoverDto value, $Res Function(CookedLeftoverDto) _then) = _$CookedLeftoverDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'batch_id') String batchId,@JsonKey(name: 'cooking_session_id') String cookingSessionId, double quantity, String unit,@JsonKey(name: 'storage_mode') String storageMode,@JsonKey(name: 'expires_at') DateTime? expiresAt,@JsonKey(name: 'created_at') DateTime createdAt
});




}
/// @nodoc
class _$CookedLeftoverDtoCopyWithImpl<$Res>
    implements $CookedLeftoverDtoCopyWith<$Res> {
  _$CookedLeftoverDtoCopyWithImpl(this._self, this._then);

  final CookedLeftoverDto _self;
  final $Res Function(CookedLeftoverDto) _then;

/// Create a copy of CookedLeftoverDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? batchId = null,Object? cookingSessionId = null,Object? quantity = null,Object? unit = null,Object? storageMode = null,Object? expiresAt = freezed,Object? createdAt = null,}) {
  return _then(_self.copyWith(
batchId: null == batchId ? _self.batchId : batchId // ignore: cast_nullable_to_non_nullable
as String,cookingSessionId: null == cookingSessionId ? _self.cookingSessionId : cookingSessionId // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,storageMode: null == storageMode ? _self.storageMode : storageMode // ignore: cast_nullable_to_non_nullable
as String,expiresAt: freezed == expiresAt ? _self.expiresAt : expiresAt // ignore: cast_nullable_to_non_nullable
as DateTime?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [CookedLeftoverDto].
extension CookedLeftoverDtoPatterns on CookedLeftoverDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookedLeftoverDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookedLeftoverDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookedLeftoverDto value)  $default,){
final _that = this;
switch (_that) {
case _CookedLeftoverDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookedLeftoverDto value)?  $default,){
final _that = this;
switch (_that) {
case _CookedLeftoverDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'batch_id')  String batchId, @JsonKey(name: 'cooking_session_id')  String cookingSessionId,  double quantity,  String unit, @JsonKey(name: 'storage_mode')  String storageMode, @JsonKey(name: 'expires_at')  DateTime? expiresAt, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookedLeftoverDto() when $default != null:
return $default(_that.batchId,_that.cookingSessionId,_that.quantity,_that.unit,_that.storageMode,_that.expiresAt,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'batch_id')  String batchId, @JsonKey(name: 'cooking_session_id')  String cookingSessionId,  double quantity,  String unit, @JsonKey(name: 'storage_mode')  String storageMode, @JsonKey(name: 'expires_at')  DateTime? expiresAt, @JsonKey(name: 'created_at')  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _CookedLeftoverDto():
return $default(_that.batchId,_that.cookingSessionId,_that.quantity,_that.unit,_that.storageMode,_that.expiresAt,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'batch_id')  String batchId, @JsonKey(name: 'cooking_session_id')  String cookingSessionId,  double quantity,  String unit, @JsonKey(name: 'storage_mode')  String storageMode, @JsonKey(name: 'expires_at')  DateTime? expiresAt, @JsonKey(name: 'created_at')  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _CookedLeftoverDto() when $default != null:
return $default(_that.batchId,_that.cookingSessionId,_that.quantity,_that.unit,_that.storageMode,_that.expiresAt,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CookedLeftoverDto extends CookedLeftoverDto {
  const _CookedLeftoverDto({@JsonKey(name: 'batch_id') required this.batchId, @JsonKey(name: 'cooking_session_id') required this.cookingSessionId, required this.quantity, required this.unit, @JsonKey(name: 'storage_mode') required this.storageMode, @JsonKey(name: 'expires_at') this.expiresAt, @JsonKey(name: 'created_at') required this.createdAt}): super._();
  factory _CookedLeftoverDto.fromJson(Map<String, dynamic> json) => _$CookedLeftoverDtoFromJson(json);

@override@JsonKey(name: 'batch_id') final  String batchId;
@override@JsonKey(name: 'cooking_session_id') final  String cookingSessionId;
@override final  double quantity;
@override final  String unit;
@override@JsonKey(name: 'storage_mode') final  String storageMode;
@override@JsonKey(name: 'expires_at') final  DateTime? expiresAt;
@override@JsonKey(name: 'created_at') final  DateTime createdAt;

/// Create a copy of CookedLeftoverDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookedLeftoverDtoCopyWith<_CookedLeftoverDto> get copyWith => __$CookedLeftoverDtoCopyWithImpl<_CookedLeftoverDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CookedLeftoverDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookedLeftoverDto&&(identical(other.batchId, batchId) || other.batchId == batchId)&&(identical(other.cookingSessionId, cookingSessionId) || other.cookingSessionId == cookingSessionId)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageMode, storageMode) || other.storageMode == storageMode)&&(identical(other.expiresAt, expiresAt) || other.expiresAt == expiresAt)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,batchId,cookingSessionId,quantity,unit,storageMode,expiresAt,createdAt);

@override
String toString() {
  return 'CookedLeftoverDto(batchId: $batchId, cookingSessionId: $cookingSessionId, quantity: $quantity, unit: $unit, storageMode: $storageMode, expiresAt: $expiresAt, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$CookedLeftoverDtoCopyWith<$Res> implements $CookedLeftoverDtoCopyWith<$Res> {
  factory _$CookedLeftoverDtoCopyWith(_CookedLeftoverDto value, $Res Function(_CookedLeftoverDto) _then) = __$CookedLeftoverDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'batch_id') String batchId,@JsonKey(name: 'cooking_session_id') String cookingSessionId, double quantity, String unit,@JsonKey(name: 'storage_mode') String storageMode,@JsonKey(name: 'expires_at') DateTime? expiresAt,@JsonKey(name: 'created_at') DateTime createdAt
});




}
/// @nodoc
class __$CookedLeftoverDtoCopyWithImpl<$Res>
    implements _$CookedLeftoverDtoCopyWith<$Res> {
  __$CookedLeftoverDtoCopyWithImpl(this._self, this._then);

  final _CookedLeftoverDto _self;
  final $Res Function(_CookedLeftoverDto) _then;

/// Create a copy of CookedLeftoverDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? batchId = null,Object? cookingSessionId = null,Object? quantity = null,Object? unit = null,Object? storageMode = null,Object? expiresAt = freezed,Object? createdAt = null,}) {
  return _then(_CookedLeftoverDto(
batchId: null == batchId ? _self.batchId : batchId // ignore: cast_nullable_to_non_nullable
as String,cookingSessionId: null == cookingSessionId ? _self.cookingSessionId : cookingSessionId // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,storageMode: null == storageMode ? _self.storageMode : storageMode // ignore: cast_nullable_to_non_nullable
as String,expiresAt: freezed == expiresAt ? _self.expiresAt : expiresAt // ignore: cast_nullable_to_non_nullable
as DateTime?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}

// dart format on
