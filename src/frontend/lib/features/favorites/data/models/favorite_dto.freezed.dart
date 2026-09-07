// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'favorite_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$FavoriteRecipeDto {

@JsonKey(name: 'recipe_id') String get recipeId;@JsonKey(name: 'is_favorite') bool get isFavorite;
/// Create a copy of FavoriteRecipeDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FavoriteRecipeDtoCopyWith<FavoriteRecipeDto> get copyWith => _$FavoriteRecipeDtoCopyWithImpl<FavoriteRecipeDto>(this as FavoriteRecipeDto, _$identity);

  /// Serializes this FavoriteRecipeDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FavoriteRecipeDto&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.isFavorite, isFavorite) || other.isFavorite == isFavorite));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeId,isFavorite);

@override
String toString() {
  return 'FavoriteRecipeDto(recipeId: $recipeId, isFavorite: $isFavorite)';
}


}

/// @nodoc
abstract mixin class $FavoriteRecipeDtoCopyWith<$Res>  {
  factory $FavoriteRecipeDtoCopyWith(FavoriteRecipeDto value, $Res Function(FavoriteRecipeDto) _then) = _$FavoriteRecipeDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'is_favorite') bool isFavorite
});




}
/// @nodoc
class _$FavoriteRecipeDtoCopyWithImpl<$Res>
    implements $FavoriteRecipeDtoCopyWith<$Res> {
  _$FavoriteRecipeDtoCopyWithImpl(this._self, this._then);

  final FavoriteRecipeDto _self;
  final $Res Function(FavoriteRecipeDto) _then;

/// Create a copy of FavoriteRecipeDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeId = null,Object? isFavorite = null,}) {
  return _then(_self.copyWith(
recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,isFavorite: null == isFavorite ? _self.isFavorite : isFavorite // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [FavoriteRecipeDto].
extension FavoriteRecipeDtoPatterns on FavoriteRecipeDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FavoriteRecipeDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FavoriteRecipeDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FavoriteRecipeDto value)  $default,){
final _that = this;
switch (_that) {
case _FavoriteRecipeDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FavoriteRecipeDto value)?  $default,){
final _that = this;
switch (_that) {
case _FavoriteRecipeDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'is_favorite')  bool isFavorite)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FavoriteRecipeDto() when $default != null:
return $default(_that.recipeId,_that.isFavorite);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'is_favorite')  bool isFavorite)  $default,) {final _that = this;
switch (_that) {
case _FavoriteRecipeDto():
return $default(_that.recipeId,_that.isFavorite);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'is_favorite')  bool isFavorite)?  $default,) {final _that = this;
switch (_that) {
case _FavoriteRecipeDto() when $default != null:
return $default(_that.recipeId,_that.isFavorite);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _FavoriteRecipeDto extends FavoriteRecipeDto {
  const _FavoriteRecipeDto({@JsonKey(name: 'recipe_id') required this.recipeId, @JsonKey(name: 'is_favorite') required this.isFavorite}): super._();
  factory _FavoriteRecipeDto.fromJson(Map<String, dynamic> json) => _$FavoriteRecipeDtoFromJson(json);

@override@JsonKey(name: 'recipe_id') final  String recipeId;
@override@JsonKey(name: 'is_favorite') final  bool isFavorite;

/// Create a copy of FavoriteRecipeDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FavoriteRecipeDtoCopyWith<_FavoriteRecipeDto> get copyWith => __$FavoriteRecipeDtoCopyWithImpl<_FavoriteRecipeDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FavoriteRecipeDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FavoriteRecipeDto&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.isFavorite, isFavorite) || other.isFavorite == isFavorite));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeId,isFavorite);

@override
String toString() {
  return 'FavoriteRecipeDto(recipeId: $recipeId, isFavorite: $isFavorite)';
}


}

/// @nodoc
abstract mixin class _$FavoriteRecipeDtoCopyWith<$Res> implements $FavoriteRecipeDtoCopyWith<$Res> {
  factory _$FavoriteRecipeDtoCopyWith(_FavoriteRecipeDto value, $Res Function(_FavoriteRecipeDto) _then) = __$FavoriteRecipeDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'is_favorite') bool isFavorite
});




}
/// @nodoc
class __$FavoriteRecipeDtoCopyWithImpl<$Res>
    implements _$FavoriteRecipeDtoCopyWith<$Res> {
  __$FavoriteRecipeDtoCopyWithImpl(this._self, this._then);

  final _FavoriteRecipeDto _self;
  final $Res Function(_FavoriteRecipeDto) _then;

/// Create a copy of FavoriteRecipeDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeId = null,Object? isFavorite = null,}) {
  return _then(_FavoriteRecipeDto(
recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,isFavorite: null == isFavorite ? _self.isFavorite : isFavorite // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$FavoriteRecipeListItemDto {

@JsonKey(name: 'recipe_id') String get recipeId;@JsonKey(name: 'recipe_name') String get recipeName;@JsonKey(name: 'recipe_description') String get recipeDescription;@JsonKey(name: 'media_url') String? get mediaUrl;@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime get createdAt;
/// Create a copy of FavoriteRecipeListItemDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FavoriteRecipeListItemDtoCopyWith<FavoriteRecipeListItemDto> get copyWith => _$FavoriteRecipeListItemDtoCopyWithImpl<FavoriteRecipeListItemDto>(this as FavoriteRecipeListItemDto, _$identity);

  /// Serializes this FavoriteRecipeListItemDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FavoriteRecipeListItemDto&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.recipeDescription, recipeDescription) || other.recipeDescription == recipeDescription)&&(identical(other.mediaUrl, mediaUrl) || other.mediaUrl == mediaUrl)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeId,recipeName,recipeDescription,mediaUrl,createdAt);

@override
String toString() {
  return 'FavoriteRecipeListItemDto(recipeId: $recipeId, recipeName: $recipeName, recipeDescription: $recipeDescription, mediaUrl: $mediaUrl, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $FavoriteRecipeListItemDtoCopyWith<$Res>  {
  factory $FavoriteRecipeListItemDtoCopyWith(FavoriteRecipeListItemDto value, $Res Function(FavoriteRecipeListItemDto) _then) = _$FavoriteRecipeListItemDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName,@JsonKey(name: 'recipe_description') String recipeDescription,@JsonKey(name: 'media_url') String? mediaUrl,@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime createdAt
});




}
/// @nodoc
class _$FavoriteRecipeListItemDtoCopyWithImpl<$Res>
    implements $FavoriteRecipeListItemDtoCopyWith<$Res> {
  _$FavoriteRecipeListItemDtoCopyWithImpl(this._self, this._then);

  final FavoriteRecipeListItemDto _self;
  final $Res Function(FavoriteRecipeListItemDto) _then;

/// Create a copy of FavoriteRecipeListItemDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeId = null,Object? recipeName = null,Object? recipeDescription = null,Object? mediaUrl = freezed,Object? createdAt = null,}) {
  return _then(_self.copyWith(
recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,recipeDescription: null == recipeDescription ? _self.recipeDescription : recipeDescription // ignore: cast_nullable_to_non_nullable
as String,mediaUrl: freezed == mediaUrl ? _self.mediaUrl : mediaUrl // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [FavoriteRecipeListItemDto].
extension FavoriteRecipeListItemDtoPatterns on FavoriteRecipeListItemDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FavoriteRecipeListItemDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FavoriteRecipeListItemDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FavoriteRecipeListItemDto value)  $default,){
final _that = this;
switch (_that) {
case _FavoriteRecipeListItemDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FavoriteRecipeListItemDto value)?  $default,){
final _that = this;
switch (_that) {
case _FavoriteRecipeListItemDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName, @JsonKey(name: 'recipe_description')  String recipeDescription, @JsonKey(name: 'media_url')  String? mediaUrl, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FavoriteRecipeListItemDto() when $default != null:
return $default(_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName, @JsonKey(name: 'recipe_description')  String recipeDescription, @JsonKey(name: 'media_url')  String? mediaUrl, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _FavoriteRecipeListItemDto():
return $default(_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName, @JsonKey(name: 'recipe_description')  String recipeDescription, @JsonKey(name: 'media_url')  String? mediaUrl, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _FavoriteRecipeListItemDto() when $default != null:
return $default(_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _FavoriteRecipeListItemDto extends FavoriteRecipeListItemDto {
  const _FavoriteRecipeListItemDto({@JsonKey(name: 'recipe_id') required this.recipeId, @JsonKey(name: 'recipe_name') required this.recipeName, @JsonKey(name: 'recipe_description') this.recipeDescription = '', @JsonKey(name: 'media_url') this.mediaUrl, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) required this.createdAt}): super._();
  factory _FavoriteRecipeListItemDto.fromJson(Map<String, dynamic> json) => _$FavoriteRecipeListItemDtoFromJson(json);

@override@JsonKey(name: 'recipe_id') final  String recipeId;
@override@JsonKey(name: 'recipe_name') final  String recipeName;
@override@JsonKey(name: 'recipe_description') final  String recipeDescription;
@override@JsonKey(name: 'media_url') final  String? mediaUrl;
@override@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) final  DateTime createdAt;

/// Create a copy of FavoriteRecipeListItemDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FavoriteRecipeListItemDtoCopyWith<_FavoriteRecipeListItemDto> get copyWith => __$FavoriteRecipeListItemDtoCopyWithImpl<_FavoriteRecipeListItemDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FavoriteRecipeListItemDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FavoriteRecipeListItemDto&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.recipeDescription, recipeDescription) || other.recipeDescription == recipeDescription)&&(identical(other.mediaUrl, mediaUrl) || other.mediaUrl == mediaUrl)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recipeId,recipeName,recipeDescription,mediaUrl,createdAt);

@override
String toString() {
  return 'FavoriteRecipeListItemDto(recipeId: $recipeId, recipeName: $recipeName, recipeDescription: $recipeDescription, mediaUrl: $mediaUrl, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$FavoriteRecipeListItemDtoCopyWith<$Res> implements $FavoriteRecipeListItemDtoCopyWith<$Res> {
  factory _$FavoriteRecipeListItemDtoCopyWith(_FavoriteRecipeListItemDto value, $Res Function(_FavoriteRecipeListItemDto) _then) = __$FavoriteRecipeListItemDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName,@JsonKey(name: 'recipe_description') String recipeDescription,@JsonKey(name: 'media_url') String? mediaUrl,@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime createdAt
});




}
/// @nodoc
class __$FavoriteRecipeListItemDtoCopyWithImpl<$Res>
    implements _$FavoriteRecipeListItemDtoCopyWith<$Res> {
  __$FavoriteRecipeListItemDtoCopyWithImpl(this._self, this._then);

  final _FavoriteRecipeListItemDto _self;
  final $Res Function(_FavoriteRecipeListItemDto) _then;

/// Create a copy of FavoriteRecipeListItemDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeId = null,Object? recipeName = null,Object? recipeDescription = null,Object? mediaUrl = freezed,Object? createdAt = null,}) {
  return _then(_FavoriteRecipeListItemDto(
recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,recipeDescription: null == recipeDescription ? _self.recipeDescription : recipeDescription // ignore: cast_nullable_to_non_nullable
as String,mediaUrl: freezed == mediaUrl ? _self.mediaUrl : mediaUrl // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}


/// @nodoc
mixin _$FavoriteRecipeListDto {

 List<FavoriteRecipeListItemDto> get items; int get total; int get limit; int get offset;
/// Create a copy of FavoriteRecipeListDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FavoriteRecipeListDtoCopyWith<FavoriteRecipeListDto> get copyWith => _$FavoriteRecipeListDtoCopyWithImpl<FavoriteRecipeListDto>(this as FavoriteRecipeListDto, _$identity);

  /// Serializes this FavoriteRecipeListDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FavoriteRecipeListDto&&const DeepCollectionEquality().equals(other.items, items)&&(identical(other.total, total) || other.total == total)&&(identical(other.limit, limit) || other.limit == limit)&&(identical(other.offset, offset) || other.offset == offset));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(items),total,limit,offset);

@override
String toString() {
  return 'FavoriteRecipeListDto(items: $items, total: $total, limit: $limit, offset: $offset)';
}


}

/// @nodoc
abstract mixin class $FavoriteRecipeListDtoCopyWith<$Res>  {
  factory $FavoriteRecipeListDtoCopyWith(FavoriteRecipeListDto value, $Res Function(FavoriteRecipeListDto) _then) = _$FavoriteRecipeListDtoCopyWithImpl;
@useResult
$Res call({
 List<FavoriteRecipeListItemDto> items, int total, int limit, int offset
});




}
/// @nodoc
class _$FavoriteRecipeListDtoCopyWithImpl<$Res>
    implements $FavoriteRecipeListDtoCopyWith<$Res> {
  _$FavoriteRecipeListDtoCopyWithImpl(this._self, this._then);

  final FavoriteRecipeListDto _self;
  final $Res Function(FavoriteRecipeListDto) _then;

/// Create a copy of FavoriteRecipeListDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? items = null,Object? total = null,Object? limit = null,Object? offset = null,}) {
  return _then(_self.copyWith(
items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<FavoriteRecipeListItemDto>,total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,limit: null == limit ? _self.limit : limit // ignore: cast_nullable_to_non_nullable
as int,offset: null == offset ? _self.offset : offset // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [FavoriteRecipeListDto].
extension FavoriteRecipeListDtoPatterns on FavoriteRecipeListDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FavoriteRecipeListDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FavoriteRecipeListDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FavoriteRecipeListDto value)  $default,){
final _that = this;
switch (_that) {
case _FavoriteRecipeListDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FavoriteRecipeListDto value)?  $default,){
final _that = this;
switch (_that) {
case _FavoriteRecipeListDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<FavoriteRecipeListItemDto> items,  int total,  int limit,  int offset)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FavoriteRecipeListDto() when $default != null:
return $default(_that.items,_that.total,_that.limit,_that.offset);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<FavoriteRecipeListItemDto> items,  int total,  int limit,  int offset)  $default,) {final _that = this;
switch (_that) {
case _FavoriteRecipeListDto():
return $default(_that.items,_that.total,_that.limit,_that.offset);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<FavoriteRecipeListItemDto> items,  int total,  int limit,  int offset)?  $default,) {final _that = this;
switch (_that) {
case _FavoriteRecipeListDto() when $default != null:
return $default(_that.items,_that.total,_that.limit,_that.offset);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _FavoriteRecipeListDto extends FavoriteRecipeListDto {
  const _FavoriteRecipeListDto({final  List<FavoriteRecipeListItemDto> items = const <FavoriteRecipeListItemDto>[], this.total = 0, this.limit = 20, this.offset = 0}): _items = items,super._();
  factory _FavoriteRecipeListDto.fromJson(Map<String, dynamic> json) => _$FavoriteRecipeListDtoFromJson(json);

 final  List<FavoriteRecipeListItemDto> _items;
@override@JsonKey() List<FavoriteRecipeListItemDto> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}

@override@JsonKey() final  int total;
@override@JsonKey() final  int limit;
@override@JsonKey() final  int offset;

/// Create a copy of FavoriteRecipeListDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FavoriteRecipeListDtoCopyWith<_FavoriteRecipeListDto> get copyWith => __$FavoriteRecipeListDtoCopyWithImpl<_FavoriteRecipeListDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FavoriteRecipeListDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FavoriteRecipeListDto&&const DeepCollectionEquality().equals(other._items, _items)&&(identical(other.total, total) || other.total == total)&&(identical(other.limit, limit) || other.limit == limit)&&(identical(other.offset, offset) || other.offset == offset));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_items),total,limit,offset);

@override
String toString() {
  return 'FavoriteRecipeListDto(items: $items, total: $total, limit: $limit, offset: $offset)';
}


}

/// @nodoc
abstract mixin class _$FavoriteRecipeListDtoCopyWith<$Res> implements $FavoriteRecipeListDtoCopyWith<$Res> {
  factory _$FavoriteRecipeListDtoCopyWith(_FavoriteRecipeListDto value, $Res Function(_FavoriteRecipeListDto) _then) = __$FavoriteRecipeListDtoCopyWithImpl;
@override @useResult
$Res call({
 List<FavoriteRecipeListItemDto> items, int total, int limit, int offset
});




}
/// @nodoc
class __$FavoriteRecipeListDtoCopyWithImpl<$Res>
    implements _$FavoriteRecipeListDtoCopyWith<$Res> {
  __$FavoriteRecipeListDtoCopyWithImpl(this._self, this._then);

  final _FavoriteRecipeListDto _self;
  final $Res Function(_FavoriteRecipeListDto) _then;

/// Create a copy of FavoriteRecipeListDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? items = null,Object? total = null,Object? limit = null,Object? offset = null,}) {
  return _then(_FavoriteRecipeListDto(
items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<FavoriteRecipeListItemDto>,total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,limit: null == limit ? _self.limit : limit // ignore: cast_nullable_to_non_nullable
as int,offset: null == offset ? _self.offset : offset // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$FavoriteMenuDto {

 String get id; String get name; String? get description;@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime get createdAt;@JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired) DateTime get updatedAt;
/// Create a copy of FavoriteMenuDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FavoriteMenuDtoCopyWith<FavoriteMenuDto> get copyWith => _$FavoriteMenuDtoCopyWithImpl<FavoriteMenuDto>(this as FavoriteMenuDto, _$identity);

  /// Serializes this FavoriteMenuDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FavoriteMenuDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,createdAt,updatedAt);

@override
String toString() {
  return 'FavoriteMenuDto(id: $id, name: $name, description: $description, createdAt: $createdAt, updatedAt: $updatedAt)';
}


}

/// @nodoc
abstract mixin class $FavoriteMenuDtoCopyWith<$Res>  {
  factory $FavoriteMenuDtoCopyWith(FavoriteMenuDto value, $Res Function(FavoriteMenuDto) _then) = _$FavoriteMenuDtoCopyWithImpl;
@useResult
$Res call({
 String id, String name, String? description,@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime createdAt,@JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired) DateTime updatedAt
});




}
/// @nodoc
class _$FavoriteMenuDtoCopyWithImpl<$Res>
    implements $FavoriteMenuDtoCopyWith<$Res> {
  _$FavoriteMenuDtoCopyWithImpl(this._self, this._then);

  final FavoriteMenuDto _self;
  final $Res Function(FavoriteMenuDto) _then;

/// Create a copy of FavoriteMenuDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? createdAt = null,Object? updatedAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [FavoriteMenuDto].
extension FavoriteMenuDtoPatterns on FavoriteMenuDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FavoriteMenuDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FavoriteMenuDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FavoriteMenuDto value)  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FavoriteMenuDto value)?  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String? description, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt, @JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired)  DateTime updatedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FavoriteMenuDto() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String? description, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt, @JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired)  DateTime updatedAt)  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuDto():
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String? description, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt, @JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired)  DateTime updatedAt)?  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuDto() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _FavoriteMenuDto extends FavoriteMenuDto {
  const _FavoriteMenuDto({required this.id, required this.name, this.description, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) required this.createdAt, @JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired) required this.updatedAt}): super._();
  factory _FavoriteMenuDto.fromJson(Map<String, dynamic> json) => _$FavoriteMenuDtoFromJson(json);

@override final  String id;
@override final  String name;
@override final  String? description;
@override@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) final  DateTime createdAt;
@override@JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired) final  DateTime updatedAt;

/// Create a copy of FavoriteMenuDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FavoriteMenuDtoCopyWith<_FavoriteMenuDto> get copyWith => __$FavoriteMenuDtoCopyWithImpl<_FavoriteMenuDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FavoriteMenuDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FavoriteMenuDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,createdAt,updatedAt);

@override
String toString() {
  return 'FavoriteMenuDto(id: $id, name: $name, description: $description, createdAt: $createdAt, updatedAt: $updatedAt)';
}


}

/// @nodoc
abstract mixin class _$FavoriteMenuDtoCopyWith<$Res> implements $FavoriteMenuDtoCopyWith<$Res> {
  factory _$FavoriteMenuDtoCopyWith(_FavoriteMenuDto value, $Res Function(_FavoriteMenuDto) _then) = __$FavoriteMenuDtoCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String? description,@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime createdAt,@JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired) DateTime updatedAt
});




}
/// @nodoc
class __$FavoriteMenuDtoCopyWithImpl<$Res>
    implements _$FavoriteMenuDtoCopyWith<$Res> {
  __$FavoriteMenuDtoCopyWithImpl(this._self, this._then);

  final _FavoriteMenuDto _self;
  final $Res Function(_FavoriteMenuDto) _then;

/// Create a copy of FavoriteMenuDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? createdAt = null,Object? updatedAt = null,}) {
  return _then(_FavoriteMenuDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}


/// @nodoc
mixin _$FavoriteMenuListDto {

 List<FavoriteMenuDto> get items; int get total; int get limit; int get offset;
/// Create a copy of FavoriteMenuListDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FavoriteMenuListDtoCopyWith<FavoriteMenuListDto> get copyWith => _$FavoriteMenuListDtoCopyWithImpl<FavoriteMenuListDto>(this as FavoriteMenuListDto, _$identity);

  /// Serializes this FavoriteMenuListDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FavoriteMenuListDto&&const DeepCollectionEquality().equals(other.items, items)&&(identical(other.total, total) || other.total == total)&&(identical(other.limit, limit) || other.limit == limit)&&(identical(other.offset, offset) || other.offset == offset));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(items),total,limit,offset);

@override
String toString() {
  return 'FavoriteMenuListDto(items: $items, total: $total, limit: $limit, offset: $offset)';
}


}

/// @nodoc
abstract mixin class $FavoriteMenuListDtoCopyWith<$Res>  {
  factory $FavoriteMenuListDtoCopyWith(FavoriteMenuListDto value, $Res Function(FavoriteMenuListDto) _then) = _$FavoriteMenuListDtoCopyWithImpl;
@useResult
$Res call({
 List<FavoriteMenuDto> items, int total, int limit, int offset
});




}
/// @nodoc
class _$FavoriteMenuListDtoCopyWithImpl<$Res>
    implements $FavoriteMenuListDtoCopyWith<$Res> {
  _$FavoriteMenuListDtoCopyWithImpl(this._self, this._then);

  final FavoriteMenuListDto _self;
  final $Res Function(FavoriteMenuListDto) _then;

/// Create a copy of FavoriteMenuListDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? items = null,Object? total = null,Object? limit = null,Object? offset = null,}) {
  return _then(_self.copyWith(
items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<FavoriteMenuDto>,total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,limit: null == limit ? _self.limit : limit // ignore: cast_nullable_to_non_nullable
as int,offset: null == offset ? _self.offset : offset // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [FavoriteMenuListDto].
extension FavoriteMenuListDtoPatterns on FavoriteMenuListDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FavoriteMenuListDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FavoriteMenuListDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FavoriteMenuListDto value)  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuListDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FavoriteMenuListDto value)?  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuListDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( List<FavoriteMenuDto> items,  int total,  int limit,  int offset)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FavoriteMenuListDto() when $default != null:
return $default(_that.items,_that.total,_that.limit,_that.offset);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( List<FavoriteMenuDto> items,  int total,  int limit,  int offset)  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuListDto():
return $default(_that.items,_that.total,_that.limit,_that.offset);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( List<FavoriteMenuDto> items,  int total,  int limit,  int offset)?  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuListDto() when $default != null:
return $default(_that.items,_that.total,_that.limit,_that.offset);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _FavoriteMenuListDto extends FavoriteMenuListDto {
  const _FavoriteMenuListDto({final  List<FavoriteMenuDto> items = const <FavoriteMenuDto>[], this.total = 0, this.limit = 20, this.offset = 0}): _items = items,super._();
  factory _FavoriteMenuListDto.fromJson(Map<String, dynamic> json) => _$FavoriteMenuListDtoFromJson(json);

 final  List<FavoriteMenuDto> _items;
@override@JsonKey() List<FavoriteMenuDto> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}

@override@JsonKey() final  int total;
@override@JsonKey() final  int limit;
@override@JsonKey() final  int offset;

/// Create a copy of FavoriteMenuListDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FavoriteMenuListDtoCopyWith<_FavoriteMenuListDto> get copyWith => __$FavoriteMenuListDtoCopyWithImpl<_FavoriteMenuListDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FavoriteMenuListDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FavoriteMenuListDto&&const DeepCollectionEquality().equals(other._items, _items)&&(identical(other.total, total) || other.total == total)&&(identical(other.limit, limit) || other.limit == limit)&&(identical(other.offset, offset) || other.offset == offset));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_items),total,limit,offset);

@override
String toString() {
  return 'FavoriteMenuListDto(items: $items, total: $total, limit: $limit, offset: $offset)';
}


}

/// @nodoc
abstract mixin class _$FavoriteMenuListDtoCopyWith<$Res> implements $FavoriteMenuListDtoCopyWith<$Res> {
  factory _$FavoriteMenuListDtoCopyWith(_FavoriteMenuListDto value, $Res Function(_FavoriteMenuListDto) _then) = __$FavoriteMenuListDtoCopyWithImpl;
@override @useResult
$Res call({
 List<FavoriteMenuDto> items, int total, int limit, int offset
});




}
/// @nodoc
class __$FavoriteMenuListDtoCopyWithImpl<$Res>
    implements _$FavoriteMenuListDtoCopyWith<$Res> {
  __$FavoriteMenuListDtoCopyWithImpl(this._self, this._then);

  final _FavoriteMenuListDto _self;
  final $Res Function(_FavoriteMenuListDto) _then;

/// Create a copy of FavoriteMenuListDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? items = null,Object? total = null,Object? limit = null,Object? offset = null,}) {
  return _then(_FavoriteMenuListDto(
items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<FavoriteMenuDto>,total: null == total ? _self.total : total // ignore: cast_nullable_to_non_nullable
as int,limit: null == limit ? _self.limit : limit // ignore: cast_nullable_to_non_nullable
as int,offset: null == offset ? _self.offset : offset // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$FavoriteMenuItemDto {

 String get id;@JsonKey(name: 'recipe_id') String get recipeId;@JsonKey(name: 'recipe_name') String get recipeName;@JsonKey(name: 'recipe_description') String get recipeDescription;@JsonKey(name: 'media_url') String? get mediaUrl;@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime get createdAt;
/// Create a copy of FavoriteMenuItemDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FavoriteMenuItemDtoCopyWith<FavoriteMenuItemDto> get copyWith => _$FavoriteMenuItemDtoCopyWithImpl<FavoriteMenuItemDto>(this as FavoriteMenuItemDto, _$identity);

  /// Serializes this FavoriteMenuItemDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FavoriteMenuItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.recipeDescription, recipeDescription) || other.recipeDescription == recipeDescription)&&(identical(other.mediaUrl, mediaUrl) || other.mediaUrl == mediaUrl)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,recipeId,recipeName,recipeDescription,mediaUrl,createdAt);

@override
String toString() {
  return 'FavoriteMenuItemDto(id: $id, recipeId: $recipeId, recipeName: $recipeName, recipeDescription: $recipeDescription, mediaUrl: $mediaUrl, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $FavoriteMenuItemDtoCopyWith<$Res>  {
  factory $FavoriteMenuItemDtoCopyWith(FavoriteMenuItemDto value, $Res Function(FavoriteMenuItemDto) _then) = _$FavoriteMenuItemDtoCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName,@JsonKey(name: 'recipe_description') String recipeDescription,@JsonKey(name: 'media_url') String? mediaUrl,@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime createdAt
});




}
/// @nodoc
class _$FavoriteMenuItemDtoCopyWithImpl<$Res>
    implements $FavoriteMenuItemDtoCopyWith<$Res> {
  _$FavoriteMenuItemDtoCopyWithImpl(this._self, this._then);

  final FavoriteMenuItemDto _self;
  final $Res Function(FavoriteMenuItemDto) _then;

/// Create a copy of FavoriteMenuItemDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? recipeId = null,Object? recipeName = null,Object? recipeDescription = null,Object? mediaUrl = freezed,Object? createdAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,recipeDescription: null == recipeDescription ? _self.recipeDescription : recipeDescription // ignore: cast_nullable_to_non_nullable
as String,mediaUrl: freezed == mediaUrl ? _self.mediaUrl : mediaUrl // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [FavoriteMenuItemDto].
extension FavoriteMenuItemDtoPatterns on FavoriteMenuItemDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FavoriteMenuItemDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FavoriteMenuItemDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FavoriteMenuItemDto value)  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuItemDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FavoriteMenuItemDto value)?  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuItemDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName, @JsonKey(name: 'recipe_description')  String recipeDescription, @JsonKey(name: 'media_url')  String? mediaUrl, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FavoriteMenuItemDto() when $default != null:
return $default(_that.id,_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName, @JsonKey(name: 'recipe_description')  String recipeDescription, @JsonKey(name: 'media_url')  String? mediaUrl, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt)  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuItemDto():
return $default(_that.id,_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName, @JsonKey(name: 'recipe_description')  String recipeDescription, @JsonKey(name: 'media_url')  String? mediaUrl, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt)?  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuItemDto() when $default != null:
return $default(_that.id,_that.recipeId,_that.recipeName,_that.recipeDescription,_that.mediaUrl,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _FavoriteMenuItemDto extends FavoriteMenuItemDto {
  const _FavoriteMenuItemDto({required this.id, @JsonKey(name: 'recipe_id') required this.recipeId, @JsonKey(name: 'recipe_name') required this.recipeName, @JsonKey(name: 'recipe_description') this.recipeDescription = '', @JsonKey(name: 'media_url') this.mediaUrl, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) required this.createdAt}): super._();
  factory _FavoriteMenuItemDto.fromJson(Map<String, dynamic> json) => _$FavoriteMenuItemDtoFromJson(json);

@override final  String id;
@override@JsonKey(name: 'recipe_id') final  String recipeId;
@override@JsonKey(name: 'recipe_name') final  String recipeName;
@override@JsonKey(name: 'recipe_description') final  String recipeDescription;
@override@JsonKey(name: 'media_url') final  String? mediaUrl;
@override@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) final  DateTime createdAt;

/// Create a copy of FavoriteMenuItemDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FavoriteMenuItemDtoCopyWith<_FavoriteMenuItemDto> get copyWith => __$FavoriteMenuItemDtoCopyWithImpl<_FavoriteMenuItemDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FavoriteMenuItemDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FavoriteMenuItemDto&&(identical(other.id, id) || other.id == id)&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.recipeDescription, recipeDescription) || other.recipeDescription == recipeDescription)&&(identical(other.mediaUrl, mediaUrl) || other.mediaUrl == mediaUrl)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,recipeId,recipeName,recipeDescription,mediaUrl,createdAt);

@override
String toString() {
  return 'FavoriteMenuItemDto(id: $id, recipeId: $recipeId, recipeName: $recipeName, recipeDescription: $recipeDescription, mediaUrl: $mediaUrl, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$FavoriteMenuItemDtoCopyWith<$Res> implements $FavoriteMenuItemDtoCopyWith<$Res> {
  factory _$FavoriteMenuItemDtoCopyWith(_FavoriteMenuItemDto value, $Res Function(_FavoriteMenuItemDto) _then) = __$FavoriteMenuItemDtoCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName,@JsonKey(name: 'recipe_description') String recipeDescription,@JsonKey(name: 'media_url') String? mediaUrl,@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime createdAt
});




}
/// @nodoc
class __$FavoriteMenuItemDtoCopyWithImpl<$Res>
    implements _$FavoriteMenuItemDtoCopyWith<$Res> {
  __$FavoriteMenuItemDtoCopyWithImpl(this._self, this._then);

  final _FavoriteMenuItemDto _self;
  final $Res Function(_FavoriteMenuItemDto) _then;

/// Create a copy of FavoriteMenuItemDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? recipeId = null,Object? recipeName = null,Object? recipeDescription = null,Object? mediaUrl = freezed,Object? createdAt = null,}) {
  return _then(_FavoriteMenuItemDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,recipeDescription: null == recipeDescription ? _self.recipeDescription : recipeDescription // ignore: cast_nullable_to_non_nullable
as String,mediaUrl: freezed == mediaUrl ? _self.mediaUrl : mediaUrl // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}


/// @nodoc
mixin _$FavoriteMenuDetailDto {

 String get id; String get name; String? get description;@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime get createdAt;@JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired) DateTime get updatedAt; List<FavoriteMenuItemDto> get items;
/// Create a copy of FavoriteMenuDetailDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FavoriteMenuDetailDtoCopyWith<FavoriteMenuDetailDto> get copyWith => _$FavoriteMenuDetailDtoCopyWithImpl<FavoriteMenuDetailDto>(this as FavoriteMenuDetailDto, _$identity);

  /// Serializes this FavoriteMenuDetailDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FavoriteMenuDetailDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&const DeepCollectionEquality().equals(other.items, items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,createdAt,updatedAt,const DeepCollectionEquality().hash(items));

@override
String toString() {
  return 'FavoriteMenuDetailDto(id: $id, name: $name, description: $description, createdAt: $createdAt, updatedAt: $updatedAt, items: $items)';
}


}

/// @nodoc
abstract mixin class $FavoriteMenuDetailDtoCopyWith<$Res>  {
  factory $FavoriteMenuDetailDtoCopyWith(FavoriteMenuDetailDto value, $Res Function(FavoriteMenuDetailDto) _then) = _$FavoriteMenuDetailDtoCopyWithImpl;
@useResult
$Res call({
 String id, String name, String? description,@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime createdAt,@JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired) DateTime updatedAt, List<FavoriteMenuItemDto> items
});




}
/// @nodoc
class _$FavoriteMenuDetailDtoCopyWithImpl<$Res>
    implements $FavoriteMenuDetailDtoCopyWith<$Res> {
  _$FavoriteMenuDetailDtoCopyWithImpl(this._self, this._then);

  final FavoriteMenuDetailDto _self;
  final $Res Function(FavoriteMenuDetailDto) _then;

/// Create a copy of FavoriteMenuDetailDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? createdAt = null,Object? updatedAt = null,Object? items = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<FavoriteMenuItemDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [FavoriteMenuDetailDto].
extension FavoriteMenuDetailDtoPatterns on FavoriteMenuDetailDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FavoriteMenuDetailDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FavoriteMenuDetailDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FavoriteMenuDetailDto value)  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuDetailDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FavoriteMenuDetailDto value)?  $default,){
final _that = this;
switch (_that) {
case _FavoriteMenuDetailDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String? description, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt, @JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired)  DateTime updatedAt,  List<FavoriteMenuItemDto> items)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FavoriteMenuDetailDto() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt,_that.items);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String? description, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt, @JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired)  DateTime updatedAt,  List<FavoriteMenuItemDto> items)  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuDetailDto():
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt,_that.items);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String? description, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired)  DateTime createdAt, @JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired)  DateTime updatedAt,  List<FavoriteMenuItemDto> items)?  $default,) {final _that = this;
switch (_that) {
case _FavoriteMenuDetailDto() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.createdAt,_that.updatedAt,_that.items);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _FavoriteMenuDetailDto extends FavoriteMenuDetailDto {
  const _FavoriteMenuDetailDto({required this.id, required this.name, this.description, @JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) required this.createdAt, @JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired) required this.updatedAt, final  List<FavoriteMenuItemDto> items = const <FavoriteMenuItemDto>[]}): _items = items,super._();
  factory _FavoriteMenuDetailDto.fromJson(Map<String, dynamic> json) => _$FavoriteMenuDetailDtoFromJson(json);

@override final  String id;
@override final  String name;
@override final  String? description;
@override@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) final  DateTime createdAt;
@override@JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired) final  DateTime updatedAt;
 final  List<FavoriteMenuItemDto> _items;
@override@JsonKey() List<FavoriteMenuItemDto> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


/// Create a copy of FavoriteMenuDetailDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FavoriteMenuDetailDtoCopyWith<_FavoriteMenuDetailDto> get copyWith => __$FavoriteMenuDetailDtoCopyWithImpl<_FavoriteMenuDetailDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FavoriteMenuDetailDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FavoriteMenuDetailDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&const DeepCollectionEquality().equals(other._items, _items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,createdAt,updatedAt,const DeepCollectionEquality().hash(_items));

@override
String toString() {
  return 'FavoriteMenuDetailDto(id: $id, name: $name, description: $description, createdAt: $createdAt, updatedAt: $updatedAt, items: $items)';
}


}

/// @nodoc
abstract mixin class _$FavoriteMenuDetailDtoCopyWith<$Res> implements $FavoriteMenuDetailDtoCopyWith<$Res> {
  factory _$FavoriteMenuDetailDtoCopyWith(_FavoriteMenuDetailDto value, $Res Function(_FavoriteMenuDetailDto) _then) = __$FavoriteMenuDetailDtoCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String? description,@JsonKey(name: 'created_at', fromJson: _parseDateTimeRequired) DateTime createdAt,@JsonKey(name: 'updated_at', fromJson: _parseDateTimeRequired) DateTime updatedAt, List<FavoriteMenuItemDto> items
});




}
/// @nodoc
class __$FavoriteMenuDetailDtoCopyWithImpl<$Res>
    implements _$FavoriteMenuDetailDtoCopyWith<$Res> {
  __$FavoriteMenuDetailDtoCopyWithImpl(this._self, this._then);

  final _FavoriteMenuDetailDto _self;
  final $Res Function(_FavoriteMenuDetailDto) _then;

/// Create a copy of FavoriteMenuDetailDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? createdAt = null,Object? updatedAt = null,Object? items = null,}) {
  return _then(_FavoriteMenuDetailDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<FavoriteMenuItemDto>,
  ));
}


}

// dart format on
