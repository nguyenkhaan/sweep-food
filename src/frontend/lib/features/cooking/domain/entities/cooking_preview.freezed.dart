// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'cooking_preview.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ProposedDeduction {

 String get recipeIngredientId; String get batchId; double get quantity; MeasurementUnit get unit; String? get masterIngredientId;
/// Create a copy of ProposedDeduction
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProposedDeductionCopyWith<ProposedDeduction> get copyWith => _$ProposedDeductionCopyWithImpl<ProposedDeduction>(this as ProposedDeduction, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProposedDeduction&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.batchId, batchId) || other.batchId == batchId)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId));
}


@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,batchId,quantity,unit,masterIngredientId);

@override
String toString() {
  return 'ProposedDeduction(recipeIngredientId: $recipeIngredientId, batchId: $batchId, quantity: $quantity, unit: $unit, masterIngredientId: $masterIngredientId)';
}


}

/// @nodoc
abstract mixin class $ProposedDeductionCopyWith<$Res>  {
  factory $ProposedDeductionCopyWith(ProposedDeduction value, $Res Function(ProposedDeduction) _then) = _$ProposedDeductionCopyWithImpl;
@useResult
$Res call({
 String recipeIngredientId, String batchId, double quantity, MeasurementUnit unit, String? masterIngredientId
});




}
/// @nodoc
class _$ProposedDeductionCopyWithImpl<$Res>
    implements $ProposedDeductionCopyWith<$Res> {
  _$ProposedDeductionCopyWithImpl(this._self, this._then);

  final ProposedDeduction _self;
  final $Res Function(ProposedDeduction) _then;

/// Create a copy of ProposedDeduction
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeIngredientId = null,Object? batchId = null,Object? quantity = null,Object? unit = null,Object? masterIngredientId = freezed,}) {
  return _then(_self.copyWith(
recipeIngredientId: null == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String,batchId: null == batchId ? _self.batchId : batchId // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ProposedDeduction].
extension ProposedDeductionPatterns on ProposedDeduction {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ProposedDeduction value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ProposedDeduction() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ProposedDeduction value)  $default,){
final _that = this;
switch (_that) {
case _ProposedDeduction():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ProposedDeduction value)?  $default,){
final _that = this;
switch (_that) {
case _ProposedDeduction() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String recipeIngredientId,  String batchId,  double quantity,  MeasurementUnit unit,  String? masterIngredientId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ProposedDeduction() when $default != null:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String recipeIngredientId,  String batchId,  double quantity,  MeasurementUnit unit,  String? masterIngredientId)  $default,) {final _that = this;
switch (_that) {
case _ProposedDeduction():
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String recipeIngredientId,  String batchId,  double quantity,  MeasurementUnit unit,  String? masterIngredientId)?  $default,) {final _that = this;
switch (_that) {
case _ProposedDeduction() when $default != null:
return $default(_that.recipeIngredientId,_that.batchId,_that.quantity,_that.unit,_that.masterIngredientId);case _:
  return null;

}
}

}

/// @nodoc


class _ProposedDeduction implements ProposedDeduction {
  const _ProposedDeduction({required this.recipeIngredientId, required this.batchId, required this.quantity, required this.unit, this.masterIngredientId});
  

@override final  String recipeIngredientId;
@override final  String batchId;
@override final  double quantity;
@override final  MeasurementUnit unit;
@override final  String? masterIngredientId;

/// Create a copy of ProposedDeduction
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProposedDeductionCopyWith<_ProposedDeduction> get copyWith => __$ProposedDeductionCopyWithImpl<_ProposedDeduction>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProposedDeduction&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.batchId, batchId) || other.batchId == batchId)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId));
}


@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,batchId,quantity,unit,masterIngredientId);

@override
String toString() {
  return 'ProposedDeduction(recipeIngredientId: $recipeIngredientId, batchId: $batchId, quantity: $quantity, unit: $unit, masterIngredientId: $masterIngredientId)';
}


}

/// @nodoc
abstract mixin class _$ProposedDeductionCopyWith<$Res> implements $ProposedDeductionCopyWith<$Res> {
  factory _$ProposedDeductionCopyWith(_ProposedDeduction value, $Res Function(_ProposedDeduction) _then) = __$ProposedDeductionCopyWithImpl;
@override @useResult
$Res call({
 String recipeIngredientId, String batchId, double quantity, MeasurementUnit unit, String? masterIngredientId
});




}
/// @nodoc
class __$ProposedDeductionCopyWithImpl<$Res>
    implements _$ProposedDeductionCopyWith<$Res> {
  __$ProposedDeductionCopyWithImpl(this._self, this._then);

  final _ProposedDeduction _self;
  final $Res Function(_ProposedDeduction) _then;

/// Create a copy of ProposedDeduction
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeIngredientId = null,Object? batchId = null,Object? quantity = null,Object? unit = null,Object? masterIngredientId = freezed,}) {
  return _then(_ProposedDeduction(
recipeIngredientId: null == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String,batchId: null == batchId ? _self.batchId : batchId // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

/// @nodoc
mixin _$MissingIngredientPreview {

 String get recipeIngredientId; String get ingredientName; double get missingQuantity; MeasurementUnit get unit;
/// Create a copy of MissingIngredientPreview
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MissingIngredientPreviewCopyWith<MissingIngredientPreview> get copyWith => _$MissingIngredientPreviewCopyWithImpl<MissingIngredientPreview>(this as MissingIngredientPreview, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MissingIngredientPreview&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.ingredientName, ingredientName) || other.ingredientName == ingredientName)&&(identical(other.missingQuantity, missingQuantity) || other.missingQuantity == missingQuantity)&&(identical(other.unit, unit) || other.unit == unit));
}


@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,ingredientName,missingQuantity,unit);

@override
String toString() {
  return 'MissingIngredientPreview(recipeIngredientId: $recipeIngredientId, ingredientName: $ingredientName, missingQuantity: $missingQuantity, unit: $unit)';
}


}

/// @nodoc
abstract mixin class $MissingIngredientPreviewCopyWith<$Res>  {
  factory $MissingIngredientPreviewCopyWith(MissingIngredientPreview value, $Res Function(MissingIngredientPreview) _then) = _$MissingIngredientPreviewCopyWithImpl;
@useResult
$Res call({
 String recipeIngredientId, String ingredientName, double missingQuantity, MeasurementUnit unit
});




}
/// @nodoc
class _$MissingIngredientPreviewCopyWithImpl<$Res>
    implements $MissingIngredientPreviewCopyWith<$Res> {
  _$MissingIngredientPreviewCopyWithImpl(this._self, this._then);

  final MissingIngredientPreview _self;
  final $Res Function(MissingIngredientPreview) _then;

/// Create a copy of MissingIngredientPreview
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeIngredientId = null,Object? ingredientName = null,Object? missingQuantity = null,Object? unit = null,}) {
  return _then(_self.copyWith(
recipeIngredientId: null == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String,ingredientName: null == ingredientName ? _self.ingredientName : ingredientName // ignore: cast_nullable_to_non_nullable
as String,missingQuantity: null == missingQuantity ? _self.missingQuantity : missingQuantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,
  ));
}

}


/// Adds pattern-matching-related methods to [MissingIngredientPreview].
extension MissingIngredientPreviewPatterns on MissingIngredientPreview {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MissingIngredientPreview value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MissingIngredientPreview() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MissingIngredientPreview value)  $default,){
final _that = this;
switch (_that) {
case _MissingIngredientPreview():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MissingIngredientPreview value)?  $default,){
final _that = this;
switch (_that) {
case _MissingIngredientPreview() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String recipeIngredientId,  String ingredientName,  double missingQuantity,  MeasurementUnit unit)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MissingIngredientPreview() when $default != null:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String recipeIngredientId,  String ingredientName,  double missingQuantity,  MeasurementUnit unit)  $default,) {final _that = this;
switch (_that) {
case _MissingIngredientPreview():
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String recipeIngredientId,  String ingredientName,  double missingQuantity,  MeasurementUnit unit)?  $default,) {final _that = this;
switch (_that) {
case _MissingIngredientPreview() when $default != null:
return $default(_that.recipeIngredientId,_that.ingredientName,_that.missingQuantity,_that.unit);case _:
  return null;

}
}

}

/// @nodoc


class _MissingIngredientPreview implements MissingIngredientPreview {
  const _MissingIngredientPreview({required this.recipeIngredientId, required this.ingredientName, required this.missingQuantity, required this.unit});
  

@override final  String recipeIngredientId;
@override final  String ingredientName;
@override final  double missingQuantity;
@override final  MeasurementUnit unit;

/// Create a copy of MissingIngredientPreview
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MissingIngredientPreviewCopyWith<_MissingIngredientPreview> get copyWith => __$MissingIngredientPreviewCopyWithImpl<_MissingIngredientPreview>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MissingIngredientPreview&&(identical(other.recipeIngredientId, recipeIngredientId) || other.recipeIngredientId == recipeIngredientId)&&(identical(other.ingredientName, ingredientName) || other.ingredientName == ingredientName)&&(identical(other.missingQuantity, missingQuantity) || other.missingQuantity == missingQuantity)&&(identical(other.unit, unit) || other.unit == unit));
}


@override
int get hashCode => Object.hash(runtimeType,recipeIngredientId,ingredientName,missingQuantity,unit);

@override
String toString() {
  return 'MissingIngredientPreview(recipeIngredientId: $recipeIngredientId, ingredientName: $ingredientName, missingQuantity: $missingQuantity, unit: $unit)';
}


}

/// @nodoc
abstract mixin class _$MissingIngredientPreviewCopyWith<$Res> implements $MissingIngredientPreviewCopyWith<$Res> {
  factory _$MissingIngredientPreviewCopyWith(_MissingIngredientPreview value, $Res Function(_MissingIngredientPreview) _then) = __$MissingIngredientPreviewCopyWithImpl;
@override @useResult
$Res call({
 String recipeIngredientId, String ingredientName, double missingQuantity, MeasurementUnit unit
});




}
/// @nodoc
class __$MissingIngredientPreviewCopyWithImpl<$Res>
    implements _$MissingIngredientPreviewCopyWith<$Res> {
  __$MissingIngredientPreviewCopyWithImpl(this._self, this._then);

  final _MissingIngredientPreview _self;
  final $Res Function(_MissingIngredientPreview) _then;

/// Create a copy of MissingIngredientPreview
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeIngredientId = null,Object? ingredientName = null,Object? missingQuantity = null,Object? unit = null,}) {
  return _then(_MissingIngredientPreview(
recipeIngredientId: null == recipeIngredientId ? _self.recipeIngredientId : recipeIngredientId // ignore: cast_nullable_to_non_nullable
as String,ingredientName: null == ingredientName ? _self.ingredientName : ingredientName // ignore: cast_nullable_to_non_nullable
as String,missingQuantity: null == missingQuantity ? _self.missingQuantity : missingQuantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,
  ));
}


}

/// @nodoc
mixin _$CookingPreview {

 String get mealPlanItemId; String get recipeId; String get recipeName; double get servings; List<ProposedDeduction> get proposedDeductions; List<MissingIngredientPreview> get missingIngredients;
/// Create a copy of CookingPreview
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$CookingPreviewCopyWith<CookingPreview> get copyWith => _$CookingPreviewCopyWithImpl<CookingPreview>(this as CookingPreview, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is CookingPreview&&(identical(other.mealPlanItemId, mealPlanItemId) || other.mealPlanItemId == mealPlanItemId)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.servings, servings) || other.servings == servings)&&const DeepCollectionEquality().equals(other.proposedDeductions, proposedDeductions)&&const DeepCollectionEquality().equals(other.missingIngredients, missingIngredients));
}


@override
int get hashCode => Object.hash(runtimeType,mealPlanItemId,recipeId,recipeName,servings,const DeepCollectionEquality().hash(proposedDeductions),const DeepCollectionEquality().hash(missingIngredients));

@override
String toString() {
  return 'CookingPreview(mealPlanItemId: $mealPlanItemId, recipeId: $recipeId, recipeName: $recipeName, servings: $servings, proposedDeductions: $proposedDeductions, missingIngredients: $missingIngredients)';
}


}

/// @nodoc
abstract mixin class $CookingPreviewCopyWith<$Res>  {
  factory $CookingPreviewCopyWith(CookingPreview value, $Res Function(CookingPreview) _then) = _$CookingPreviewCopyWithImpl;
@useResult
$Res call({
 String mealPlanItemId, String recipeId, String recipeName, double servings, List<ProposedDeduction> proposedDeductions, List<MissingIngredientPreview> missingIngredients
});




}
/// @nodoc
class _$CookingPreviewCopyWithImpl<$Res>
    implements $CookingPreviewCopyWith<$Res> {
  _$CookingPreviewCopyWithImpl(this._self, this._then);

  final CookingPreview _self;
  final $Res Function(CookingPreview) _then;

/// Create a copy of CookingPreview
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? mealPlanItemId = null,Object? recipeId = null,Object? recipeName = null,Object? servings = null,Object? proposedDeductions = null,Object? missingIngredients = null,}) {
  return _then(_self.copyWith(
mealPlanItemId: null == mealPlanItemId ? _self.mealPlanItemId : mealPlanItemId // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,proposedDeductions: null == proposedDeductions ? _self.proposedDeductions : proposedDeductions // ignore: cast_nullable_to_non_nullable
as List<ProposedDeduction>,missingIngredients: null == missingIngredients ? _self.missingIngredients : missingIngredients // ignore: cast_nullable_to_non_nullable
as List<MissingIngredientPreview>,
  ));
}

}


/// Adds pattern-matching-related methods to [CookingPreview].
extension CookingPreviewPatterns on CookingPreview {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _CookingPreview value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _CookingPreview() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _CookingPreview value)  $default,){
final _that = this;
switch (_that) {
case _CookingPreview():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _CookingPreview value)?  $default,){
final _that = this;
switch (_that) {
case _CookingPreview() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String mealPlanItemId,  String recipeId,  String recipeName,  double servings,  List<ProposedDeduction> proposedDeductions,  List<MissingIngredientPreview> missingIngredients)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _CookingPreview() when $default != null:
return $default(_that.mealPlanItemId,_that.recipeId,_that.recipeName,_that.servings,_that.proposedDeductions,_that.missingIngredients);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String mealPlanItemId,  String recipeId,  String recipeName,  double servings,  List<ProposedDeduction> proposedDeductions,  List<MissingIngredientPreview> missingIngredients)  $default,) {final _that = this;
switch (_that) {
case _CookingPreview():
return $default(_that.mealPlanItemId,_that.recipeId,_that.recipeName,_that.servings,_that.proposedDeductions,_that.missingIngredients);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String mealPlanItemId,  String recipeId,  String recipeName,  double servings,  List<ProposedDeduction> proposedDeductions,  List<MissingIngredientPreview> missingIngredients)?  $default,) {final _that = this;
switch (_that) {
case _CookingPreview() when $default != null:
return $default(_that.mealPlanItemId,_that.recipeId,_that.recipeName,_that.servings,_that.proposedDeductions,_that.missingIngredients);case _:
  return null;

}
}

}

/// @nodoc


class _CookingPreview extends CookingPreview {
  const _CookingPreview({required this.mealPlanItemId, required this.recipeId, required this.recipeName, required this.servings, final  List<ProposedDeduction> proposedDeductions = const <ProposedDeduction>[], final  List<MissingIngredientPreview> missingIngredients = const <MissingIngredientPreview>[]}): _proposedDeductions = proposedDeductions,_missingIngredients = missingIngredients,super._();
  

@override final  String mealPlanItemId;
@override final  String recipeId;
@override final  String recipeName;
@override final  double servings;
 final  List<ProposedDeduction> _proposedDeductions;
@override@JsonKey() List<ProposedDeduction> get proposedDeductions {
  if (_proposedDeductions is EqualUnmodifiableListView) return _proposedDeductions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_proposedDeductions);
}

 final  List<MissingIngredientPreview> _missingIngredients;
@override@JsonKey() List<MissingIngredientPreview> get missingIngredients {
  if (_missingIngredients is EqualUnmodifiableListView) return _missingIngredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_missingIngredients);
}


/// Create a copy of CookingPreview
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$CookingPreviewCopyWith<_CookingPreview> get copyWith => __$CookingPreviewCopyWithImpl<_CookingPreview>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _CookingPreview&&(identical(other.mealPlanItemId, mealPlanItemId) || other.mealPlanItemId == mealPlanItemId)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.servings, servings) || other.servings == servings)&&const DeepCollectionEquality().equals(other._proposedDeductions, _proposedDeductions)&&const DeepCollectionEquality().equals(other._missingIngredients, _missingIngredients));
}


@override
int get hashCode => Object.hash(runtimeType,mealPlanItemId,recipeId,recipeName,servings,const DeepCollectionEquality().hash(_proposedDeductions),const DeepCollectionEquality().hash(_missingIngredients));

@override
String toString() {
  return 'CookingPreview(mealPlanItemId: $mealPlanItemId, recipeId: $recipeId, recipeName: $recipeName, servings: $servings, proposedDeductions: $proposedDeductions, missingIngredients: $missingIngredients)';
}


}

/// @nodoc
abstract mixin class _$CookingPreviewCopyWith<$Res> implements $CookingPreviewCopyWith<$Res> {
  factory _$CookingPreviewCopyWith(_CookingPreview value, $Res Function(_CookingPreview) _then) = __$CookingPreviewCopyWithImpl;
@override @useResult
$Res call({
 String mealPlanItemId, String recipeId, String recipeName, double servings, List<ProposedDeduction> proposedDeductions, List<MissingIngredientPreview> missingIngredients
});




}
/// @nodoc
class __$CookingPreviewCopyWithImpl<$Res>
    implements _$CookingPreviewCopyWith<$Res> {
  __$CookingPreviewCopyWithImpl(this._self, this._then);

  final _CookingPreview _self;
  final $Res Function(_CookingPreview) _then;

/// Create a copy of CookingPreview
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? mealPlanItemId = null,Object? recipeId = null,Object? recipeName = null,Object? servings = null,Object? proposedDeductions = null,Object? missingIngredients = null,}) {
  return _then(_CookingPreview(
mealPlanItemId: null == mealPlanItemId ? _self.mealPlanItemId : mealPlanItemId // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,proposedDeductions: null == proposedDeductions ? _self._proposedDeductions : proposedDeductions // ignore: cast_nullable_to_non_nullable
as List<ProposedDeduction>,missingIngredients: null == missingIngredients ? _self._missingIngredients : missingIngredients // ignore: cast_nullable_to_non_nullable
as List<MissingIngredientPreview>,
  ));
}


}

// dart format on
