// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'cooking_preview_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ProposedDeductionDto {

@JsonKey(name: 'recipe_ingredient_id') String get recipeIngredientId;@JsonKey(name: 'batch_id') String get batchId; double get quantity; String get unit;@JsonKey(name: 'master_ingredient_id') String? get masterIngredientId;
/// Create a copy of ProposedDeductionDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProposedDeductionDtoCopyWith<ProposedDeductionDto> get copyWith => _$ProposedDeductionDtoCopyWithImpl<ProposedDeductionDto>(this as ProposedDeductionDto, _$identity);

  /// Serializes this ProposedDeductionDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProposedDeductionDto&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.batchId, batchId) || other.batchId == batchId)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,batchId,quantity,unit,masterIngredientId);

@override
String toString() {
  return 'ProposedDeductionDto(recipeIngredientId: $recipeIngredientId, batchId: $batchId, quantity: $quantity, unit: $unit, masterIngredientId: $masterIngredientId)';
}


}

/// @nodoc
abstract mixin class $ProposedDeductionDtoCopyWith<$Res>  {
  factory $ProposedDeductionDtoCopyWith(ProposedDeductionDto value, $Res Function(ProposedDeductionDto) _then) = _$ProposedDeductionDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'recipe_ingredient_id') String recipeIngredientId,@JsonKey(name: 'batch_id') String batchId, double quantity, String unit,@JsonKey(name: 'master_ingredient_id') String? masterIngredientId
});




}
/// @nodoc
class _$ProposedDeductionDtoCopyWithImpl<$Res>
    implements $ProposedDeductionDtoCopyWith<$Res> {
  _$ProposedDeductionDtoCopyWithImpl(this._self, this._then);

  final ProposedDeductionDto _self;
  final $Res Function(ProposedDeductionDto) _then;

/// Create a copy of ProposedDeductionDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeIngredientId = null,Object? batchId = null,Object? quantity = null,Object? unit = null,Object? masterIngredientId = freezed,}) {
  return _then(_self.copyWith(
recipeIngredientId: null == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String,batchId: null == batchId ? _self.batchId : batchId // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ProposedDeductionDto].
extension ProposedDeductionDtoPatterns on ProposedDeductionDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ProposedDeductionDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ProposedDeductionDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ProposedDeductionDto value)  $default,){
final _that = this;
switch (_that) {
case _ProposedDeductionDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ProposedDeductionDto value)?  $default,){
final _that = this;
switch (_that) {
case _ProposedDeductionDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_ingredient_id')  String recipeIngredientId, @JsonKey(name: 'batch_id')  String batchId,  double quantity,  String unit, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ProposedDeductionDto() when $default != null:
return $default(_that.recipeIngredientId,_that.batchId,_that.quantity,_that.unit,_that.masterIngredientId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_ingredient_id')  String recipeIngredientId, @JsonKey(name: 'batch_id')  String batchId,  double quantity,  String unit, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId)  $default,) {final _that = this;
switch (_that) {
case _ProposedDeductionDto():
return $default(_that.recipeIngredientId,_that.batchId,_that.quantity,_that.unit,_that.masterIngredientId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'recipe_ingredient_id')  String recipeIngredientId, @JsonKey(name: 'batch_id')  String batchId,  double quantity,  String unit, @JsonKey(name: 'master_ingredient_id')  String? masterIngredientId)?  $default,) {final _that = this;
switch (_that) {
case _ProposedDeductionDto() when $default != null:
return $default(_that.recipeIngredientId,_that.batchId,_that.quantity,_that.unit,_that.masterIngredientId);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ProposedDeductionDto extends ProposedDeductionDto {
  const _ProposedDeductionDto({@JsonKey(name: 'recipe_ingredient_id') required this.recipeIngredientId, @JsonKey(name: 'batch_id') required this.batchId, required this.quantity, required this.unit, @JsonKey(name: 'master_ingredient_id') this.masterIngredientId}): super._();
  factory _ProposedDeductionDto.fromJson(Map<String, dynamic> json) => _$ProposedDeductionDtoFromJson(json);

@override@JsonKey(name: 'recipe_ingredient_id') final  String recipeIngredientId;
@override@JsonKey(name: 'batch_id') final  String batchId;
@override final  double quantity;
@override final  String unit;
@override@JsonKey(name: 'master_ingredient_id') final  String? masterIngredientId;

/// Create a copy of ProposedDeductionDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProposedDeductionDtoCopyWith<_ProposedDeductionDto> get copyWith => __$ProposedDeductionDtoCopyWithImpl<_ProposedDeductionDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProposedDeductionDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProposedDeductionDto&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.batchId, batchId) || other.batchId == batchId)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,batchId,quantity,unit,masterIngredientId);

@override
String toString() {
  return 'ProposedDeductionDto(recipeIngredientId: $recipeIngredientId, batchId: $batchId, quantity: $quantity, unit: $unit, masterIngredientId: $masterIngredientId)';
}


}

/// @nodoc
abstract mixin class _$ProposedDeductionDtoCopyWith<$Res> implements $ProposedDeductionDtoCopyWith<$Res> {
  factory _$ProposedDeductionDtoCopyWith(_ProposedDeductionDto value, $Res Function(_ProposedDeductionDto) _then) = __$ProposedDeductionDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'recipe_ingredient_id') String recipeIngredientId,@JsonKey(name: 'batch_id') String batchId, double quantity, String unit,@JsonKey(name: 'master_ingredient_id') String? masterIngredientId
});




}
/// @nodoc
class __$ProposedDeductionDtoCopyWithImpl<$Res>
    implements _$ProposedDeductionDtoCopyWith<$Res> {
  __$ProposedDeductionDtoCopyWithImpl(this._self, this._then);

  final _ProposedDeductionDto _self;
  final $Res Function(_ProposedDeductionDto) _then;

/// Create a copy of ProposedDeductionDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeIngredientId = null,Object? batchId = null,Object? quantity = null,Object? unit = null,Object? masterIngredientId = freezed,}) {
  return _then(_ProposedDeductionDto(
recipeIngredientId: null == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String,batchId: null == batchId ? _self.batchId : batchId // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$MissingIngredientPreviewDto {

@JsonKey(name: 'recipe_ingredient_id') String get recipeIngredientId;@JsonKey(name: 'ingredient_name') String get ingredientName;@JsonKey(name: 'missing_quantity') double get missingQuantity; String get unit;
/// Create a copy of MissingIngredientPreviewDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MissingIngredientPreviewDtoCopyWith<MissingIngredientPreviewDto> get copyWith => _$MissingIngredientPreviewDtoCopyWithImpl<MissingIngredientPreviewDto>(this as MissingIngredientPreviewDto, _$identity);

  /// Serializes this MissingIngredientPreviewDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MissingIngredientPreviewDto&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.ingredientName, ingredientName) || other.ingredientName == ingredientName)&&(identical(other.missingQuantity, missingQuantity) || other.missingQuantity == missingQuantity)&&(identical(other.unit, unit) || other.unit == unit));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,ingredientName,missingQuantity,unit);

@override
String toString() {
  return 'MissingIngredientPreviewDto(recipeIngredientId: $recipeIngredientId, ingredientName: $ingredientName, missingQuantity: $missingQuantity, unit: $unit)';
}


}

/// @nodoc
abstract mixin class $MissingIngredientPreviewDtoCopyWith<$Res>  {
  factory $MissingIngredientPreviewDtoCopyWith(MissingIngredientPreviewDto value, $Res Function(MissingIngredientPreviewDto) _then) = _$MissingIngredientPreviewDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'recipe_ingredient_id') String recipeIngredientId,@JsonKey(name: 'ingredient_name') String ingredientName,@JsonKey(name: 'missing_quantity') double missingQuantity, String unit
});




}
/// @nodoc
class _$MissingIngredientPreviewDtoCopyWithImpl<$Res>
    implements $MissingIngredientPreviewDtoCopyWith<$Res> {
  _$MissingIngredientPreviewDtoCopyWithImpl(this._self, this._then);

  final MissingIngredientPreviewDto _self;
  final $Res Function(MissingIngredientPreviewDto) _then;

/// Create a copy of MissingIngredientPreviewDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeIngredientId = null,Object? ingredientName = null,Object? missingQuantity = null,Object? unit = null,}) {
  return _then(_self.copyWith(
recipeIngredientId: null == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String,ingredientName: null == ingredientName ? _self.ingredientName : ingredientName // ignore: cast_nullable_to_non_nullable
as String,missingQuantity: null == missingQuantity ? _self.missingQuantity : missingQuantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [MissingIngredientPreviewDto].
extension MissingIngredientPreviewDtoPatterns on MissingIngredientPreviewDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MissingIngredientPreviewDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MissingIngredientPreviewDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MissingIngredientPreviewDto value)  $default,){
final _that = this;
switch (_that) {
case _MissingIngredientPreviewDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MissingIngredientPreviewDto value)?  $default,){
final _that = this;
switch (_that) {
case _MissingIngredientPreviewDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_ingredient_id')  String recipeIngredientId, @JsonKey(name: 'ingredient_name')  String ingredientName, @JsonKey(name: 'missing_quantity')  double missingQuantity,  String unit)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MissingIngredientPreviewDto() when $default != null:
return $default(_that.recipeIngredientId,_that.ingredientName,_that.missingQuantity,_that.unit);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_ingredient_id')  String recipeIngredientId, @JsonKey(name: 'ingredient_name')  String ingredientName, @JsonKey(name: 'missing_quantity')  double missingQuantity,  String unit)  $default,) {final _that = this;
switch (_that) {
case _MissingIngredientPreviewDto():
return $default(_that.recipeIngredientId,_that.ingredientName,_that.missingQuantity,_that.unit);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'recipe_ingredient_id')  String recipeIngredientId, @JsonKey(name: 'ingredient_name')  String ingredientName, @JsonKey(name: 'missing_quantity')  double missingQuantity,  String unit)?  $default,) {final _that = this;
switch (_that) {
case _MissingIngredientPreviewDto() when $default != null:
return $default(_that.recipeIngredientId,_that.ingredientName,_that.missingQuantity,_that.unit);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MissingIngredientPreviewDto extends MissingIngredientPreviewDto {
  const _MissingIngredientPreviewDto({@JsonKey(name: 'recipe_ingredient_id') required this.recipeIngredientId, @JsonKey(name: 'ingredient_name') required this.ingredientName, @JsonKey(name: 'missing_quantity') required this.missingQuantity, required this.unit}): super._();
  factory _MissingIngredientPreviewDto.fromJson(Map<String, dynamic> json) => _$MissingIngredientPreviewDtoFromJson(json);

@override@JsonKey(name: 'recipe_ingredient_id') final  String recipeIngredientId;
@override@JsonKey(name: 'ingredient_name') final  String ingredientName;
@override@JsonKey(name: 'missing_quantity') final  double missingQuantity;
@override final  String unit;

/// Create a copy of MissingIngredientPreviewDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MissingIngredientPreviewDtoCopyWith<_MissingIngredientPreviewDto> get copyWith => __$MissingIngredientPreviewDtoCopyWithImpl<_MissingIngredientPreviewDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MissingIngredientPreviewDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MissingIngredientPreviewDto&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.ingredientName, ingredientName) || other.ingredientName == ingredientName)&&(identical(other.missingQuantity, missingQuantity) || other.missingQuantity == missingQuantity)&&(identical(other.unit, unit) || other.unit == unit));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,ingredientName,missingQuantity,unit);

@override
String toString() {
  return 'MissingIngredientPreviewDto(recipeIngredientId: $recipeIngredientId, ingredientName: $ingredientName, missingQuantity: $missingQuantity, unit: $unit)';
}


}

/// @nodoc
abstract mixin class _$MissingIngredientPreviewDtoCopyWith<$Res> implements $MissingIngredientPreviewDtoCopyWith<$Res> {
  factory _$MissingIngredientPreviewDtoCopyWith(_MissingIngredientPreviewDto value, $Res Function(_MissingIngredientPreviewDto) _then) = __$MissingIngredientPreviewDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'recipe_ingredient_id') String recipeIngredientId,@JsonKey(name: 'ingredient_name') String ingredientName,@JsonKey(name: 'missing_quantity') double missingQuantity, String unit
});




}
/// @nodoc
class __$MissingIngredientPreviewDtoCopyWithImpl<$Res>
    implements _$MissingIngredientPreviewDtoCopyWith<$Res> {
  __$MissingIngredientPreviewDtoCopyWithImpl(this._self, this._then);

  final _MissingIngredientPreviewDto _self;
  final $Res Function(_MissingIngredientPreviewDto) _then;

/// Create a copy of MissingIngredientPreviewDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeIngredientId = null,Object? ingredientName = null,Object? missingQuantity = null,Object? unit = null,}) {
  return _then(_MissingIngredientPreviewDto(
recipeIngredientId: null == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String,ingredientName: null == ingredientName ? _self.ingredientName : ingredientName // ignore: cast_nullable_to_non_nullable
as String,missingQuantity: null == missingQuantity ? _self.missingQuantity : missingQuantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$CookingPreviewResponseDto {

@JsonKey(name: 'recipe_id') String get recipeId;@JsonKey(name: 'recipe_name') String get recipeName; double get servings;@JsonKey(name: 'proposed_deductions') List<ProposedDeductionDto> get proposedDeductions;@JsonKey(name: 'missing_ingredients') List<MissingIngredientPreviewDto> get missingIngredients;
/// Create a copy of CookingPreviewResponseDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookingPreviewResponseDtoCopyWith<CookingPreviewResponseDto> get copyWith => _$CookingPreviewResponseDtoCopyWithImpl<CookingPreviewResponseDto>(this as CookingPreviewResponseDto, _$identity);

  /// Serializes this CookingPreviewResponseDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookingPreviewResponseDto&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.servings, servings) || other.servings == servings)&&const DeepCollectionEquality().equals(other.proposedDeductions, proposedDeductions)&&const DeepCollectionEquality().equals(other.missingIngredients, missingIngredients));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeId,recipeName,servings,const DeepCollectionEquality().hash(proposedDeductions),const DeepCollectionEquality().hash(missingIngredients));

@override
String toString() {
  return 'CookingPreviewResponseDto(recipeId: $recipeId, recipeName: $recipeName, servings: $servings, proposedDeductions: $proposedDeductions, missingIngredients: $missingIngredients)';
}


}

/// @nodoc
abstract mixin class $CookingPreviewResponseDtoCopyWith<$Res>  {
  factory $CookingPreviewResponseDtoCopyWith(CookingPreviewResponseDto value, $Res Function(CookingPreviewResponseDto) _then) = _$CookingPreviewResponseDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName, double servings,@JsonKey(name: 'proposed_deductions') List<ProposedDeductionDto> proposedDeductions,@JsonKey(name: 'missing_ingredients') List<MissingIngredientPreviewDto> missingIngredients
});




}
/// @nodoc
class _$CookingPreviewResponseDtoCopyWithImpl<$Res>
    implements $CookingPreviewResponseDtoCopyWith<$Res> {
  _$CookingPreviewResponseDtoCopyWithImpl(this._self, this._then);

  final CookingPreviewResponseDto _self;
  final $Res Function(CookingPreviewResponseDto) _then;

/// Create a copy of CookingPreviewResponseDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeId = null,Object? recipeName = null,Object? servings = null,Object? proposedDeductions = null,Object? missingIngredients = null,}) {
  return _then(_self.copyWith(
recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,proposedDeductions: null == proposedDeductions ? _self.proposedDeductions : proposedDeductions // ignore: cast_nullable_to_non_nullable
as List<ProposedDeductionDto>,missingIngredients: null == missingIngredients ? _self.missingIngredients : missingIngredients // ignore: cast_nullable_to_non_nullable
as List<MissingIngredientPreviewDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [CookingPreviewResponseDto].
extension CookingPreviewResponseDtoPatterns on CookingPreviewResponseDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookingPreviewResponseDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookingPreviewResponseDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookingPreviewResponseDto value)  $default,){
final _that = this;
switch (_that) {
case _CookingPreviewResponseDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookingPreviewResponseDto value)?  $default,){
final _that = this;
switch (_that) {
case _CookingPreviewResponseDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName,  double servings, @JsonKey(name: 'proposed_deductions')  List<ProposedDeductionDto> proposedDeductions, @JsonKey(name: 'missing_ingredients')  List<MissingIngredientPreviewDto> missingIngredients)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookingPreviewResponseDto() when $default != null:
return $default(_that.recipeId,_that.recipeName,_that.servings,_that.proposedDeductions,_that.missingIngredients);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName,  double servings, @JsonKey(name: 'proposed_deductions')  List<ProposedDeductionDto> proposedDeductions, @JsonKey(name: 'missing_ingredients')  List<MissingIngredientPreviewDto> missingIngredients)  $default,) {final _that = this;
switch (_that) {
case _CookingPreviewResponseDto():
return $default(_that.recipeId,_that.recipeName,_that.servings,_that.proposedDeductions,_that.missingIngredients);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName,  double servings, @JsonKey(name: 'proposed_deductions')  List<ProposedDeductionDto> proposedDeductions, @JsonKey(name: 'missing_ingredients')  List<MissingIngredientPreviewDto> missingIngredients)?  $default,) {final _that = this;
switch (_that) {
case _CookingPreviewResponseDto() when $default != null:
return $default(_that.recipeId,_that.recipeName,_that.servings,_that.proposedDeductions,_that.missingIngredients);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _CookingPreviewResponseDto extends CookingPreviewResponseDto {
  const _CookingPreviewResponseDto({@JsonKey(name: 'recipe_id') required this.recipeId, @JsonKey(name: 'recipe_name') required this.recipeName, required this.servings, @JsonKey(name: 'proposed_deductions') final  List<ProposedDeductionDto> proposedDeductions = const <ProposedDeductionDto>[], @JsonKey(name: 'missing_ingredients') final  List<MissingIngredientPreviewDto> missingIngredients = const <MissingIngredientPreviewDto>[]}): _proposedDeductions = proposedDeductions,_missingIngredients = missingIngredients,super._();
  factory _CookingPreviewResponseDto.fromJson(Map<String, dynamic> json) => _$CookingPreviewResponseDtoFromJson(json);

@override@JsonKey(name: 'recipe_id') final  String recipeId;
@override@JsonKey(name: 'recipe_name') final  String recipeName;
@override final  double servings;
 final  List<ProposedDeductionDto> _proposedDeductions;
@override@JsonKey(name: 'proposed_deductions') List<ProposedDeductionDto> get proposedDeductions {
  if (_proposedDeductions is EqualUnmodifiableListView) return _proposedDeductions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_proposedDeductions);
}

 final  List<MissingIngredientPreviewDto> _missingIngredients;
@override@JsonKey(name: 'missing_ingredients') List<MissingIngredientPreviewDto> get missingIngredients {
  if (_missingIngredients is EqualUnmodifiableListView) return _missingIngredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_missingIngredients);
}


/// Create a copy of CookingPreviewResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookingPreviewResponseDtoCopyWith<_CookingPreviewResponseDto> get copyWith => __$CookingPreviewResponseDtoCopyWithImpl<_CookingPreviewResponseDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$CookingPreviewResponseDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookingPreviewResponseDto&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.servings, servings) || other.servings == servings)&&const DeepCollectionEquality().equals(other._proposedDeductions, _proposedDeductions)&&const DeepCollectionEquality().equals(other._missingIngredients, _missingIngredients));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeId,recipeName,servings,const DeepCollectionEquality().hash(_proposedDeductions),const DeepCollectionEquality().hash(_missingIngredients));

@override
String toString() {
  return 'CookingPreviewResponseDto(recipeId: $recipeId, recipeName: $recipeName, servings: $servings, proposedDeductions: $proposedDeductions, missingIngredients: $missingIngredients)';
}


}

/// @nodoc
abstract mixin class _$CookingPreviewResponseDtoCopyWith<$Res> implements $CookingPreviewResponseDtoCopyWith<$Res> {
  factory _$CookingPreviewResponseDtoCopyWith(_CookingPreviewResponseDto value, $Res Function(_CookingPreviewResponseDto) _then) = __$CookingPreviewResponseDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName, double servings,@JsonKey(name: 'proposed_deductions') List<ProposedDeductionDto> proposedDeductions,@JsonKey(name: 'missing_ingredients') List<MissingIngredientPreviewDto> missingIngredients
});




}
/// @nodoc
class __$CookingPreviewResponseDtoCopyWithImpl<$Res>
    implements _$CookingPreviewResponseDtoCopyWith<$Res> {
  __$CookingPreviewResponseDtoCopyWithImpl(this._self, this._then);

  final _CookingPreviewResponseDto _self;
  final $Res Function(_CookingPreviewResponseDto) _then;

/// Create a copy of CookingPreviewResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeId = null,Object? recipeName = null,Object? servings = null,Object? proposedDeductions = null,Object? missingIngredients = null,}) {
  return _then(_CookingPreviewResponseDto(
recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,proposedDeductions: null == proposedDeductions ? _self._proposedDeductions : proposedDeductions // ignore: cast_nullable_to_non_nullable
as List<ProposedDeductionDto>,missingIngredients: null == missingIngredients ? _self._missingIngredients : missingIngredients // ignore: cast_nullable_to_non_nullable
as List<MissingIngredientPreviewDto>,
  ));
}


}

// dart format on
