// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'parsed_item_draft.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ParsedItemDraft {

 String get name; String get category; double get quantity; MeasurementUnit get unit; StorageTier get storageTier; DateTime? get packedDate; DateTime? get expiryDate; int? get priceVnd; bool get isExpiryWarn; String? get imagePath;
/// Create a copy of ParsedItemDraft
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParsedItemDraftCopyWith<ParsedItemDraft> get copyWith => _$ParsedItemDraftCopyWithImpl<ParsedItemDraft>(this as ParsedItemDraft, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParsedItemDraft&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageTier, storageTier) || other.storageTier == storageTier)&&(identical(other.packedDate, packedDate) || other.packedDate == packedDate)&&(identical(other.expiryDate, expiryDate) || other.expiryDate == expiryDate)&&(identical(other.priceVnd, priceVnd) || other.priceVnd == priceVnd)&&(identical(other.isExpiryWarn, isExpiryWarn) || other.isExpiryWarn == isExpiryWarn)&&(identical(other.imagePath, imagePath) || other.imagePath == imagePath));
}


@override
int get hashCode => Object.hash(runtimeType,name,category,quantity,unit,storageTier,packedDate,expiryDate,priceVnd,isExpiryWarn,imagePath);

@override
String toString() {
  return 'ParsedItemDraft(name: $name, category: $category, quantity: $quantity, unit: $unit, storageTier: $storageTier, packedDate: $packedDate, expiryDate: $expiryDate, priceVnd: $priceVnd, isExpiryWarn: $isExpiryWarn, imagePath: $imagePath)';
}


}

/// @nodoc
abstract mixin class $ParsedItemDraftCopyWith<$Res>  {
  factory $ParsedItemDraftCopyWith(ParsedItemDraft value, $Res Function(ParsedItemDraft) _then) = _$ParsedItemDraftCopyWithImpl;
@useResult
$Res call({
 String name, String category, double quantity, MeasurementUnit unit, StorageTier storageTier, DateTime? packedDate, DateTime? expiryDate, int? priceVnd, bool isExpiryWarn, String? imagePath
});




}
/// @nodoc
class _$ParsedItemDraftCopyWithImpl<$Res>
    implements $ParsedItemDraftCopyWith<$Res> {
  _$ParsedItemDraftCopyWithImpl(this._self, this._then);

  final ParsedItemDraft _self;
  final $Res Function(ParsedItemDraft) _then;

/// Create a copy of ParsedItemDraft
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? category = null,Object? quantity = null,Object? unit = null,Object? storageTier = null,Object? packedDate = freezed,Object? expiryDate = freezed,Object? priceVnd = freezed,Object? isExpiryWarn = null,Object? imagePath = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,storageTier: null == storageTier ? _self.storageTier : storageTier // ignore: cast_nullable_to_non_nullable
as StorageTier,packedDate: freezed == packedDate ? _self.packedDate : packedDate // ignore: cast_nullable_to_non_nullable
as DateTime?,expiryDate: freezed == expiryDate ? _self.expiryDate : expiryDate // ignore: cast_nullable_to_non_nullable
as DateTime?,priceVnd: freezed == priceVnd ? _self.priceVnd : priceVnd // ignore: cast_nullable_to_non_nullable
as int?,isExpiryWarn: null == isExpiryWarn ? _self.isExpiryWarn : isExpiryWarn // ignore: cast_nullable_to_non_nullable
as bool,imagePath: freezed == imagePath ? _self.imagePath : imagePath // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ParsedItemDraft].
extension ParsedItemDraftPatterns on ParsedItemDraft {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ParsedItemDraft value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ParsedItemDraft() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ParsedItemDraft value)  $default,){
final _that = this;
switch (_that) {
case _ParsedItemDraft():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ParsedItemDraft value)?  $default,){
final _that = this;
switch (_that) {
case _ParsedItemDraft() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String name,  String category,  double quantity,  MeasurementUnit unit,  StorageTier storageTier,  DateTime? packedDate,  DateTime? expiryDate,  int? priceVnd,  bool isExpiryWarn,  String? imagePath)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ParsedItemDraft() when $default != null:
return $default(_that.name,_that.category,_that.quantity,_that.unit,_that.storageTier,_that.packedDate,_that.expiryDate,_that.priceVnd,_that.isExpiryWarn,_that.imagePath);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String name,  String category,  double quantity,  MeasurementUnit unit,  StorageTier storageTier,  DateTime? packedDate,  DateTime? expiryDate,  int? priceVnd,  bool isExpiryWarn,  String? imagePath)  $default,) {final _that = this;
switch (_that) {
case _ParsedItemDraft():
return $default(_that.name,_that.category,_that.quantity,_that.unit,_that.storageTier,_that.packedDate,_that.expiryDate,_that.priceVnd,_that.isExpiryWarn,_that.imagePath);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String name,  String category,  double quantity,  MeasurementUnit unit,  StorageTier storageTier,  DateTime? packedDate,  DateTime? expiryDate,  int? priceVnd,  bool isExpiryWarn,  String? imagePath)?  $default,) {final _that = this;
switch (_that) {
case _ParsedItemDraft() when $default != null:
return $default(_that.name,_that.category,_that.quantity,_that.unit,_that.storageTier,_that.packedDate,_that.expiryDate,_that.priceVnd,_that.isExpiryWarn,_that.imagePath);case _:
  return null;

}
}

}

/// @nodoc


class _ParsedItemDraft extends ParsedItemDraft {
  const _ParsedItemDraft({this.name = 'Cà chua bi', this.category = 'Rau củ', this.quantity = 500, this.unit = MeasurementUnit.gram, this.storageTier = StorageTier.fridge, this.packedDate, this.expiryDate, this.priceVnd, this.isExpiryWarn = false, this.imagePath}): super._();
  

@override@JsonKey() final  String name;
@override@JsonKey() final  String category;
@override@JsonKey() final  double quantity;
@override@JsonKey() final  MeasurementUnit unit;
@override@JsonKey() final  StorageTier storageTier;
@override final  DateTime? packedDate;
@override final  DateTime? expiryDate;
@override final  int? priceVnd;
@override@JsonKey() final  bool isExpiryWarn;
@override final  String? imagePath;

/// Create a copy of ParsedItemDraft
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ParsedItemDraftCopyWith<_ParsedItemDraft> get copyWith => __$ParsedItemDraftCopyWithImpl<_ParsedItemDraft>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ParsedItemDraft&&(identical(other.name, name) || other.name == name)&&(identical(other.category, category) || other.category == category)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.storageTier, storageTier) || other.storageTier == storageTier)&&(identical(other.packedDate, packedDate) || other.packedDate == packedDate)&&(identical(other.expiryDate, expiryDate) || other.expiryDate == expiryDate)&&(identical(other.priceVnd, priceVnd) || other.priceVnd == priceVnd)&&(identical(other.isExpiryWarn, isExpiryWarn) || other.isExpiryWarn == isExpiryWarn)&&(identical(other.imagePath, imagePath) || other.imagePath == imagePath));
}


@override
int get hashCode => Object.hash(runtimeType,name,category,quantity,unit,storageTier,packedDate,expiryDate,priceVnd,isExpiryWarn,imagePath);

@override
String toString() {
  return 'ParsedItemDraft(name: $name, category: $category, quantity: $quantity, unit: $unit, storageTier: $storageTier, packedDate: $packedDate, expiryDate: $expiryDate, priceVnd: $priceVnd, isExpiryWarn: $isExpiryWarn, imagePath: $imagePath)';
}


}

/// @nodoc
abstract mixin class _$ParsedItemDraftCopyWith<$Res> implements $ParsedItemDraftCopyWith<$Res> {
  factory _$ParsedItemDraftCopyWith(_ParsedItemDraft value, $Res Function(_ParsedItemDraft) _then) = __$ParsedItemDraftCopyWithImpl;
@override @useResult
$Res call({
 String name, String category, double quantity, MeasurementUnit unit, StorageTier storageTier, DateTime? packedDate, DateTime? expiryDate, int? priceVnd, bool isExpiryWarn, String? imagePath
});




}
/// @nodoc
class __$ParsedItemDraftCopyWithImpl<$Res>
    implements _$ParsedItemDraftCopyWith<$Res> {
  __$ParsedItemDraftCopyWithImpl(this._self, this._then);

  final _ParsedItemDraft _self;
  final $Res Function(_ParsedItemDraft) _then;

/// Create a copy of ParsedItemDraft
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? category = null,Object? quantity = null,Object? unit = null,Object? storageTier = null,Object? packedDate = freezed,Object? expiryDate = freezed,Object? priceVnd = freezed,Object? isExpiryWarn = null,Object? imagePath = freezed,}) {
  return _then(_ParsedItemDraft(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as MeasurementUnit,storageTier: null == storageTier ? _self.storageTier : storageTier // ignore: cast_nullable_to_non_nullable
as StorageTier,packedDate: freezed == packedDate ? _self.packedDate : packedDate // ignore: cast_nullable_to_non_nullable
as DateTime?,expiryDate: freezed == expiryDate ? _self.expiryDate : expiryDate // ignore: cast_nullable_to_non_nullable
as DateTime?,priceVnd: freezed == priceVnd ? _self.priceVnd : priceVnd // ignore: cast_nullable_to_non_nullable
as int?,isExpiryWarn: null == isExpiryWarn ? _self.isExpiryWarn : isExpiryWarn // ignore: cast_nullable_to_non_nullable
as bool,imagePath: freezed == imagePath ? _self.imagePath : imagePath // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
