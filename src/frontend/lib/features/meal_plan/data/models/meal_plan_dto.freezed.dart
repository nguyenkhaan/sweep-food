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
mixin _$MealPlanEntryDto {

 DateTime get date; String get slot;@JsonKey(name: 'dish_id') String get dishId;@JsonKey(name: 'dish_name') String? get dishName;@JsonKey(name: 'dish_image_url') String? get dishImageUrl;
/// Create a copy of MealPlanEntryDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MealPlanEntryDtoCopyWith<MealPlanEntryDto> get copyWith => _$MealPlanEntryDtoCopyWithImpl<MealPlanEntryDto>(this as MealPlanEntryDto, _$identity);

  /// Serializes this MealPlanEntryDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MealPlanEntryDto&&(identical(other.date, date) || other.date == date)&&(identical(other.slot, slot) || other.slot == slot)&&(identical(other.dishId, dishId) || other.dishId == dishId)&&(identical(other.dishName, dishName) || other.dishName == dishName)&&(identical(other.dishImageUrl, dishImageUrl) || other.dishImageUrl == dishImageUrl));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,date,slot,dishId,dishName,dishImageUrl);

@override
String toString() {
  return 'MealPlanEntryDto(date: $date, slot: $slot, dishId: $dishId, dishName: $dishName, dishImageUrl: $dishImageUrl)';
}


}

/// @nodoc
abstract mixin class $MealPlanEntryDtoCopyWith<$Res>  {
  factory $MealPlanEntryDtoCopyWith(MealPlanEntryDto value, $Res Function(MealPlanEntryDto) _then) = _$MealPlanEntryDtoCopyWithImpl;
@useResult
$Res call({
 DateTime date, String slot,@JsonKey(name: 'dish_id') String dishId,@JsonKey(name: 'dish_name') String? dishName,@JsonKey(name: 'dish_image_url') String? dishImageUrl
});




}
/// @nodoc
class _$MealPlanEntryDtoCopyWithImpl<$Res>
    implements $MealPlanEntryDtoCopyWith<$Res> {
  _$MealPlanEntryDtoCopyWithImpl(this._self, this._then);

  final MealPlanEntryDto _self;
  final $Res Function(MealPlanEntryDto) _then;

/// Create a copy of MealPlanEntryDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? date = null,Object? slot = null,Object? dishId = null,Object? dishName = freezed,Object? dishImageUrl = freezed,}) {
  return _then(_self.copyWith(
date: null == date ? _self.date : date // ignore: cast_nullable_to_non_nullable
as DateTime,slot: null == slot ? _self.slot : slot // ignore: cast_nullable_to_non_nullable
as String,dishId: null == dishId ? _self.dishId : dishId // ignore: cast_nullable_to_non_nullable
as String,dishName: freezed == dishName ? _self.dishName : dishName // ignore: cast_nullable_to_non_nullable
as String?,dishImageUrl: freezed == dishImageUrl ? _self.dishImageUrl : dishImageUrl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [MealPlanEntryDto].
extension MealPlanEntryDtoPatterns on MealPlanEntryDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MealPlanEntryDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MealPlanEntryDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MealPlanEntryDto value)  $default,){
final _that = this;
switch (_that) {
case _MealPlanEntryDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MealPlanEntryDto value)?  $default,){
final _that = this;
switch (_that) {
case _MealPlanEntryDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( DateTime date,  String slot, @JsonKey(name: 'dish_id')  String dishId, @JsonKey(name: 'dish_name')  String? dishName, @JsonKey(name: 'dish_image_url')  String? dishImageUrl)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MealPlanEntryDto() when $default != null:
return $default(_that.date,_that.slot,_that.dishId,_that.dishName,_that.dishImageUrl);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( DateTime date,  String slot, @JsonKey(name: 'dish_id')  String dishId, @JsonKey(name: 'dish_name')  String? dishName, @JsonKey(name: 'dish_image_url')  String? dishImageUrl)  $default,) {final _that = this;
switch (_that) {
case _MealPlanEntryDto():
return $default(_that.date,_that.slot,_that.dishId,_that.dishName,_that.dishImageUrl);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( DateTime date,  String slot, @JsonKey(name: 'dish_id')  String dishId, @JsonKey(name: 'dish_name')  String? dishName, @JsonKey(name: 'dish_image_url')  String? dishImageUrl)?  $default,) {final _that = this;
switch (_that) {
case _MealPlanEntryDto() when $default != null:
return $default(_that.date,_that.slot,_that.dishId,_that.dishName,_that.dishImageUrl);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MealPlanEntryDto extends MealPlanEntryDto {
  const _MealPlanEntryDto({required this.date, required this.slot, @JsonKey(name: 'dish_id') required this.dishId, @JsonKey(name: 'dish_name') this.dishName, @JsonKey(name: 'dish_image_url') this.dishImageUrl}): super._();
  factory _MealPlanEntryDto.fromJson(Map<String, dynamic> json) => _$MealPlanEntryDtoFromJson(json);

@override final  DateTime date;
@override final  String slot;
@override@JsonKey(name: 'dish_id') final  String dishId;
@override@JsonKey(name: 'dish_name') final  String? dishName;
@override@JsonKey(name: 'dish_image_url') final  String? dishImageUrl;

/// Create a copy of MealPlanEntryDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MealPlanEntryDtoCopyWith<_MealPlanEntryDto> get copyWith => __$MealPlanEntryDtoCopyWithImpl<_MealPlanEntryDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MealPlanEntryDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MealPlanEntryDto&&(identical(other.date, date) || other.date == date)&&(identical(other.slot, slot) || other.slot == slot)&&(identical(other.dishId, dishId) || other.dishId == dishId)&&(identical(other.dishName, dishName) || other.dishName == dishName)&&(identical(other.dishImageUrl, dishImageUrl) || other.dishImageUrl == dishImageUrl));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,date,slot,dishId,dishName,dishImageUrl);

@override
String toString() {
  return 'MealPlanEntryDto(date: $date, slot: $slot, dishId: $dishId, dishName: $dishName, dishImageUrl: $dishImageUrl)';
}


}

/// @nodoc
abstract mixin class _$MealPlanEntryDtoCopyWith<$Res> implements $MealPlanEntryDtoCopyWith<$Res> {
  factory _$MealPlanEntryDtoCopyWith(_MealPlanEntryDto value, $Res Function(_MealPlanEntryDto) _then) = __$MealPlanEntryDtoCopyWithImpl;
@override @useResult
$Res call({
 DateTime date, String slot,@JsonKey(name: 'dish_id') String dishId,@JsonKey(name: 'dish_name') String? dishName,@JsonKey(name: 'dish_image_url') String? dishImageUrl
});




}
/// @nodoc
class __$MealPlanEntryDtoCopyWithImpl<$Res>
    implements _$MealPlanEntryDtoCopyWith<$Res> {
  __$MealPlanEntryDtoCopyWithImpl(this._self, this._then);

  final _MealPlanEntryDto _self;
  final $Res Function(_MealPlanEntryDto) _then;

/// Create a copy of MealPlanEntryDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? date = null,Object? slot = null,Object? dishId = null,Object? dishName = freezed,Object? dishImageUrl = freezed,}) {
  return _then(_MealPlanEntryDto(
date: null == date ? _self.date : date // ignore: cast_nullable_to_non_nullable
as DateTime,slot: null == slot ? _self.slot : slot // ignore: cast_nullable_to_non_nullable
as String,dishId: null == dishId ? _self.dishId : dishId // ignore: cast_nullable_to_non_nullable
as String,dishName: freezed == dishName ? _self.dishName : dishName // ignore: cast_nullable_to_non_nullable
as String?,dishImageUrl: freezed == dishImageUrl ? _self.dishImageUrl : dishImageUrl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$MealPlanDto {

@JsonKey(name: 'week_start') DateTime get weekStart; List<MealPlanEntryDto> get entries;
/// Create a copy of MealPlanDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MealPlanDtoCopyWith<MealPlanDto> get copyWith => _$MealPlanDtoCopyWithImpl<MealPlanDto>(this as MealPlanDto, _$identity);

  /// Serializes this MealPlanDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MealPlanDto&&(identical(other.weekStart, weekStart) || other.weekStart == weekStart)&&const DeepCollectionEquality().equals(other.entries, entries));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,weekStart,const DeepCollectionEquality().hash(entries));

@override
String toString() {
  return 'MealPlanDto(weekStart: $weekStart, entries: $entries)';
}


}

/// @nodoc
abstract mixin class $MealPlanDtoCopyWith<$Res>  {
  factory $MealPlanDtoCopyWith(MealPlanDto value, $Res Function(MealPlanDto) _then) = _$MealPlanDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'week_start') DateTime weekStart, List<MealPlanEntryDto> entries
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
@pragma('vm:prefer-inline') @override $Res call({Object? weekStart = null,Object? entries = null,}) {
  return _then(_self.copyWith(
weekStart: null == weekStart ? _self.weekStart : weekStart // ignore: cast_nullable_to_non_nullable
as DateTime,entries: null == entries ? _self.entries : entries // ignore: cast_nullable_to_non_nullable
as List<MealPlanEntryDto>,
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'week_start')  DateTime weekStart,  List<MealPlanEntryDto> entries)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MealPlanDto() when $default != null:
return $default(_that.weekStart,_that.entries);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'week_start')  DateTime weekStart,  List<MealPlanEntryDto> entries)  $default,) {final _that = this;
switch (_that) {
case _MealPlanDto():
return $default(_that.weekStart,_that.entries);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'week_start')  DateTime weekStart,  List<MealPlanEntryDto> entries)?  $default,) {final _that = this;
switch (_that) {
case _MealPlanDto() when $default != null:
return $default(_that.weekStart,_that.entries);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MealPlanDto extends MealPlanDto {
  const _MealPlanDto({@JsonKey(name: 'week_start') required this.weekStart, final  List<MealPlanEntryDto> entries = const <MealPlanEntryDto>[]}): _entries = entries,super._();
  factory _MealPlanDto.fromJson(Map<String, dynamic> json) => _$MealPlanDtoFromJson(json);

@override@JsonKey(name: 'week_start') final  DateTime weekStart;
 final  List<MealPlanEntryDto> _entries;
@override@JsonKey() List<MealPlanEntryDto> get entries {
  if (_entries is EqualUnmodifiableListView) return _entries;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_entries);
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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MealPlanDto&&(identical(other.weekStart, weekStart) || other.weekStart == weekStart)&&const DeepCollectionEquality().equals(other._entries, _entries));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,weekStart,const DeepCollectionEquality().hash(_entries));

@override
String toString() {
  return 'MealPlanDto(weekStart: $weekStart, entries: $entries)';
}


}

/// @nodoc
abstract mixin class _$MealPlanDtoCopyWith<$Res> implements $MealPlanDtoCopyWith<$Res> {
  factory _$MealPlanDtoCopyWith(_MealPlanDto value, $Res Function(_MealPlanDto) _then) = __$MealPlanDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'week_start') DateTime weekStart, List<MealPlanEntryDto> entries
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
@override @pragma('vm:prefer-inline') $Res call({Object? weekStart = null,Object? entries = null,}) {
  return _then(_MealPlanDto(
weekStart: null == weekStart ? _self.weekStart : weekStart // ignore: cast_nullable_to_non_nullable
as DateTime,entries: null == entries ? _self._entries : entries // ignore: cast_nullable_to_non_nullable
as List<MealPlanEntryDto>,
  ));
}


}

// dart format on
