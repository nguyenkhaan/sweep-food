// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'meal_plan_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$MealPlanItemDto {

 String get id;@JsonKey(name: 'recipe_id') String get recipeId;@JsonKey(name: 'recipe_name') String? get recipeName;@JsonKey(name: 'planned_for') DateTime get plannedFor;@JsonKey(name: 'meal_slot') String get mealSlot; double get servings; String get status;
/// Create a copy of MealPlanItemDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MealPlanItemDtoCopyWith<MealPlanItemDto> get copyWith => _$MealPlanItemDtoCopyWithImpl<MealPlanItemDto>(this as MealPlanItemDto, _$identity);

  /// Serializes this MealPlanItemDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MealPlanItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.plannedFor, plannedFor) || other.plannedFor == plannedFor)&&(identical(other.mealSlot, mealSlot) || other.mealSlot == mealSlot)&&(identical(other.servings, servings) || other.servings == servings)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,recipeId,recipeName,plannedFor,mealSlot,servings,status);

@override
String toString() {
  return 'MealPlanItemDto(id: $id, recipeId: $recipeId, recipeName: $recipeName, plannedFor: $plannedFor, mealSlot: $mealSlot, servings: $servings, status: $status)';
}


}

/// @nodoc
abstract mixin class $MealPlanItemDtoCopyWith<$Res>  {
  factory $MealPlanItemDtoCopyWith(MealPlanItemDto value, $Res Function(MealPlanItemDto) _then) = _$MealPlanItemDtoCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String? recipeName,@JsonKey(name: 'planned_for') DateTime plannedFor,@JsonKey(name: 'meal_slot') String mealSlot, double servings, String status
});




}
/// @nodoc
class _$MealPlanItemDtoCopyWithImpl<$Res>
    implements $MealPlanItemDtoCopyWith<$Res> {
  _$MealPlanItemDtoCopyWithImpl(this._self, this._then);

  final MealPlanItemDto _self;
  final $Res Function(MealPlanItemDto) _then;

/// Create a copy of MealPlanItemDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? recipeId = null,Object? recipeName = freezed,Object? plannedFor = null,Object? mealSlot = null,Object? servings = null,Object? status = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: freezed == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String?,plannedFor: null == plannedFor ? _self.plannedFor : plannedFor // ignore: cast_nullable_to_non_nullable
as DateTime,mealSlot: null == mealSlot ? _self.mealSlot : mealSlot // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [MealPlanItemDto].
extension MealPlanItemDtoPatterns on MealPlanItemDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MealPlanItemDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MealPlanItemDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MealPlanItemDto value)  $default,){
final _that = this;
switch (_that) {
case _MealPlanItemDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MealPlanItemDto value)?  $default,){
final _that = this;
switch (_that) {
case _MealPlanItemDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String? recipeName, @JsonKey(name: 'planned_for')  DateTime plannedFor, @JsonKey(name: 'meal_slot')  String mealSlot,  double servings,  String status)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MealPlanItemDto() when $default != null:
return $default(_that.id,_that.recipeId,_that.recipeName,_that.plannedFor,_that.mealSlot,_that.servings,_that.status);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String? recipeName, @JsonKey(name: 'planned_for')  DateTime plannedFor, @JsonKey(name: 'meal_slot')  String mealSlot,  double servings,  String status)  $default,) {final _that = this;
switch (_that) {
case _MealPlanItemDto():
return $default(_that.id,_that.recipeId,_that.recipeName,_that.plannedFor,_that.mealSlot,_that.servings,_that.status);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String? recipeName, @JsonKey(name: 'planned_for')  DateTime plannedFor, @JsonKey(name: 'meal_slot')  String mealSlot,  double servings,  String status)?  $default,) {final _that = this;
switch (_that) {
case _MealPlanItemDto() when $default != null:
return $default(_that.id,_that.recipeId,_that.recipeName,_that.plannedFor,_that.mealSlot,_that.servings,_that.status);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MealPlanItemDto extends MealPlanItemDto {
  const _MealPlanItemDto({required this.id, @JsonKey(name: 'recipe_id') required this.recipeId, @JsonKey(name: 'recipe_name') this.recipeName, @JsonKey(name: 'planned_for') required this.plannedFor, @JsonKey(name: 'meal_slot') required this.mealSlot, required this.servings, this.status = 'PLANNED'}): super._();
  factory _MealPlanItemDto.fromJson(Map<String, dynamic> json) => _$MealPlanItemDtoFromJson(json);

@override final  String id;
@override@JsonKey(name: 'recipe_id') final  String recipeId;
@override@JsonKey(name: 'recipe_name') final  String? recipeName;
@override@JsonKey(name: 'planned_for') final  DateTime plannedFor;
@override@JsonKey(name: 'meal_slot') final  String mealSlot;
@override final  double servings;
@override@JsonKey() final  String status;

/// Create a copy of MealPlanItemDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MealPlanItemDtoCopyWith<_MealPlanItemDto> get copyWith => __$MealPlanItemDtoCopyWithImpl<_MealPlanItemDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MealPlanItemDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MealPlanItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.plannedFor, plannedFor) || other.plannedFor == plannedFor)&&(identical(other.mealSlot, mealSlot) || other.mealSlot == mealSlot)&&(identical(other.servings, servings) || other.servings == servings)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,recipeId,recipeName,plannedFor,mealSlot,servings,status);

@override
String toString() {
  return 'MealPlanItemDto(id: $id, recipeId: $recipeId, recipeName: $recipeName, plannedFor: $plannedFor, mealSlot: $mealSlot, servings: $servings, status: $status)';
}


}

/// @nodoc
abstract mixin class _$MealPlanItemDtoCopyWith<$Res> implements $MealPlanItemDtoCopyWith<$Res> {
  factory _$MealPlanItemDtoCopyWith(_MealPlanItemDto value, $Res Function(_MealPlanItemDto) _then) = __$MealPlanItemDtoCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String? recipeName,@JsonKey(name: 'planned_for') DateTime plannedFor,@JsonKey(name: 'meal_slot') String mealSlot, double servings, String status
});




}
/// @nodoc
class __$MealPlanItemDtoCopyWithImpl<$Res>
    implements _$MealPlanItemDtoCopyWith<$Res> {
  __$MealPlanItemDtoCopyWithImpl(this._self, this._then);

  final _MealPlanItemDto _self;
  final $Res Function(_MealPlanItemDto) _then;

/// Create a copy of MealPlanItemDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? recipeId = null,Object? recipeName = freezed,Object? plannedFor = null,Object? mealSlot = null,Object? servings = null,Object? status = null,}) {
  return _then(_MealPlanItemDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: freezed == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String?,plannedFor: null == plannedFor ? _self.plannedFor : plannedFor // ignore: cast_nullable_to_non_nullable
as DateTime,mealSlot: null == mealSlot ? _self.mealSlot : mealSlot // ignore: cast_nullable_to_non_nullable
as String,servings: null == servings ? _self.servings : servings // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$MealPlanDto {

 String get id; String? get name;@JsonKey(name: 'starts_on') DateTime get startsOn;@JsonKey(name: 'ends_on') DateTime get endsOn; List<MealPlanItemDto> get items;
/// Create a copy of MealPlanDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MealPlanDtoCopyWith<MealPlanDto> get copyWith => _$MealPlanDtoCopyWithImpl<MealPlanDto>(this as MealPlanDto, _$identity);

  /// Serializes this MealPlanDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MealPlanDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.startsOn, startsOn) || other.startsOn == startsOn)&&(identical(other.endsOn, endsOn) || other.endsOn == endsOn)&&const DeepCollectionEquality().equals(other.items, items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,startsOn,endsOn,const DeepCollectionEquality().hash(items));

@override
String toString() {
  return 'MealPlanDto(id: $id, name: $name, startsOn: $startsOn, endsOn: $endsOn, items: $items)';
}


}

/// @nodoc
abstract mixin class $MealPlanDtoCopyWith<$Res>  {
  factory $MealPlanDtoCopyWith(MealPlanDto value, $Res Function(MealPlanDto) _then) = _$MealPlanDtoCopyWithImpl;
@useResult
$Res call({
 String id, String? name,@JsonKey(name: 'starts_on') DateTime startsOn,@JsonKey(name: 'ends_on') DateTime endsOn, List<MealPlanItemDto> items
});




}
/// @nodoc
class _$MealPlanDtoCopyWithImpl<$Res>
    implements $MealPlanDtoCopyWith<$Res> {
  _$MealPlanDtoCopyWithImpl(this._self, this._then);

  final MealPlanDto _self;
  final $Res Function(MealPlanDto) _then;

/// Create a copy of MealPlanDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = freezed,Object? startsOn = null,Object? endsOn = null,Object? items = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,startsOn: null == startsOn ? _self.startsOn : startsOn // ignore: cast_nullable_to_non_nullable
as DateTime,endsOn: null == endsOn ? _self.endsOn : endsOn // ignore: cast_nullable_to_non_nullable
as DateTime,items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<MealPlanItemDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [MealPlanDto].
extension MealPlanDtoPatterns on MealPlanDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MealPlanDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MealPlanDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MealPlanDto value)  $default,){
final _that = this;
switch (_that) {
case _MealPlanDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MealPlanDto value)?  $default,){
final _that = this;
switch (_that) {
case _MealPlanDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String? name, @JsonKey(name: 'starts_on')  DateTime startsOn, @JsonKey(name: 'ends_on')  DateTime endsOn,  List<MealPlanItemDto> items)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MealPlanDto() when $default != null:
return $default(_that.id,_that.name,_that.startsOn,_that.endsOn,_that.items);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String? name, @JsonKey(name: 'starts_on')  DateTime startsOn, @JsonKey(name: 'ends_on')  DateTime endsOn,  List<MealPlanItemDto> items)  $default,) {final _that = this;
switch (_that) {
case _MealPlanDto():
return $default(_that.id,_that.name,_that.startsOn,_that.endsOn,_that.items);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String? name, @JsonKey(name: 'starts_on')  DateTime startsOn, @JsonKey(name: 'ends_on')  DateTime endsOn,  List<MealPlanItemDto> items)?  $default,) {final _that = this;
switch (_that) {
case _MealPlanDto() when $default != null:
return $default(_that.id,_that.name,_that.startsOn,_that.endsOn,_that.items);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MealPlanDto extends MealPlanDto {
  const _MealPlanDto({required this.id, this.name, @JsonKey(name: 'starts_on') required this.startsOn, @JsonKey(name: 'ends_on') required this.endsOn, final  List<MealPlanItemDto> items = const <MealPlanItemDto>[]}): _items = items,super._();
  factory _MealPlanDto.fromJson(Map<String, dynamic> json) => _$MealPlanDtoFromJson(json);

@override final  String id;
@override final  String? name;
@override@JsonKey(name: 'starts_on') final  DateTime startsOn;
@override@JsonKey(name: 'ends_on') final  DateTime endsOn;
 final  List<MealPlanItemDto> _items;
@override@JsonKey() List<MealPlanItemDto> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


/// Create a copy of MealPlanDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MealPlanDtoCopyWith<_MealPlanDto> get copyWith => __$MealPlanDtoCopyWithImpl<_MealPlanDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MealPlanDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MealPlanDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.startsOn, startsOn) || other.startsOn == startsOn)&&(identical(other.endsOn, endsOn) || other.endsOn == endsOn)&&const DeepCollectionEquality().equals(other._items, _items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,startsOn,endsOn,const DeepCollectionEquality().hash(_items));

@override
String toString() {
  return 'MealPlanDto(id: $id, name: $name, startsOn: $startsOn, endsOn: $endsOn, items: $items)';
}


}

/// @nodoc
abstract mixin class _$MealPlanDtoCopyWith<$Res> implements $MealPlanDtoCopyWith<$Res> {
  factory _$MealPlanDtoCopyWith(_MealPlanDto value, $Res Function(_MealPlanDto) _then) = __$MealPlanDtoCopyWithImpl;
@override @useResult
$Res call({
 String id, String? name,@JsonKey(name: 'starts_on') DateTime startsOn,@JsonKey(name: 'ends_on') DateTime endsOn, List<MealPlanItemDto> items
});




}
/// @nodoc
class __$MealPlanDtoCopyWithImpl<$Res>
    implements _$MealPlanDtoCopyWith<$Res> {
  __$MealPlanDtoCopyWithImpl(this._self, this._then);

  final _MealPlanDto _self;
  final $Res Function(_MealPlanDto) _then;

/// Create a copy of MealPlanDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = freezed,Object? startsOn = null,Object? endsOn = null,Object? items = null,}) {
  return _then(_MealPlanDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,startsOn: null == startsOn ? _self.startsOn : startsOn // ignore: cast_nullable_to_non_nullable
as DateTime,endsOn: null == endsOn ? _self.endsOn : endsOn // ignore: cast_nullable_to_non_nullable
as DateTime,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<MealPlanItemDto>,
  ));
}


}

// dart format on
