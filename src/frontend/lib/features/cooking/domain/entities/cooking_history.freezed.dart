// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'cooking_history.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$CookingHistoryEntry {

 String get sessionId; String get recipeId; String get recipeName; double get servings; CookingSessionStatus get status; DateTime? get completedAt;
/// Create a copy of CookingHistoryEntry
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookingHistoryEntryCopyWith<CookingHistoryEntry> get copyWith => _$CookingHistoryEntryCopyWithImpl<CookingHistoryEntry>(this as CookingHistoryEntry, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookingHistoryEntry&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.servings, servings) || other.servings == servings)&&(identical(other.status, status) || other.status == status)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt));
}


@override
int get hashCode => Object.hash(runtimeType,sessionId,recipeId,recipeName,servings,status,completedAt);

@override
String toString() {
  return 'CookingHistoryEntry(sessionId: $sessionId, recipeId: $recipeId, recipeName: $recipeName, servings: $servings, status: $status, completedAt: $completedAt)';
}


}

/// @nodoc
abstract mixin class $CookingHistoryEntryCopyWith<$Res>  {
  factory $CookingHistoryEntryCopyWith(CookingHistoryEntry value, $Res Function(CookingHistoryEntry) _then) = _$CookingHistoryEntryCopyWithImpl;
@useResult
$Res call({
 String sessionId, String recipeId, String recipeName, double servings, CookingSessionStatus status, DateTime? completedAt
});




}
/// @nodoc
class _$CookingHistoryEntryCopyWithImpl<$Res>
    implements $CookingHistoryEntryCopyWith<$Res> {
  _$CookingHistoryEntryCopyWithImpl(this._self, this._then);

  final CookingHistoryEntry _self;
  final $Res Function(CookingHistoryEntry) _then;

/// Create a copy of CookingHistoryEntry
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? sessionId = null,Object? recipeId = null,Object? recipeName = null,Object? servings = null,Object? status = null,Object? completedAt = freezed,}) {
  return _then(_self.copyWith(
sessionId: null == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as CookingSessionStatus,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,
  ));
}

}


/// Adds pattern-matching-related methods to [CookingHistoryEntry].
extension CookingHistoryEntryPatterns on CookingHistoryEntry {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookingHistoryEntry value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookingHistoryEntry() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookingHistoryEntry value)  $default,){
final _that = this;
switch (_that) {
case _CookingHistoryEntry():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookingHistoryEntry value)?  $default,){
final _that = this;
switch (_that) {
case _CookingHistoryEntry() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String sessionId,  String recipeId,  String recipeName,  double servings,  CookingSessionStatus status,  DateTime? completedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookingHistoryEntry() when $default != null:
return $default(_that.sessionId,_that.recipeId,_that.recipeName,_that.servings,_that.status,_that.completedAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String sessionId,  String recipeId,  String recipeName,  double servings,  CookingSessionStatus status,  DateTime? completedAt)  $default,) {final _that = this;
switch (_that) {
case _CookingHistoryEntry():
return $default(_that.sessionId,_that.recipeId,_that.recipeName,_that.servings,_that.status,_that.completedAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String sessionId,  String recipeId,  String recipeName,  double servings,  CookingSessionStatus status,  DateTime? completedAt)?  $default,) {final _that = this;
switch (_that) {
case _CookingHistoryEntry() when $default != null:
return $default(_that.sessionId,_that.recipeId,_that.recipeName,_that.servings,_that.status,_that.completedAt);case _:
  return null;

}
}

}

/// @nodoc


class _CookingHistoryEntry implements CookingHistoryEntry {
  const _CookingHistoryEntry({required this.sessionId, required this.recipeId, required this.recipeName, required this.servings, required this.status, this.completedAt});
  

@override final  String sessionId;
@override final  String recipeId;
@override final  String recipeName;
@override final  double servings;
@override final  CookingSessionStatus status;
@override final  DateTime? completedAt;

/// Create a copy of CookingHistoryEntry
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookingHistoryEntryCopyWith<_CookingHistoryEntry> get copyWith => __$CookingHistoryEntryCopyWithImpl<_CookingHistoryEntry>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookingHistoryEntry&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.servings, servings) || other.servings == servings)&&(identical(other.status, status) || other.status == status)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt));
}


@override
int get hashCode => Object.hash(runtimeType,sessionId,recipeId,recipeName,servings,status,completedAt);

@override
String toString() {
  return 'CookingHistoryEntry(sessionId: $sessionId, recipeId: $recipeId, recipeName: $recipeName, servings: $servings, status: $status, completedAt: $completedAt)';
}


}

/// @nodoc
abstract mixin class _$CookingHistoryEntryCopyWith<$Res> implements $CookingHistoryEntryCopyWith<$Res> {
  factory _$CookingHistoryEntryCopyWith(_CookingHistoryEntry value, $Res Function(_CookingHistoryEntry) _then) = __$CookingHistoryEntryCopyWithImpl;
@override @useResult
$Res call({
 String sessionId, String recipeId, String recipeName, double servings, CookingSessionStatus status, DateTime? completedAt
});




}
/// @nodoc
class __$CookingHistoryEntryCopyWithImpl<$Res>
    implements _$CookingHistoryEntryCopyWith<$Res> {
  __$CookingHistoryEntryCopyWithImpl(this._self, this._then);

  final _CookingHistoryEntry _self;
  final $Res Function(_CookingHistoryEntry) _then;

/// Create a copy of CookingHistoryEntry
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? sessionId = null,Object? recipeId = null,Object? recipeName = null,Object? servings = null,Object? status = null,Object? completedAt = freezed,}) {
  return _then(_CookingHistoryEntry(
sessionId: null == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as CookingSessionStatus,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,
  ));
}


}

/// @nodoc
mixin _$CookingConsumption {

 String? get recipeIngredientId; String get inventoryBatchId; double get quantity; MeasurementUnit get unit;
/// Create a copy of CookingConsumption
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookingConsumptionCopyWith<CookingConsumption> get copyWith => _$CookingConsumptionCopyWithImpl<CookingConsumption>(this as CookingConsumption, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookingConsumption&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.inventoryBatchId, inventoryBatchId) || other.inventoryBatchId == inventoryBatchId)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit));
}


@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,inventoryBatchId,quantity,unit);

@override
String toString() {
  return 'CookingConsumption(recipeIngredientId: $recipeIngredientId, inventoryBatchId: $inventoryBatchId, quantity: $quantity, unit: $unit)';
}


}

/// @nodoc
abstract mixin class $CookingConsumptionCopyWith<$Res>  {
  factory $CookingConsumptionCopyWith(CookingConsumption value, $Res Function(CookingConsumption) _then) = _$CookingConsumptionCopyWithImpl;
@useResult
$Res call({
 String? recipeIngredientId, String inventoryBatchId, double quantity, MeasurementUnit unit
});




}
/// @nodoc
class _$CookingConsumptionCopyWithImpl<$Res>
    implements $CookingConsumptionCopyWith<$Res> {
  _$CookingConsumptionCopyWithImpl(this._self, this._then);

  final CookingConsumption _self;
  final $Res Function(CookingConsumption) _then;

/// Create a copy of CookingConsumption
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeIngredientId = freezed,Object? inventoryBatchId = null,Object? quantity = null,Object? unit = null,}) {
  return _then(_self.copyWith(
recipeIngredientId: freezed == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String?,inventoryBatchId: null == inventoryBatchId ? _self.inventoryBatchId : inventoryBatchId // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,
  ));
}

}


/// Adds pattern-matching-related methods to [CookingConsumption].
extension CookingConsumptionPatterns on CookingConsumption {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookingConsumption value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookingConsumption() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookingConsumption value)  $default,){
final _that = this;
switch (_that) {
case _CookingConsumption():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookingConsumption value)?  $default,){
final _that = this;
switch (_that) {
case _CookingConsumption() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? recipeIngredientId,  String inventoryBatchId,  double quantity,  MeasurementUnit unit)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookingConsumption() when $default != null:
return $default(_that.recipeIngredientId,_that.inventoryBatchId,_that.quantity,_that.unit);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? recipeIngredientId,  String inventoryBatchId,  double quantity,  MeasurementUnit unit)  $default,) {final _that = this;
switch (_that) {
case _CookingConsumption():
return $default(_that.recipeIngredientId,_that.inventoryBatchId,_that.quantity,_that.unit);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? recipeIngredientId,  String inventoryBatchId,  double quantity,  MeasurementUnit unit)?  $default,) {final _that = this;
switch (_that) {
case _CookingConsumption() when $default != null:
return $default(_that.recipeIngredientId,_that.inventoryBatchId,_that.quantity,_that.unit);case _:
  return null;

}
}

}

/// @nodoc


class _CookingConsumption implements CookingConsumption {
  const _CookingConsumption({this.recipeIngredientId, required this.inventoryBatchId, required this.quantity, required this.unit});
  

@override final  String? recipeIngredientId;
@override final  String inventoryBatchId;
@override final  double quantity;
@override final  MeasurementUnit unit;

/// Create a copy of CookingConsumption
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookingConsumptionCopyWith<_CookingConsumption> get copyWith => __$CookingConsumptionCopyWithImpl<_CookingConsumption>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookingConsumption&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.inventoryBatchId, inventoryBatchId) || other.inventoryBatchId == inventoryBatchId)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit));
}


@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,inventoryBatchId,quantity,unit);

@override
String toString() {
  return 'CookingConsumption(recipeIngredientId: $recipeIngredientId, inventoryBatchId: $inventoryBatchId, quantity: $quantity, unit: $unit)';
}


}

/// @nodoc
abstract mixin class _$CookingConsumptionCopyWith<$Res> implements $CookingConsumptionCopyWith<$Res> {
  factory _$CookingConsumptionCopyWith(_CookingConsumption value, $Res Function(_CookingConsumption) _then) = __$CookingConsumptionCopyWithImpl;
@override @useResult
$Res call({
 String? recipeIngredientId, String inventoryBatchId, double quantity, MeasurementUnit unit
});




}
/// @nodoc
class __$CookingConsumptionCopyWithImpl<$Res>
    implements _$CookingConsumptionCopyWith<$Res> {
  __$CookingConsumptionCopyWithImpl(this._self, this._then);

  final _CookingConsumption _self;
  final $Res Function(_CookingConsumption) _then;

/// Create a copy of CookingConsumption
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeIngredientId = freezed,Object? inventoryBatchId = null,Object? quantity = null,Object? unit = null,}) {
  return _then(_CookingConsumption(
recipeIngredientId: freezed == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String?,inventoryBatchId: null == inventoryBatchId ? _self.inventoryBatchId : inventoryBatchId // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,
  ));
}


}

/// @nodoc
mixin _$CookingHistoryDetail {

 String get sessionId; String get recipeId; String get recipeName; double get servings; CookingSessionStatus get status;/// Which consumption mode was used at completion (`EXACT`/`HALF`/…).
 CookMode? get consumptionMode; DateTime? get completedAt; String? get leftoverBatchId; List<CookingConsumption> get consumptions;
/// Create a copy of CookingHistoryDetail
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookingHistoryDetailCopyWith<CookingHistoryDetail> get copyWith => _$CookingHistoryDetailCopyWithImpl<CookingHistoryDetail>(this as CookingHistoryDetail, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookingHistoryDetail&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.servings, servings) || other.servings == servings)&&(identical(other.status, status) || other.status == status)&&(identical(other.consumptionMode, consumptionMode) || other.consumptionMode == consumptionMode)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt)&&(identical(other.leftoverBatchId, leftoverBatchId) || other.leftoverBatchId == leftoverBatchId)&&const DeepCollectionEquality().equals(other.consumptions, consumptions));
}


@override
int get hashCode => Object.hash(runtimeType,sessionId,recipeId,recipeName,servings,status,consumptionMode,completedAt,leftoverBatchId,const DeepCollectionEquality().hash(consumptions));

@override
String toString() {
  return 'CookingHistoryDetail(sessionId: $sessionId, recipeId: $recipeId, recipeName: $recipeName, servings: $servings, status: $status, consumptionMode: $consumptionMode, completedAt: $completedAt, leftoverBatchId: $leftoverBatchId, consumptions: $consumptions)';
}


}

/// @nodoc
abstract mixin class $CookingHistoryDetailCopyWith<$Res>  {
  factory $CookingHistoryDetailCopyWith(CookingHistoryDetail value, $Res Function(CookingHistoryDetail) _then) = _$CookingHistoryDetailCopyWithImpl;
@useResult
$Res call({
 String sessionId, String recipeId, String recipeName, double servings, CookingSessionStatus status, CookMode? consumptionMode, DateTime? completedAt, String? leftoverBatchId, List<CookingConsumption> consumptions
});




}
/// @nodoc
class _$CookingHistoryDetailCopyWithImpl<$Res>
    implements $CookingHistoryDetailCopyWith<$Res> {
  _$CookingHistoryDetailCopyWithImpl(this._self, this._then);

  final CookingHistoryDetail _self;
  final $Res Function(CookingHistoryDetail) _then;

/// Create a copy of CookingHistoryDetail
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? sessionId = null,Object? recipeId = null,Object? recipeName = null,Object? servings = null,Object? status = null,Object? consumptionMode = freezed,Object? completedAt = freezed,Object? leftoverBatchId = freezed,Object? consumptions = null,}) {
  return _then(_self.copyWith(
sessionId: null == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as CookingSessionStatus,consumptionMode: freezed == consumptionMode ? _self.consumptionMode : consumptionMode // ignore: cast_nullable_to_non_nullable
as CookMode?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,leftoverBatchId: freezed == leftoverBatchId ? _self.leftoverBatchId : leftoverBatchId // ignore: cast_nullable_to_non_nullable
as String?,consumptions: null == consumptions ? _self.consumptions : consumptions // ignore: cast_nullable_to_non_nullable
as List<CookingConsumption>,
  ));
}

}


/// Adds pattern-matching-related methods to [CookingHistoryDetail].
extension CookingHistoryDetailPatterns on CookingHistoryDetail {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookingHistoryDetail value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookingHistoryDetail() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookingHistoryDetail value)  $default,){
final _that = this;
switch (_that) {
case _CookingHistoryDetail():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookingHistoryDetail value)?  $default,){
final _that = this;
switch (_that) {
case _CookingHistoryDetail() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String sessionId,  String recipeId,  String recipeName,  double servings,  CookingSessionStatus status,  CookMode? consumptionMode,  DateTime? completedAt,  String? leftoverBatchId,  List<CookingConsumption> consumptions)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookingHistoryDetail() when $default != null:
return $default(_that.sessionId,_that.recipeId,_that.recipeName,_that.servings,_that.status,_that.consumptionMode,_that.completedAt,_that.leftoverBatchId,_that.consumptions);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String sessionId,  String recipeId,  String recipeName,  double servings,  CookingSessionStatus status,  CookMode? consumptionMode,  DateTime? completedAt,  String? leftoverBatchId,  List<CookingConsumption> consumptions)  $default,) {final _that = this;
switch (_that) {
case _CookingHistoryDetail():
return $default(_that.sessionId,_that.recipeId,_that.recipeName,_that.servings,_that.status,_that.consumptionMode,_that.completedAt,_that.leftoverBatchId,_that.consumptions);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String sessionId,  String recipeId,  String recipeName,  double servings,  CookingSessionStatus status,  CookMode? consumptionMode,  DateTime? completedAt,  String? leftoverBatchId,  List<CookingConsumption> consumptions)?  $default,) {final _that = this;
switch (_that) {
case _CookingHistoryDetail() when $default != null:
return $default(_that.sessionId,_that.recipeId,_that.recipeName,_that.servings,_that.status,_that.consumptionMode,_that.completedAt,_that.leftoverBatchId,_that.consumptions);case _:
  return null;

}
}

}

/// @nodoc


class _CookingHistoryDetail implements CookingHistoryDetail {
  const _CookingHistoryDetail({required this.sessionId, required this.recipeId, required this.recipeName, required this.servings, required this.status, this.consumptionMode, this.completedAt, this.leftoverBatchId, final  List<CookingConsumption> consumptions = const <CookingConsumption>[]}): _consumptions = consumptions;
  

@override final  String sessionId;
@override final  String recipeId;
@override final  String recipeName;
@override final  double servings;
@override final  CookingSessionStatus status;
/// Which consumption mode was used at completion (`EXACT`/`HALF`/…).
@override final  CookMode? consumptionMode;
@override final  DateTime? completedAt;
@override final  String? leftoverBatchId;
 final  List<CookingConsumption> _consumptions;
@override@JsonKey() List<CookingConsumption> get consumptions {
  if (_consumptions is EqualUnmodifiableListView) return _consumptions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_consumptions);
}


/// Create a copy of CookingHistoryDetail
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookingHistoryDetailCopyWith<_CookingHistoryDetail> get copyWith => __$CookingHistoryDetailCopyWithImpl<_CookingHistoryDetail>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookingHistoryDetail&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.servings, servings) || other.servings == servings)&&(identical(other.status, status) || other.status == status)&&(identical(other.consumptionMode, consumptionMode) || other.consumptionMode == consumptionMode)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt)&&(identical(other.leftoverBatchId, leftoverBatchId) || other.leftoverBatchId == leftoverBatchId)&&const DeepCollectionEquality().equals(other._consumptions, _consumptions));
}


@override
int get hashCode => Object.hash(runtimeType,sessionId,recipeId,recipeName,servings,status,consumptionMode,completedAt,leftoverBatchId,const DeepCollectionEquality().hash(_consumptions));

@override
String toString() {
  return 'CookingHistoryDetail(sessionId: $sessionId, recipeId: $recipeId, recipeName: $recipeName, servings: $servings, status: $status, consumptionMode: $consumptionMode, completedAt: $completedAt, leftoverBatchId: $leftoverBatchId, consumptions: $consumptions)';
}


}

/// @nodoc
abstract mixin class _$CookingHistoryDetailCopyWith<$Res> implements $CookingHistoryDetailCopyWith<$Res> {
  factory _$CookingHistoryDetailCopyWith(_CookingHistoryDetail value, $Res Function(_CookingHistoryDetail) _then) = __$CookingHistoryDetailCopyWithImpl;
@override @useResult
$Res call({
 String sessionId, String recipeId, String recipeName, double servings, CookingSessionStatus status, CookMode? consumptionMode, DateTime? completedAt, String? leftoverBatchId, List<CookingConsumption> consumptions
});




}
/// @nodoc
class __$CookingHistoryDetailCopyWithImpl<$Res>
    implements _$CookingHistoryDetailCopyWith<$Res> {
  __$CookingHistoryDetailCopyWithImpl(this._self, this._then);

  final _CookingHistoryDetail _self;
  final $Res Function(_CookingHistoryDetail) _then;

/// Create a copy of CookingHistoryDetail
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? sessionId = null,Object? recipeId = null,Object? recipeName = null,Object? servings = null,Object? status = null,Object? consumptionMode = freezed,Object? completedAt = freezed,Object? leftoverBatchId = freezed,Object? consumptions = null,}) {
  return _then(_CookingHistoryDetail(
sessionId: null == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as CookingSessionStatus,consumptionMode: freezed == consumptionMode ? _self.consumptionMode : consumptionMode // ignore: cast_nullable_to_non_nullable
as CookMode?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,leftoverBatchId: freezed == leftoverBatchId ? _self.leftoverBatchId : leftoverBatchId // ignore: cast_nullable_to_non_nullable
as String?,consumptions: null == consumptions ? _self._consumptions : consumptions // ignore: cast_nullable_to_non_nullable
as List<CookingConsumption>,
  ));
}


}

// dart format on
