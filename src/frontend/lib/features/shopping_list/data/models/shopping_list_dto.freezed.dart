// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'shopping_list_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ShoppingListItemDto {

 String get id; String get name; double get quantity; String get unit; String get category;@JsonKey(name: 'checked') bool get isChecked;@JsonKey(name: 'already_in_pantry') bool get alreadyInPantry;@JsonKey(name: 'from_dish_ids') List<String> get fromDishIds;@JsonKey(name: 'est_price_vnd') int? get estPriceVnd;
/// Create a copy of ShoppingListItemDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ShoppingListItemDtoCopyWith<ShoppingListItemDto> get copyWith => _$ShoppingListItemDtoCopyWithImpl<ShoppingListItemDto>(this as ShoppingListItemDto, _$identity);

  /// Serializes this ShoppingListItemDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ShoppingListItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.category, category) || other.category == category)&&(identical(other.isChecked, isChecked) || other.isChecked == isChecked)&&(identical(other.alreadyInPantry, alreadyInPantry) || other.alreadyInPantry == alreadyInPantry)&&const DeepCollectionEquality().equals(other.fromDishIds, fromDishIds)&&(identical(other.estPriceVnd, estPriceVnd) || other.estPriceVnd == estPriceVnd));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,quantity,unit,category,isChecked,alreadyInPantry,const DeepCollectionEquality().hash(fromDishIds),estPriceVnd);

@override
String toString() {
  return 'ShoppingListItemDto(id: $id, name: $name, quantity: $quantity, unit: $unit, category: $category, isChecked: $isChecked, alreadyInPantry: $alreadyInPantry, fromDishIds: $fromDishIds, estPriceVnd: $estPriceVnd)';
}


}

/// @nodoc
abstract mixin class $ShoppingListItemDtoCopyWith<$Res>  {
  factory $ShoppingListItemDtoCopyWith(ShoppingListItemDto value, $Res Function(ShoppingListItemDto) _then) = _$ShoppingListItemDtoCopyWithImpl;
@useResult
$Res call({
 String id, String name, double quantity, String unit, String category,@JsonKey(name: 'checked') bool isChecked,@JsonKey(name: 'already_in_pantry') bool alreadyInPantry,@JsonKey(name: 'from_dish_ids') List<String> fromDishIds,@JsonKey(name: 'est_price_vnd') int? estPriceVnd
});




}
/// @nodoc
class _$ShoppingListItemDtoCopyWithImpl<$Res>
    implements $ShoppingListItemDtoCopyWith<$Res> {
  _$ShoppingListItemDtoCopyWithImpl(this._self, this._then);

  final ShoppingListItemDto _self;
  final $Res Function(ShoppingListItemDto) _then;

/// Create a copy of ShoppingListItemDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? quantity = null,Object? unit = null,Object? category = null,Object? isChecked = null,Object? alreadyInPantry = null,Object? fromDishIds = null,Object? estPriceVnd = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,isChecked: null == isChecked ? _self.isChecked : isChecked // ignore: cast_nullable_to_non_nullable
as bool,alreadyInPantry: null == alreadyInPantry ? _self.alreadyInPantry : alreadyInPantry // ignore: cast_nullable_to_non_nullable
as bool,fromDishIds: null == fromDishIds ? _self.fromDishIds : fromDishIds // ignore: cast_nullable_to_non_nullable
as List<String>,estPriceVnd: freezed == estPriceVnd ? _self.estPriceVnd : estPriceVnd // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [ShoppingListItemDto].
extension ShoppingListItemDtoPatterns on ShoppingListItemDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ShoppingListItemDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ShoppingListItemDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ShoppingListItemDto value)  $default,){
final _that = this;
switch (_that) {
case _ShoppingListItemDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ShoppingListItemDto value)?  $default,){
final _that = this;
switch (_that) {
case _ShoppingListItemDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  double quantity,  String unit,  String category, @JsonKey(name: 'checked')  bool isChecked, @JsonKey(name: 'already_in_pantry')  bool alreadyInPantry, @JsonKey(name: 'from_dish_ids')  List<String> fromDishIds, @JsonKey(name: 'est_price_vnd')  int? estPriceVnd)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ShoppingListItemDto() when $default != null:
return $default(_that.id,_that.name,_that.quantity,_that.unit,_that.category,_that.isChecked,_that.alreadyInPantry,_that.fromDishIds,_that.estPriceVnd);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  double quantity,  String unit,  String category, @JsonKey(name: 'checked')  bool isChecked, @JsonKey(name: 'already_in_pantry')  bool alreadyInPantry, @JsonKey(name: 'from_dish_ids')  List<String> fromDishIds, @JsonKey(name: 'est_price_vnd')  int? estPriceVnd)  $default,) {final _that = this;
switch (_that) {
case _ShoppingListItemDto():
return $default(_that.id,_that.name,_that.quantity,_that.unit,_that.category,_that.isChecked,_that.alreadyInPantry,_that.fromDishIds,_that.estPriceVnd);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  double quantity,  String unit,  String category, @JsonKey(name: 'checked')  bool isChecked, @JsonKey(name: 'already_in_pantry')  bool alreadyInPantry, @JsonKey(name: 'from_dish_ids')  List<String> fromDishIds, @JsonKey(name: 'est_price_vnd')  int? estPriceVnd)?  $default,) {final _that = this;
switch (_that) {
case _ShoppingListItemDto() when $default != null:
return $default(_that.id,_that.name,_that.quantity,_that.unit,_that.category,_that.isChecked,_that.alreadyInPantry,_that.fromDishIds,_that.estPriceVnd);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ShoppingListItemDto extends ShoppingListItemDto {
  const _ShoppingListItemDto({required this.id, required this.name, required this.quantity, required this.unit, this.category = 'Khác', @JsonKey(name: 'checked') this.isChecked = false, @JsonKey(name: 'already_in_pantry') this.alreadyInPantry = false, @JsonKey(name: 'from_dish_ids') final  List<String> fromDishIds = const <String>[], @JsonKey(name: 'est_price_vnd') this.estPriceVnd}): _fromDishIds = fromDishIds,super._();
  factory _ShoppingListItemDto.fromJson(Map<String, dynamic> json) => _$ShoppingListItemDtoFromJson(json);

@override final  String id;
@override final  String name;
@override final  double quantity;
@override final  String unit;
@override@JsonKey() final  String category;
@override@JsonKey(name: 'checked') final  bool isChecked;
@override@JsonKey(name: 'already_in_pantry') final  bool alreadyInPantry;
 final  List<String> _fromDishIds;
@override@JsonKey(name: 'from_dish_ids') List<String> get fromDishIds {
  if (_fromDishIds is EqualUnmodifiableListView) return _fromDishIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_fromDishIds);
}

@override@JsonKey(name: 'est_price_vnd') final  int? estPriceVnd;

/// Create a copy of ShoppingListItemDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ShoppingListItemDtoCopyWith<_ShoppingListItemDto> get copyWith => __$ShoppingListItemDtoCopyWithImpl<_ShoppingListItemDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ShoppingListItemDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ShoppingListItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.category, category) || other.category == category)&&(identical(other.isChecked, isChecked) || other.isChecked == isChecked)&&(identical(other.alreadyInPantry, alreadyInPantry) || other.alreadyInPantry == alreadyInPantry)&&const DeepCollectionEquality().equals(other._fromDishIds, _fromDishIds)&&(identical(other.estPriceVnd, estPriceVnd) || other.estPriceVnd == estPriceVnd));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,quantity,unit,category,isChecked,alreadyInPantry,const DeepCollectionEquality().hash(_fromDishIds),estPriceVnd);

@override
String toString() {
  return 'ShoppingListItemDto(id: $id, name: $name, quantity: $quantity, unit: $unit, category: $category, isChecked: $isChecked, alreadyInPantry: $alreadyInPantry, fromDishIds: $fromDishIds, estPriceVnd: $estPriceVnd)';
}


}

/// @nodoc
abstract mixin class _$ShoppingListItemDtoCopyWith<$Res> implements $ShoppingListItemDtoCopyWith<$Res> {
  factory _$ShoppingListItemDtoCopyWith(_ShoppingListItemDto value, $Res Function(_ShoppingListItemDto) _then) = __$ShoppingListItemDtoCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, double quantity, String unit, String category,@JsonKey(name: 'checked') bool isChecked,@JsonKey(name: 'already_in_pantry') bool alreadyInPantry,@JsonKey(name: 'from_dish_ids') List<String> fromDishIds,@JsonKey(name: 'est_price_vnd') int? estPriceVnd
});




}
/// @nodoc
class __$ShoppingListItemDtoCopyWithImpl<$Res>
    implements _$ShoppingListItemDtoCopyWith<$Res> {
  __$ShoppingListItemDtoCopyWithImpl(this._self, this._then);

  final _ShoppingListItemDto _self;
  final $Res Function(_ShoppingListItemDto) _then;

/// Create a copy of ShoppingListItemDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? quantity = null,Object? unit = null,Object? category = null,Object? isChecked = null,Object? alreadyInPantry = null,Object? fromDishIds = null,Object? estPriceVnd = freezed,}) {
  return _then(_ShoppingListItemDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,category: null == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String,isChecked: null == isChecked ? _self.isChecked : isChecked // ignore: cast_nullable_to_non_nullable
as bool,alreadyInPantry: null == alreadyInPantry ? _self.alreadyInPantry : alreadyInPantry // ignore: cast_nullable_to_non_nullable
as bool,fromDishIds: null == fromDishIds ? _self._fromDishIds : fromDishIds // ignore: cast_nullable_to_non_nullable
as List<String>,estPriceVnd: freezed == estPriceVnd ? _self.estPriceVnd : estPriceVnd // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}


/// @nodoc
mixin _$ShoppingListDto {

 String get id;@JsonKey(name: 'source_label') String? get sourceLabel; List<ShoppingListItemDto> get items;
/// Create a copy of ShoppingListDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ShoppingListDtoCopyWith<ShoppingListDto> get copyWith => _$ShoppingListDtoCopyWithImpl<ShoppingListDto>(this as ShoppingListDto, _$identity);

  /// Serializes this ShoppingListDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ShoppingListDto&&(identical(other.id, id) || other.id == id)&&(identical(other.sourceLabel, sourceLabel) || other.sourceLabel == sourceLabel)&&const DeepCollectionEquality().equals(other.items, items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,sourceLabel,const DeepCollectionEquality().hash(items));

@override
String toString() {
  return 'ShoppingListDto(id: $id, sourceLabel: $sourceLabel, items: $items)';
}


}

/// @nodoc
abstract mixin class $ShoppingListDtoCopyWith<$Res>  {
  factory $ShoppingListDtoCopyWith(ShoppingListDto value, $Res Function(ShoppingListDto) _then) = _$ShoppingListDtoCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'source_label') String? sourceLabel, List<ShoppingListItemDto> items
});




}
/// @nodoc
class _$ShoppingListDtoCopyWithImpl<$Res>
    implements $ShoppingListDtoCopyWith<$Res> {
  _$ShoppingListDtoCopyWithImpl(this._self, this._then);

  final ShoppingListDto _self;
  final $Res Function(ShoppingListDto) _then;

/// Create a copy of ShoppingListDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? sourceLabel = freezed,Object? items = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,sourceLabel: freezed == sourceLabel ? _self.sourceLabel : sourceLabel // ignore: cast_nullable_to_non_nullable
as String?,items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<ShoppingListItemDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [ShoppingListDto].
extension ShoppingListDtoPatterns on ShoppingListDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ShoppingListDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ShoppingListDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ShoppingListDto value)  $default,){
final _that = this;
switch (_that) {
case _ShoppingListDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ShoppingListDto value)?  $default,){
final _that = this;
switch (_that) {
case _ShoppingListDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'source_label')  String? sourceLabel,  List<ShoppingListItemDto> items)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ShoppingListDto() when $default != null:
return $default(_that.id,_that.sourceLabel,_that.items);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'source_label')  String? sourceLabel,  List<ShoppingListItemDto> items)  $default,) {final _that = this;
switch (_that) {
case _ShoppingListDto():
return $default(_that.id,_that.sourceLabel,_that.items);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'source_label')  String? sourceLabel,  List<ShoppingListItemDto> items)?  $default,) {final _that = this;
switch (_that) {
case _ShoppingListDto() when $default != null:
return $default(_that.id,_that.sourceLabel,_that.items);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ShoppingListDto extends ShoppingListDto {
  const _ShoppingListDto({required this.id, @JsonKey(name: 'source_label') this.sourceLabel, final  List<ShoppingListItemDto> items = const <ShoppingListItemDto>[]}): _items = items,super._();
  factory _ShoppingListDto.fromJson(Map<String, dynamic> json) => _$ShoppingListDtoFromJson(json);

@override final  String id;
@override@JsonKey(name: 'source_label') final  String? sourceLabel;
 final  List<ShoppingListItemDto> _items;
@override@JsonKey() List<ShoppingListItemDto> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


/// Create a copy of ShoppingListDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ShoppingListDtoCopyWith<_ShoppingListDto> get copyWith => __$ShoppingListDtoCopyWithImpl<_ShoppingListDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ShoppingListDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ShoppingListDto&&(identical(other.id, id) || other.id == id)&&(identical(other.sourceLabel, sourceLabel) || other.sourceLabel == sourceLabel)&&const DeepCollectionEquality().equals(other._items, _items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,sourceLabel,const DeepCollectionEquality().hash(_items));

@override
String toString() {
  return 'ShoppingListDto(id: $id, sourceLabel: $sourceLabel, items: $items)';
}


}

/// @nodoc
abstract mixin class _$ShoppingListDtoCopyWith<$Res> implements $ShoppingListDtoCopyWith<$Res> {
  factory _$ShoppingListDtoCopyWith(_ShoppingListDto value, $Res Function(_ShoppingListDto) _then) = __$ShoppingListDtoCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'source_label') String? sourceLabel, List<ShoppingListItemDto> items
});




}
/// @nodoc
class __$ShoppingListDtoCopyWithImpl<$Res>
    implements _$ShoppingListDtoCopyWith<$Res> {
  __$ShoppingListDtoCopyWithImpl(this._self, this._then);

  final _ShoppingListDto _self;
  final $Res Function(_ShoppingListDto) _then;

/// Create a copy of ShoppingListDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? sourceLabel = freezed,Object? items = null,}) {
  return _then(_ShoppingListDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,sourceLabel: freezed == sourceLabel ? _self.sourceLabel : sourceLabel // ignore: cast_nullable_to_non_nullable
as String?,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<ShoppingListItemDto>,
  ));
}


}

// dart format on
