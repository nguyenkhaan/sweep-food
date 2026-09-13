// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'cooking_history_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$CookingHistorySummaryDto {

@JsonKey(name: 'session_id') String get sessionId;@JsonKey(name: 'recipe_id') String get recipeId;@JsonKey(name: 'recipe_name') String get recipeName;@JsonKey(fromJson: _asDouble) double get servings; String get status;@JsonKey(name: 'completed_at') DateTime? get completedAt;
/// Create a copy of CookingHistorySummaryDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookingHistorySummaryDtoCopyWith<CookingHistorySummaryDto> get copyWith => _$CookingHistorySummaryDtoCopyWithImpl<CookingHistorySummaryDto>(this as CookingHistorySummaryDto, _$identity);

  /// Serializes this CookingHistorySummaryDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookingHistorySummaryDto&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.servings, servings) || other.servings == servings)&&(identical(other.status, status) || other.status == status)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,sessionId,recipeId,recipeName,servings,status,completedAt);

@override
String toString() {
  return 'CookingHistorySummaryDto(sessionId: $sessionId, recipeId: $recipeId, recipeName: $recipeName, servings: $servings, status: $status, completedAt: $completedAt)';
}


}

/// @nodoc
abstract mixin class $CookingHistorySummaryDtoCopyWith<$Res>  {
  factory $CookingHistorySummaryDtoCopyWith(CookingHistorySummaryDto value, $Res Function(CookingHistorySummaryDto) _then) = _$CookingHistorySummaryDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'session_id') String sessionId,@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName,@JsonKey(fromJson: _asDouble) double servings, String status,@JsonKey(name: 'completed_at') DateTime? completedAt
});




}
/// @nodoc
class _$CookingHistorySummaryDtoCopyWithImpl<$Res>
    implements $CookingHistorySummaryDtoCopyWith<$Res> {
  _$CookingHistorySummaryDtoCopyWithImpl(this._self, this._then);

  final CookingHistorySummaryDto _self;
  final $Res Function(CookingHistorySummaryDto) _then;

/// Create a copy of CookingHistorySummaryDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? sessionId = null,Object? recipeId = null,Object? recipeName = null,Object? servings = null,Object? status = null,Object? completedAt = freezed,}) {
  return _then(_self.copyWith(
sessionId: null == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,
  ));
}

}


/// Adds pattern-matching-related methods to [CookingHistorySummaryDto].
extension CookingHistorySummaryDtoPatterns on CookingHistorySummaryDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookingHistorySummaryDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookingHistorySummaryDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookingHistorySummaryDto value)  $default,){
final _that = this;
switch (_that) {
case _CookingHistorySummaryDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookingHistorySummaryDto value)?  $default,){
final _that = this;
switch (_that) {
case _CookingHistorySummaryDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'session_id')  String sessionId, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName, @JsonKey(fromJson: _asDouble)  double servings,  String status, @JsonKey(name: 'completed_at')  DateTime? completedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookingHistorySummaryDto() when $default != null:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'session_id')  String sessionId, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName, @JsonKey(fromJson: _asDouble)  double servings,  String status, @JsonKey(name: 'completed_at')  DateTime? completedAt)  $default,) {final _that = this;
switch (_that) {
case _CookingHistorySummaryDto():
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'session_id')  String sessionId, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName, @JsonKey(fromJson: _asDouble)  double servings,  String status, @JsonKey(name: 'completed_at')  DateTime? completedAt)?  $default,) {final _that = this;
switch (_that) {
case _CookingHistorySummaryDto() when $default != null:
return $default(_that.sessionId,_that.recipeId,_that.recipeName,_that.servings,_that.status,_that.completedAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CookingHistorySummaryDto extends CookingHistorySummaryDto {
  const _CookingHistorySummaryDto({@JsonKey(name: 'session_id') required this.sessionId, @JsonKey(name: 'recipe_id') required this.recipeId, @JsonKey(name: 'recipe_name') this.recipeName = '', @JsonKey(fromJson: _asDouble) this.servings = 0, this.status = 'COMPLETED', @JsonKey(name: 'completed_at') this.completedAt}): super._();
  factory _CookingHistorySummaryDto.fromJson(Map<String, dynamic> json) => _$CookingHistorySummaryDtoFromJson(json);

@override@JsonKey(name: 'session_id') final  String sessionId;
@override@JsonKey(name: 'recipe_id') final  String recipeId;
@override@JsonKey(name: 'recipe_name') final  String recipeName;
@override@JsonKey(fromJson: _asDouble) final  double servings;
@override@JsonKey() final  String status;
@override@JsonKey(name: 'completed_at') final  DateTime? completedAt;

/// Create a copy of CookingHistorySummaryDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookingHistorySummaryDtoCopyWith<_CookingHistorySummaryDto> get copyWith => __$CookingHistorySummaryDtoCopyWithImpl<_CookingHistorySummaryDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CookingHistorySummaryDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookingHistorySummaryDto&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.servings, servings) || other.servings == servings)&&(identical(other.status, status) || other.status == status)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,sessionId,recipeId,recipeName,servings,status,completedAt);

@override
String toString() {
  return 'CookingHistorySummaryDto(sessionId: $sessionId, recipeId: $recipeId, recipeName: $recipeName, servings: $servings, status: $status, completedAt: $completedAt)';
}


}

/// @nodoc
abstract mixin class _$CookingHistorySummaryDtoCopyWith<$Res> implements $CookingHistorySummaryDtoCopyWith<$Res> {
  factory _$CookingHistorySummaryDtoCopyWith(_CookingHistorySummaryDto value, $Res Function(_CookingHistorySummaryDto) _then) = __$CookingHistorySummaryDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'session_id') String sessionId,@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName,@JsonKey(fromJson: _asDouble) double servings, String status,@JsonKey(name: 'completed_at') DateTime? completedAt
});




}
/// @nodoc
class __$CookingHistorySummaryDtoCopyWithImpl<$Res>
    implements _$CookingHistorySummaryDtoCopyWith<$Res> {
  __$CookingHistorySummaryDtoCopyWithImpl(this._self, this._then);

  final _CookingHistorySummaryDto _self;
  final $Res Function(_CookingHistorySummaryDto) _then;

/// Create a copy of CookingHistorySummaryDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? sessionId = null,Object? recipeId = null,Object? recipeName = null,Object? servings = null,Object? status = null,Object? completedAt = freezed,}) {
  return _then(_CookingHistorySummaryDto(
sessionId: null == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,
  ));
}


}


/// @nodoc
mixin _$CookingHistoryListDto {

 List<CookingHistorySummaryDto> get items;
/// Create a copy of CookingHistoryListDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookingHistoryListDtoCopyWith<CookingHistoryListDto> get copyWith => _$CookingHistoryListDtoCopyWithImpl<CookingHistoryListDto>(this as CookingHistoryListDto, _$identity);

  /// Serializes this CookingHistoryListDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookingHistoryListDto&&const DeepCollectionEquality().equals(other.items, items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(items));

@override
String toString() {
  return 'CookingHistoryListDto(items: $items)';
}


}

/// @nodoc
abstract mixin class $CookingHistoryListDtoCopyWith<$Res>  {
  factory $CookingHistoryListDtoCopyWith(CookingHistoryListDto value, $Res Function(CookingHistoryListDto) _then) = _$CookingHistoryListDtoCopyWithImpl;
@useResult
$Res call({
 List<CookingHistorySummaryDto> items
});




}
/// @nodoc
class _$CookingHistoryListDtoCopyWithImpl<$Res>
    implements $CookingHistoryListDtoCopyWith<$Res> {
  _$CookingHistoryListDtoCopyWithImpl(this._self, this._then);

  final CookingHistoryListDto _self;
  final $Res Function(CookingHistoryListDto) _then;

/// Create a copy of CookingHistoryListDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? items = null,}) {
  return _then(_self.copyWith(
items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<CookingHistorySummaryDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [CookingHistoryListDto].
extension CookingHistoryListDtoPatterns on CookingHistoryListDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookingHistoryListDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookingHistoryListDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookingHistoryListDto value)  $default,){
final _that = this;
switch (_that) {
case _CookingHistoryListDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookingHistoryListDto value)?  $default,){
final _that = this;
switch (_that) {
case _CookingHistoryListDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<CookingHistorySummaryDto> items)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookingHistoryListDto() when $default != null:
return $default(_that.items);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<CookingHistorySummaryDto> items)  $default,) {final _that = this;
switch (_that) {
case _CookingHistoryListDto():
return $default(_that.items);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<CookingHistorySummaryDto> items)?  $default,) {final _that = this;
switch (_that) {
case _CookingHistoryListDto() when $default != null:
return $default(_that.items);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CookingHistoryListDto implements CookingHistoryListDto {
  const _CookingHistoryListDto({final  List<CookingHistorySummaryDto> items = const <CookingHistorySummaryDto>[]}): _items = items;
  factory _CookingHistoryListDto.fromJson(Map<String, dynamic> json) => _$CookingHistoryListDtoFromJson(json);

 final  List<CookingHistorySummaryDto> _items;
@override@JsonKey() List<CookingHistorySummaryDto> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


/// Create a copy of CookingHistoryListDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookingHistoryListDtoCopyWith<_CookingHistoryListDto> get copyWith => __$CookingHistoryListDtoCopyWithImpl<_CookingHistoryListDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CookingHistoryListDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookingHistoryListDto&&const DeepCollectionEquality().equals(other._items, _items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_items));

@override
String toString() {
  return 'CookingHistoryListDto(items: $items)';
}


}

/// @nodoc
abstract mixin class _$CookingHistoryListDtoCopyWith<$Res> implements $CookingHistoryListDtoCopyWith<$Res> {
  factory _$CookingHistoryListDtoCopyWith(_CookingHistoryListDto value, $Res Function(_CookingHistoryListDto) _then) = __$CookingHistoryListDtoCopyWithImpl;
@override @useResult
$Res call({
 List<CookingHistorySummaryDto> items
});




}
/// @nodoc
class __$CookingHistoryListDtoCopyWithImpl<$Res>
    implements _$CookingHistoryListDtoCopyWith<$Res> {
  __$CookingHistoryListDtoCopyWithImpl(this._self, this._then);

  final _CookingHistoryListDto _self;
  final $Res Function(_CookingHistoryListDto) _then;

/// Create a copy of CookingHistoryListDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? items = null,}) {
  return _then(_CookingHistoryListDto(
items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<CookingHistorySummaryDto>,
  ));
}


}


/// @nodoc
mixin _$CookingConsumptionDto {

@JsonKey(name: 'recipe_ingredient_id') String? get recipeIngredientId;@JsonKey(name: 'inventory_batch_id') String get inventoryBatchId;@JsonKey(fromJson: _asDouble) double get quantity; String get unit;
/// Create a copy of CookingConsumptionDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookingConsumptionDtoCopyWith<CookingConsumptionDto> get copyWith => _$CookingConsumptionDtoCopyWithImpl<CookingConsumptionDto>(this as CookingConsumptionDto, _$identity);

  /// Serializes this CookingConsumptionDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookingConsumptionDto&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.inventoryBatchId, inventoryBatchId) || other.inventoryBatchId == inventoryBatchId)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,inventoryBatchId,quantity,unit);

@override
String toString() {
  return 'CookingConsumptionDto(recipeIngredientId: $recipeIngredientId, inventoryBatchId: $inventoryBatchId, quantity: $quantity, unit: $unit)';
}


}

/// @nodoc
abstract mixin class $CookingConsumptionDtoCopyWith<$Res>  {
  factory $CookingConsumptionDtoCopyWith(CookingConsumptionDto value, $Res Function(CookingConsumptionDto) _then) = _$CookingConsumptionDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'recipe_ingredient_id') String? recipeIngredientId,@JsonKey(name: 'inventory_batch_id') String inventoryBatchId,@JsonKey(fromJson: _asDouble) double quantity, String unit
});




}
/// @nodoc
class _$CookingConsumptionDtoCopyWithImpl<$Res>
    implements $CookingConsumptionDtoCopyWith<$Res> {
  _$CookingConsumptionDtoCopyWithImpl(this._self, this._then);

  final CookingConsumptionDto _self;
  final $Res Function(CookingConsumptionDto) _then;

/// Create a copy of CookingConsumptionDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeIngredientId = freezed,Object? inventoryBatchId = null,Object? quantity = null,Object? unit = null,}) {
  return _then(_self.copyWith(
recipeIngredientId: freezed == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String?,inventoryBatchId: null == inventoryBatchId ? _self.inventoryBatchId : inventoryBatchId // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [CookingConsumptionDto].
extension CookingConsumptionDtoPatterns on CookingConsumptionDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookingConsumptionDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookingConsumptionDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookingConsumptionDto value)  $default,){
final _that = this;
switch (_that) {
case _CookingConsumptionDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookingConsumptionDto value)?  $default,){
final _that = this;
switch (_that) {
case _CookingConsumptionDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_ingredient_id')  String? recipeIngredientId, @JsonKey(name: 'inventory_batch_id')  String inventoryBatchId, @JsonKey(fromJson: _asDouble)  double quantity,  String unit)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookingConsumptionDto() when $default != null:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_ingredient_id')  String? recipeIngredientId, @JsonKey(name: 'inventory_batch_id')  String inventoryBatchId, @JsonKey(fromJson: _asDouble)  double quantity,  String unit)  $default,) {final _that = this;
switch (_that) {
case _CookingConsumptionDto():
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'recipe_ingredient_id')  String? recipeIngredientId, @JsonKey(name: 'inventory_batch_id')  String inventoryBatchId, @JsonKey(fromJson: _asDouble)  double quantity,  String unit)?  $default,) {final _that = this;
switch (_that) {
case _CookingConsumptionDto() when $default != null:
return $default(_that.recipeIngredientId,_that.inventoryBatchId,_that.quantity,_that.unit);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CookingConsumptionDto extends CookingConsumptionDto {
  const _CookingConsumptionDto({@JsonKey(name: 'recipe_ingredient_id') this.recipeIngredientId, @JsonKey(name: 'inventory_batch_id') required this.inventoryBatchId, @JsonKey(fromJson: _asDouble) this.quantity = 0, this.unit = 'GRAM'}): super._();
  factory _CookingConsumptionDto.fromJson(Map<String, dynamic> json) => _$CookingConsumptionDtoFromJson(json);

@override@JsonKey(name: 'recipe_ingredient_id') final  String? recipeIngredientId;
@override@JsonKey(name: 'inventory_batch_id') final  String inventoryBatchId;
@override@JsonKey(fromJson: _asDouble) final  double quantity;
@override@JsonKey() final  String unit;

/// Create a copy of CookingConsumptionDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookingConsumptionDtoCopyWith<_CookingConsumptionDto> get copyWith => __$CookingConsumptionDtoCopyWithImpl<_CookingConsumptionDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CookingConsumptionDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookingConsumptionDto&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.inventoryBatchId, inventoryBatchId) || other.inventoryBatchId == inventoryBatchId)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,inventoryBatchId,quantity,unit);

@override
String toString() {
  return 'CookingConsumptionDto(recipeIngredientId: $recipeIngredientId, inventoryBatchId: $inventoryBatchId, quantity: $quantity, unit: $unit)';
}


}

/// @nodoc
abstract mixin class _$CookingConsumptionDtoCopyWith<$Res> implements $CookingConsumptionDtoCopyWith<$Res> {
  factory _$CookingConsumptionDtoCopyWith(_CookingConsumptionDto value, $Res Function(_CookingConsumptionDto) _then) = __$CookingConsumptionDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'recipe_ingredient_id') String? recipeIngredientId,@JsonKey(name: 'inventory_batch_id') String inventoryBatchId,@JsonKey(fromJson: _asDouble) double quantity, String unit
});




}
/// @nodoc
class __$CookingConsumptionDtoCopyWithImpl<$Res>
    implements _$CookingConsumptionDtoCopyWith<$Res> {
  __$CookingConsumptionDtoCopyWithImpl(this._self, this._then);

  final _CookingConsumptionDto _self;
  final $Res Function(_CookingConsumptionDto) _then;

/// Create a copy of CookingConsumptionDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeIngredientId = freezed,Object? inventoryBatchId = null,Object? quantity = null,Object? unit = null,}) {
  return _then(_CookingConsumptionDto(
recipeIngredientId: freezed == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String?,inventoryBatchId: null == inventoryBatchId ? _self.inventoryBatchId : inventoryBatchId // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$CookingSessionDto {

 String get id;@JsonKey(name: 'recipe_id') String get recipeId;@JsonKey(name: 'meal_plan_item_id') String? get mealPlanItemId;@JsonKey(fromJson: _asDouble) double get servings; String get status;@JsonKey(name: 'consumption_mode') String? get consumptionMode;@JsonKey(name: 'completed_at') DateTime? get completedAt;
/// Create a copy of CookingSessionDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookingSessionDtoCopyWith<CookingSessionDto> get copyWith => _$CookingSessionDtoCopyWithImpl<CookingSessionDto>(this as CookingSessionDto, _$identity);

  /// Serializes this CookingSessionDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookingSessionDto&&(identical(other.id, id) || other.id == id)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.mealPlanItemId, mealPlanItemId) || other.mealPlanItemId == mealPlanItemId)&&(identical(other.servings, servings) || other.servings == servings)&&(identical(other.status, status) || other.status == status)&&(identical(other.consumptionMode, consumptionMode) || other.consumptionMode == consumptionMode)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,recipeId,mealPlanItemId,servings,status,consumptionMode,completedAt);

@override
String toString() {
  return 'CookingSessionDto(id: $id, recipeId: $recipeId, mealPlanItemId: $mealPlanItemId, servings: $servings, status: $status, consumptionMode: $consumptionMode, completedAt: $completedAt)';
}


}

/// @nodoc
abstract mixin class $CookingSessionDtoCopyWith<$Res>  {
  factory $CookingSessionDtoCopyWith(CookingSessionDto value, $Res Function(CookingSessionDto) _then) = _$CookingSessionDtoCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'meal_plan_item_id') String? mealPlanItemId,@JsonKey(fromJson: _asDouble) double servings, String status,@JsonKey(name: 'consumption_mode') String? consumptionMode,@JsonKey(name: 'completed_at') DateTime? completedAt
});




}
/// @nodoc
class _$CookingSessionDtoCopyWithImpl<$Res>
    implements $CookingSessionDtoCopyWith<$Res> {
  _$CookingSessionDtoCopyWithImpl(this._self, this._then);

  final CookingSessionDto _self;
  final $Res Function(CookingSessionDto) _then;

/// Create a copy of CookingSessionDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? recipeId = null,Object? mealPlanItemId = freezed,Object? servings = null,Object? status = null,Object? consumptionMode = freezed,Object? completedAt = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,mealPlanItemId: freezed == mealPlanItemId ? _self.mealPlanItemId : mealPlanItemId // ignore: cast_nullable_to_non_nullable
as String?,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,consumptionMode: freezed == consumptionMode ? _self.consumptionMode : consumptionMode // ignore: cast_nullable_to_non_nullable
as String?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,
  ));
}

}


/// Adds pattern-matching-related methods to [CookingSessionDto].
extension CookingSessionDtoPatterns on CookingSessionDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookingSessionDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookingSessionDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookingSessionDto value)  $default,){
final _that = this;
switch (_that) {
case _CookingSessionDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookingSessionDto value)?  $default,){
final _that = this;
switch (_that) {
case _CookingSessionDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'meal_plan_item_id')  String? mealPlanItemId, @JsonKey(fromJson: _asDouble)  double servings,  String status, @JsonKey(name: 'consumption_mode')  String? consumptionMode, @JsonKey(name: 'completed_at')  DateTime? completedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookingSessionDto() when $default != null:
return $default(_that.id,_that.recipeId,_that.mealPlanItemId,_that.servings,_that.status,_that.consumptionMode,_that.completedAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'meal_plan_item_id')  String? mealPlanItemId, @JsonKey(fromJson: _asDouble)  double servings,  String status, @JsonKey(name: 'consumption_mode')  String? consumptionMode, @JsonKey(name: 'completed_at')  DateTime? completedAt)  $default,) {final _that = this;
switch (_that) {
case _CookingSessionDto():
return $default(_that.id,_that.recipeId,_that.mealPlanItemId,_that.servings,_that.status,_that.consumptionMode,_that.completedAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'meal_plan_item_id')  String? mealPlanItemId, @JsonKey(fromJson: _asDouble)  double servings,  String status, @JsonKey(name: 'consumption_mode')  String? consumptionMode, @JsonKey(name: 'completed_at')  DateTime? completedAt)?  $default,) {final _that = this;
switch (_that) {
case _CookingSessionDto() when $default != null:
return $default(_that.id,_that.recipeId,_that.mealPlanItemId,_that.servings,_that.status,_that.consumptionMode,_that.completedAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CookingSessionDto implements CookingSessionDto {
  const _CookingSessionDto({required this.id, @JsonKey(name: 'recipe_id') required this.recipeId, @JsonKey(name: 'meal_plan_item_id') this.mealPlanItemId, @JsonKey(fromJson: _asDouble) this.servings = 0, this.status = 'COMPLETED', @JsonKey(name: 'consumption_mode') this.consumptionMode, @JsonKey(name: 'completed_at') this.completedAt});
  factory _CookingSessionDto.fromJson(Map<String, dynamic> json) => _$CookingSessionDtoFromJson(json);

@override final  String id;
@override@JsonKey(name: 'recipe_id') final  String recipeId;
@override@JsonKey(name: 'meal_plan_item_id') final  String? mealPlanItemId;
@override@JsonKey(fromJson: _asDouble) final  double servings;
@override@JsonKey() final  String status;
@override@JsonKey(name: 'consumption_mode') final  String? consumptionMode;
@override@JsonKey(name: 'completed_at') final  DateTime? completedAt;

/// Create a copy of CookingSessionDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookingSessionDtoCopyWith<_CookingSessionDto> get copyWith => __$CookingSessionDtoCopyWithImpl<_CookingSessionDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CookingSessionDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookingSessionDto&&(identical(other.id, id) || other.id == id)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.mealPlanItemId, mealPlanItemId) || other.mealPlanItemId == mealPlanItemId)&&(identical(other.servings, servings) || other.servings == servings)&&(identical(other.status, status) || other.status == status)&&(identical(other.consumptionMode, consumptionMode) || other.consumptionMode == consumptionMode)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,recipeId,mealPlanItemId,servings,status,consumptionMode,completedAt);

@override
String toString() {
  return 'CookingSessionDto(id: $id, recipeId: $recipeId, mealPlanItemId: $mealPlanItemId, servings: $servings, status: $status, consumptionMode: $consumptionMode, completedAt: $completedAt)';
}


}

/// @nodoc
abstract mixin class _$CookingSessionDtoCopyWith<$Res> implements $CookingSessionDtoCopyWith<$Res> {
  factory _$CookingSessionDtoCopyWith(_CookingSessionDto value, $Res Function(_CookingSessionDto) _then) = __$CookingSessionDtoCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'meal_plan_item_id') String? mealPlanItemId,@JsonKey(fromJson: _asDouble) double servings, String status,@JsonKey(name: 'consumption_mode') String? consumptionMode,@JsonKey(name: 'completed_at') DateTime? completedAt
});




}
/// @nodoc
class __$CookingSessionDtoCopyWithImpl<$Res>
    implements _$CookingSessionDtoCopyWith<$Res> {
  __$CookingSessionDtoCopyWithImpl(this._self, this._then);

  final _CookingSessionDto _self;
  final $Res Function(_CookingSessionDto) _then;

/// Create a copy of CookingSessionDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? recipeId = null,Object? mealPlanItemId = freezed,Object? servings = null,Object? status = null,Object? consumptionMode = freezed,Object? completedAt = freezed,}) {
  return _then(_CookingSessionDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,mealPlanItemId: freezed == mealPlanItemId ? _self.mealPlanItemId : mealPlanItemId // ignore: cast_nullable_to_non_nullable
as String?,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,consumptionMode: freezed == consumptionMode ? _self.consumptionMode : consumptionMode // ignore: cast_nullable_to_non_nullable
as String?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,
  ));
}


}


/// @nodoc
mixin _$CookingHistoryDetailDto {

 CookingSessionDto get session;@JsonKey(name: 'recipe_id') String get recipeId;@JsonKey(name: 'recipe_name') String get recipeName; List<CookingConsumptionDto> get consumptions;@JsonKey(name: 'leftover_batch_id') String? get leftoverBatchId;@JsonKey(name: 'completed_at') DateTime? get completedAt;
/// Create a copy of CookingHistoryDetailDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookingHistoryDetailDtoCopyWith<CookingHistoryDetailDto> get copyWith => _$CookingHistoryDetailDtoCopyWithImpl<CookingHistoryDetailDto>(this as CookingHistoryDetailDto, _$identity);

  /// Serializes this CookingHistoryDetailDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookingHistoryDetailDto&&(identical(other.session, session) || other.session == session)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&const DeepCollectionEquality().equals(other.consumptions, consumptions)&&(identical(other.leftoverBatchId, leftoverBatchId) || other.leftoverBatchId == leftoverBatchId)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,session,recipeId,recipeName,const DeepCollectionEquality().hash(consumptions),leftoverBatchId,completedAt);

@override
String toString() {
  return 'CookingHistoryDetailDto(session: $session, recipeId: $recipeId, recipeName: $recipeName, consumptions: $consumptions, leftoverBatchId: $leftoverBatchId, completedAt: $completedAt)';
}


}

/// @nodoc
abstract mixin class $CookingHistoryDetailDtoCopyWith<$Res>  {
  factory $CookingHistoryDetailDtoCopyWith(CookingHistoryDetailDto value, $Res Function(CookingHistoryDetailDto) _then) = _$CookingHistoryDetailDtoCopyWithImpl;
@useResult
$Res call({
 CookingSessionDto session,@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName, List<CookingConsumptionDto> consumptions,@JsonKey(name: 'leftover_batch_id') String? leftoverBatchId,@JsonKey(name: 'completed_at') DateTime? completedAt
});


$CookingSessionDtoCopyWith<$Res> get session;

}
/// @nodoc
class _$CookingHistoryDetailDtoCopyWithImpl<$Res>
    implements $CookingHistoryDetailDtoCopyWith<$Res> {
  _$CookingHistoryDetailDtoCopyWithImpl(this._self, this._then);

  final CookingHistoryDetailDto _self;
  final $Res Function(CookingHistoryDetailDto) _then;

/// Create a copy of CookingHistoryDetailDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? session = null,Object? recipeId = null,Object? recipeName = null,Object? consumptions = null,Object? leftoverBatchId = freezed,Object? completedAt = freezed,}) {
  return _then(_self.copyWith(
session: null == session ? _self.session : session // ignore: cast_nullable_to_non_nullable
as CookingSessionDto,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,consumptions: null == consumptions ? _self.consumptions : consumptions // ignore: cast_nullable_to_non_nullable
as List<CookingConsumptionDto>,leftoverBatchId: freezed == leftoverBatchId ? _self.leftoverBatchId : leftoverBatchId // ignore: cast_nullable_to_non_nullable
as String?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,
  ));
}
/// Create a copy of CookingHistoryDetailDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CookingSessionDtoCopyWith<$Res> get session {
  
  return $CookingSessionDtoCopyWith<$Res>(_self.session, (value) {
    return _then(_self.copyWith(session: value));
  });
}
}


/// Adds pattern-matching-related methods to [CookingHistoryDetailDto].
extension CookingHistoryDetailDtoPatterns on CookingHistoryDetailDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookingHistoryDetailDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookingHistoryDetailDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookingHistoryDetailDto value)  $default,){
final _that = this;
switch (_that) {
case _CookingHistoryDetailDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookingHistoryDetailDto value)?  $default,){
final _that = this;
switch (_that) {
case _CookingHistoryDetailDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( CookingSessionDto session, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName,  List<CookingConsumptionDto> consumptions, @JsonKey(name: 'leftover_batch_id')  String? leftoverBatchId, @JsonKey(name: 'completed_at')  DateTime? completedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookingHistoryDetailDto() when $default != null:
return $default(_that.session,_that.recipeId,_that.recipeName,_that.consumptions,_that.leftoverBatchId,_that.completedAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( CookingSessionDto session, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName,  List<CookingConsumptionDto> consumptions, @JsonKey(name: 'leftover_batch_id')  String? leftoverBatchId, @JsonKey(name: 'completed_at')  DateTime? completedAt)  $default,) {final _that = this;
switch (_that) {
case _CookingHistoryDetailDto():
return $default(_that.session,_that.recipeId,_that.recipeName,_that.consumptions,_that.leftoverBatchId,_that.completedAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( CookingSessionDto session, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName,  List<CookingConsumptionDto> consumptions, @JsonKey(name: 'leftover_batch_id')  String? leftoverBatchId, @JsonKey(name: 'completed_at')  DateTime? completedAt)?  $default,) {final _that = this;
switch (_that) {
case _CookingHistoryDetailDto() when $default != null:
return $default(_that.session,_that.recipeId,_that.recipeName,_that.consumptions,_that.leftoverBatchId,_that.completedAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CookingHistoryDetailDto extends CookingHistoryDetailDto {
  const _CookingHistoryDetailDto({required this.session, @JsonKey(name: 'recipe_id') required this.recipeId, @JsonKey(name: 'recipe_name') this.recipeName = '', final  List<CookingConsumptionDto> consumptions = const <CookingConsumptionDto>[], @JsonKey(name: 'leftover_batch_id') this.leftoverBatchId, @JsonKey(name: 'completed_at') this.completedAt}): _consumptions = consumptions,super._();
  factory _CookingHistoryDetailDto.fromJson(Map<String, dynamic> json) => _$CookingHistoryDetailDtoFromJson(json);

@override final  CookingSessionDto session;
@override@JsonKey(name: 'recipe_id') final  String recipeId;
@override@JsonKey(name: 'recipe_name') final  String recipeName;
 final  List<CookingConsumptionDto> _consumptions;
@override@JsonKey() List<CookingConsumptionDto> get consumptions {
  if (_consumptions is EqualUnmodifiableListView) return _consumptions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_consumptions);
}

@override@JsonKey(name: 'leftover_batch_id') final  String? leftoverBatchId;
@override@JsonKey(name: 'completed_at') final  DateTime? completedAt;

/// Create a copy of CookingHistoryDetailDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookingHistoryDetailDtoCopyWith<_CookingHistoryDetailDto> get copyWith => __$CookingHistoryDetailDtoCopyWithImpl<_CookingHistoryDetailDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CookingHistoryDetailDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookingHistoryDetailDto&&(identical(other.session, session) || other.session == session)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&const DeepCollectionEquality().equals(other._consumptions, _consumptions)&&(identical(other.leftoverBatchId, leftoverBatchId) || other.leftoverBatchId == leftoverBatchId)&&(identical(other.completedAt, completedAt) || other.completedAt == completedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,session,recipeId,recipeName,const DeepCollectionEquality().hash(_consumptions),leftoverBatchId,completedAt);

@override
String toString() {
  return 'CookingHistoryDetailDto(session: $session, recipeId: $recipeId, recipeName: $recipeName, consumptions: $consumptions, leftoverBatchId: $leftoverBatchId, completedAt: $completedAt)';
}


}

/// @nodoc
abstract mixin class _$CookingHistoryDetailDtoCopyWith<$Res> implements $CookingHistoryDetailDtoCopyWith<$Res> {
  factory _$CookingHistoryDetailDtoCopyWith(_CookingHistoryDetailDto value, $Res Function(_CookingHistoryDetailDto) _then) = __$CookingHistoryDetailDtoCopyWithImpl;
@override @useResult
$Res call({
 CookingSessionDto session,@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName, List<CookingConsumptionDto> consumptions,@JsonKey(name: 'leftover_batch_id') String? leftoverBatchId,@JsonKey(name: 'completed_at') DateTime? completedAt
});


@override $CookingSessionDtoCopyWith<$Res> get session;

}
/// @nodoc
class __$CookingHistoryDetailDtoCopyWithImpl<$Res>
    implements _$CookingHistoryDetailDtoCopyWith<$Res> {
  __$CookingHistoryDetailDtoCopyWithImpl(this._self, this._then);

  final _CookingHistoryDetailDto _self;
  final $Res Function(_CookingHistoryDetailDto) _then;

/// Create a copy of CookingHistoryDetailDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? session = null,Object? recipeId = null,Object? recipeName = null,Object? consumptions = null,Object? leftoverBatchId = freezed,Object? completedAt = freezed,}) {
  return _then(_CookingHistoryDetailDto(
session: null == session ? _self.session : session // ignore: cast_nullable_to_non_nullable
as CookingSessionDto,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,consumptions: null == consumptions ? _self._consumptions : consumptions // ignore: cast_nullable_to_non_nullable
as List<CookingConsumptionDto>,leftoverBatchId: freezed == leftoverBatchId ? _self.leftoverBatchId : leftoverBatchId // ignore: cast_nullable_to_non_nullable
as String?,completedAt: freezed == completedAt ? _self.completedAt : completedAt // ignore: cast_nullable_to_non_nullable
as DateTime?,
  ));
}

/// Create a copy of CookingHistoryDetailDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$CookingSessionDtoCopyWith<$Res> get session {
  
  return $CookingSessionDtoCopyWith<$Res>(_self.session, (value) {
    return _then(_self.copyWith(session: value));
  });
}
}

// dart format on
