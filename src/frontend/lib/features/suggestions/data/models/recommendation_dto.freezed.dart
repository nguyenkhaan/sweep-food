// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'recommendation_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$MockRecommendationAnalysisDto {

 String get intent; String get summary;@JsonKey(name: 'is_mock') bool get isMock;
/// Create a copy of MockRecommendationAnalysisDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MockRecommendationAnalysisDtoCopyWith<MockRecommendationAnalysisDto> get copyWith => _$MockRecommendationAnalysisDtoCopyWithImpl<MockRecommendationAnalysisDto>(this as MockRecommendationAnalysisDto, _$identity);

  /// Serializes this MockRecommendationAnalysisDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MockRecommendationAnalysisDto&&(identical(other.intent, intent) || other.intent == intent)&&(identical(other.summary, summary) || other.summary == summary)&&(identical(other.isMock, isMock) || other.isMock == isMock));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,intent,summary,isMock);

@override
String toString() {
  return 'MockRecommendationAnalysisDto(intent: $intent, summary: $summary, isMock: $isMock)';
}


}

/// @nodoc
abstract mixin class $MockRecommendationAnalysisDtoCopyWith<$Res>  {
  factory $MockRecommendationAnalysisDtoCopyWith(MockRecommendationAnalysisDto value, $Res Function(MockRecommendationAnalysisDto) _then) = _$MockRecommendationAnalysisDtoCopyWithImpl;
@useResult
$Res call({
 String intent, String summary,@JsonKey(name: 'is_mock') bool isMock
});




}
/// @nodoc
class _$MockRecommendationAnalysisDtoCopyWithImpl<$Res>
    implements $MockRecommendationAnalysisDtoCopyWith<$Res> {
  _$MockRecommendationAnalysisDtoCopyWithImpl(this._self, this._then);

  final MockRecommendationAnalysisDto _self;
  final $Res Function(MockRecommendationAnalysisDto) _then;

/// Create a copy of MockRecommendationAnalysisDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? intent = null,Object? summary = null,Object? isMock = null,}) {
  return _then(_self.copyWith(
intent: null == intent ? _self.intent : intent // ignore: cast_nullable_to_non_nullable
as String,summary: null == summary ? _self.summary : summary // ignore: cast_nullable_to_non_nullable
as String,isMock: null == isMock ? _self.isMock : isMock // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [MockRecommendationAnalysisDto].
extension MockRecommendationAnalysisDtoPatterns on MockRecommendationAnalysisDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MockRecommendationAnalysisDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MockRecommendationAnalysisDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MockRecommendationAnalysisDto value)  $default,){
final _that = this;
switch (_that) {
case _MockRecommendationAnalysisDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MockRecommendationAnalysisDto value)?  $default,){
final _that = this;
switch (_that) {
case _MockRecommendationAnalysisDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String intent,  String summary, @JsonKey(name: 'is_mock')  bool isMock)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MockRecommendationAnalysisDto() when $default != null:
return $default(_that.intent,_that.summary,_that.isMock);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String intent,  String summary, @JsonKey(name: 'is_mock')  bool isMock)  $default,) {final _that = this;
switch (_that) {
case _MockRecommendationAnalysisDto():
return $default(_that.intent,_that.summary,_that.isMock);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String intent,  String summary, @JsonKey(name: 'is_mock')  bool isMock)?  $default,) {final _that = this;
switch (_that) {
case _MockRecommendationAnalysisDto() when $default != null:
return $default(_that.intent,_that.summary,_that.isMock);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MockRecommendationAnalysisDto extends MockRecommendationAnalysisDto {
  const _MockRecommendationAnalysisDto({this.intent = '', this.summary = '', @JsonKey(name: 'is_mock') this.isMock = false}): super._();
  factory _MockRecommendationAnalysisDto.fromJson(Map<String, dynamic> json) => _$MockRecommendationAnalysisDtoFromJson(json);

@override@JsonKey() final  String intent;
@override@JsonKey() final  String summary;
@override@JsonKey(name: 'is_mock') final  bool isMock;

/// Create a copy of MockRecommendationAnalysisDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MockRecommendationAnalysisDtoCopyWith<_MockRecommendationAnalysisDto> get copyWith => __$MockRecommendationAnalysisDtoCopyWithImpl<_MockRecommendationAnalysisDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MockRecommendationAnalysisDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MockRecommendationAnalysisDto&&(identical(other.intent, intent) || other.intent == intent)&&(identical(other.summary, summary) || other.summary == summary)&&(identical(other.isMock, isMock) || other.isMock == isMock));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,intent,summary,isMock);

@override
String toString() {
  return 'MockRecommendationAnalysisDto(intent: $intent, summary: $summary, isMock: $isMock)';
}


}

/// @nodoc
abstract mixin class _$MockRecommendationAnalysisDtoCopyWith<$Res> implements $MockRecommendationAnalysisDtoCopyWith<$Res> {
  factory _$MockRecommendationAnalysisDtoCopyWith(_MockRecommendationAnalysisDto value, $Res Function(_MockRecommendationAnalysisDto) _then) = __$MockRecommendationAnalysisDtoCopyWithImpl;
@override @useResult
$Res call({
 String intent, String summary,@JsonKey(name: 'is_mock') bool isMock
});




}
/// @nodoc
class __$MockRecommendationAnalysisDtoCopyWithImpl<$Res>
    implements _$MockRecommendationAnalysisDtoCopyWith<$Res> {
  __$MockRecommendationAnalysisDtoCopyWithImpl(this._self, this._then);

  final _MockRecommendationAnalysisDto _self;
  final $Res Function(_MockRecommendationAnalysisDto) _then;

/// Create a copy of MockRecommendationAnalysisDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? intent = null,Object? summary = null,Object? isMock = null,}) {
  return _then(_MockRecommendationAnalysisDto(
intent: null == intent ? _self.intent : intent // ignore: cast_nullable_to_non_nullable
as String,summary: null == summary ? _self.summary : summary // ignore: cast_nullable_to_non_nullable
as String,isMock: null == isMock ? _self.isMock : isMock // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

/// @nodoc
mixin _$RecommendationScoreComponentsDto {

@JsonKey(name: 'expiration_utilization', fromJson: _asDoubleDefault) double get expirationUtilization;@JsonKey(fromJson: _asDoubleDefault) double get availability;@JsonKey(name: 'preference_fit', fromJson: _asDoubleDefault) double get preferenceFit;@JsonKey(name: 'purchase_minimization', fromJson: _asDoubleDefault) double get purchaseMinimization;
/// Create a copy of RecommendationScoreComponentsDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecommendationScoreComponentsDtoCopyWith<RecommendationScoreComponentsDto> get copyWith => _$RecommendationScoreComponentsDtoCopyWithImpl<RecommendationScoreComponentsDto>(this as RecommendationScoreComponentsDto, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RecommendationScoreComponentsDto&&(identical(other.expirationUtilization, expirationUtilization) || other.expirationUtilization == expirationUtilization)&&(identical(other.availability, availability) || other.availability == availability)&&(identical(other.preferenceFit, preferenceFit) || other.preferenceFit == preferenceFit)&&(identical(other.purchaseMinimization, purchaseMinimization) || other.purchaseMinimization == purchaseMinimization));
}


@override
int get hashCode => Object.hash(runtimeType,expirationUtilization,availability,preferenceFit,purchaseMinimization);

@override
String toString() {
  return 'RecommendationScoreComponentsDto(expirationUtilization: $expirationUtilization, availability: $availability, preferenceFit: $preferenceFit, purchaseMinimization: $purchaseMinimization)';
}


}

/// @nodoc
abstract mixin class $RecommendationScoreComponentsDtoCopyWith<$Res>  {
  factory $RecommendationScoreComponentsDtoCopyWith(RecommendationScoreComponentsDto value, $Res Function(RecommendationScoreComponentsDto) _then) = _$RecommendationScoreComponentsDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'expiration_utilization', fromJson: _asDoubleDefault) double expirationUtilization,@JsonKey(fromJson: _asDoubleDefault) double availability,@JsonKey(name: 'preference_fit', fromJson: _asDoubleDefault) double preferenceFit,@JsonKey(name: 'purchase_minimization', fromJson: _asDoubleDefault) double purchaseMinimization
});




}
/// @nodoc
class _$RecommendationScoreComponentsDtoCopyWithImpl<$Res>
    implements $RecommendationScoreComponentsDtoCopyWith<$Res> {
  _$RecommendationScoreComponentsDtoCopyWithImpl(this._self, this._then);

  final RecommendationScoreComponentsDto _self;
  final $Res Function(RecommendationScoreComponentsDto) _then;

/// Create a copy of RecommendationScoreComponentsDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? expirationUtilization = null,Object? availability = null,Object? preferenceFit = null,Object? purchaseMinimization = null,}) {
  return _then(_self.copyWith(
expirationUtilization: null == expirationUtilization ? _self.expirationUtilization : expirationUtilization // ignore: cast_nullable_to_non_nullable
as double,availability: null == availability ? _self.availability : availability // ignore: cast_nullable_to_non_nullable
as double,preferenceFit: null == preferenceFit ? _self.preferenceFit : preferenceFit // ignore: cast_nullable_to_non_nullable
as double,purchaseMinimization: null == purchaseMinimization ? _self.purchaseMinimization : purchaseMinimization // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

}


/// Adds pattern-matching-related methods to [RecommendationScoreComponentsDto].
extension RecommendationScoreComponentsDtoPatterns on RecommendationScoreComponentsDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RecommendationScoreComponentsDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RecommendationScoreComponentsDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RecommendationScoreComponentsDto value)  $default,){
final _that = this;
switch (_that) {
case _RecommendationScoreComponentsDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RecommendationScoreComponentsDto value)?  $default,){
final _that = this;
switch (_that) {
case _RecommendationScoreComponentsDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'expiration_utilization', fromJson: _asDoubleDefault)  double expirationUtilization, @JsonKey(fromJson: _asDoubleDefault)  double availability, @JsonKey(name: 'preference_fit', fromJson: _asDoubleDefault)  double preferenceFit, @JsonKey(name: 'purchase_minimization', fromJson: _asDoubleDefault)  double purchaseMinimization)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RecommendationScoreComponentsDto() when $default != null:
return $default(_that.expirationUtilization,_that.availability,_that.preferenceFit,_that.purchaseMinimization);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'expiration_utilization', fromJson: _asDoubleDefault)  double expirationUtilization, @JsonKey(fromJson: _asDoubleDefault)  double availability, @JsonKey(name: 'preference_fit', fromJson: _asDoubleDefault)  double preferenceFit, @JsonKey(name: 'purchase_minimization', fromJson: _asDoubleDefault)  double purchaseMinimization)  $default,) {final _that = this;
switch (_that) {
case _RecommendationScoreComponentsDto():
return $default(_that.expirationUtilization,_that.availability,_that.preferenceFit,_that.purchaseMinimization);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'expiration_utilization', fromJson: _asDoubleDefault)  double expirationUtilization, @JsonKey(fromJson: _asDoubleDefault)  double availability, @JsonKey(name: 'preference_fit', fromJson: _asDoubleDefault)  double preferenceFit, @JsonKey(name: 'purchase_minimization', fromJson: _asDoubleDefault)  double purchaseMinimization)?  $default,) {final _that = this;
switch (_that) {
case _RecommendationScoreComponentsDto() when $default != null:
return $default(_that.expirationUtilization,_that.availability,_that.preferenceFit,_that.purchaseMinimization);case _:
  return null;

}
}

}

/// @nodoc


class _RecommendationScoreComponentsDto extends RecommendationScoreComponentsDto {
  const _RecommendationScoreComponentsDto({@JsonKey(name: 'expiration_utilization', fromJson: _asDoubleDefault) this.expirationUtilization = 0.0, @JsonKey(fromJson: _asDoubleDefault) this.availability = 0.0, @JsonKey(name: 'preference_fit', fromJson: _asDoubleDefault) this.preferenceFit = 0.0, @JsonKey(name: 'purchase_minimization', fromJson: _asDoubleDefault) this.purchaseMinimization = 0.0}): super._();
  

@override@JsonKey(name: 'expiration_utilization', fromJson: _asDoubleDefault) final  double expirationUtilization;
@override@JsonKey(fromJson: _asDoubleDefault) final  double availability;
@override@JsonKey(name: 'preference_fit', fromJson: _asDoubleDefault) final  double preferenceFit;
@override@JsonKey(name: 'purchase_minimization', fromJson: _asDoubleDefault) final  double purchaseMinimization;

/// Create a copy of RecommendationScoreComponentsDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RecommendationScoreComponentsDtoCopyWith<_RecommendationScoreComponentsDto> get copyWith => __$RecommendationScoreComponentsDtoCopyWithImpl<_RecommendationScoreComponentsDto>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RecommendationScoreComponentsDto&&(identical(other.expirationUtilization, expirationUtilization) || other.expirationUtilization == expirationUtilization)&&(identical(other.availability, availability) || other.availability == availability)&&(identical(other.preferenceFit, preferenceFit) || other.preferenceFit == preferenceFit)&&(identical(other.purchaseMinimization, purchaseMinimization) || other.purchaseMinimization == purchaseMinimization));
}


@override
int get hashCode => Object.hash(runtimeType,expirationUtilization,availability,preferenceFit,purchaseMinimization);

@override
String toString() {
  return 'RecommendationScoreComponentsDto(expirationUtilization: $expirationUtilization, availability: $availability, preferenceFit: $preferenceFit, purchaseMinimization: $purchaseMinimization)';
}


}

/// @nodoc
abstract mixin class _$RecommendationScoreComponentsDtoCopyWith<$Res> implements $RecommendationScoreComponentsDtoCopyWith<$Res> {
  factory _$RecommendationScoreComponentsDtoCopyWith(_RecommendationScoreComponentsDto value, $Res Function(_RecommendationScoreComponentsDto) _then) = __$RecommendationScoreComponentsDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'expiration_utilization', fromJson: _asDoubleDefault) double expirationUtilization,@JsonKey(fromJson: _asDoubleDefault) double availability,@JsonKey(name: 'preference_fit', fromJson: _asDoubleDefault) double preferenceFit,@JsonKey(name: 'purchase_minimization', fromJson: _asDoubleDefault) double purchaseMinimization
});




}
/// @nodoc
class __$RecommendationScoreComponentsDtoCopyWithImpl<$Res>
    implements _$RecommendationScoreComponentsDtoCopyWith<$Res> {
  __$RecommendationScoreComponentsDtoCopyWithImpl(this._self, this._then);

  final _RecommendationScoreComponentsDto _self;
  final $Res Function(_RecommendationScoreComponentsDto) _then;

/// Create a copy of RecommendationScoreComponentsDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? expirationUtilization = null,Object? availability = null,Object? preferenceFit = null,Object? purchaseMinimization = null,}) {
  return _then(_RecommendationScoreComponentsDto(
expirationUtilization: null == expirationUtilization ? _self.expirationUtilization : expirationUtilization // ignore: cast_nullable_to_non_nullable
as double,availability: null == availability ? _self.availability : availability // ignore: cast_nullable_to_non_nullable
as double,preferenceFit: null == preferenceFit ? _self.preferenceFit : preferenceFit // ignore: cast_nullable_to_non_nullable
as double,purchaseMinimization: null == purchaseMinimization ? _self.purchaseMinimization : purchaseMinimization // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}


/// @nodoc
mixin _$RecommendationMissingIngredientDto {

@JsonKey(name: 'master_ingredient_id') String? get masterIngredientId; String get name;@JsonKey(fromJson: _asDoubleDefault) double get quantity; String get unit;
/// Create a copy of RecommendationMissingIngredientDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecommendationMissingIngredientDtoCopyWith<RecommendationMissingIngredientDto> get copyWith => _$RecommendationMissingIngredientDtoCopyWithImpl<RecommendationMissingIngredientDto>(this as RecommendationMissingIngredientDto, _$identity);

  /// Serializes this RecommendationMissingIngredientDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RecommendationMissingIngredientDto&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId)&&(identical(other.name, name) || other.name == name)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,masterIngredientId,name,quantity,unit);

@override
String toString() {
  return 'RecommendationMissingIngredientDto(masterIngredientId: $masterIngredientId, name: $name, quantity: $quantity, unit: $unit)';
}


}

/// @nodoc
abstract mixin class $RecommendationMissingIngredientDtoCopyWith<$Res>  {
  factory $RecommendationMissingIngredientDtoCopyWith(RecommendationMissingIngredientDto value, $Res Function(RecommendationMissingIngredientDto) _then) = _$RecommendationMissingIngredientDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'master_ingredient_id') String? masterIngredientId, String name,@JsonKey(fromJson: _asDoubleDefault) double quantity, String unit
});




}
/// @nodoc
class _$RecommendationMissingIngredientDtoCopyWithImpl<$Res>
    implements $RecommendationMissingIngredientDtoCopyWith<$Res> {
  _$RecommendationMissingIngredientDtoCopyWithImpl(this._self, this._then);

  final RecommendationMissingIngredientDto _self;
  final $Res Function(RecommendationMissingIngredientDto) _then;

/// Create a copy of RecommendationMissingIngredientDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? masterIngredientId = freezed,Object? name = null,Object? quantity = null,Object? unit = null,}) {
  return _then(_self.copyWith(
masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [RecommendationMissingIngredientDto].
extension RecommendationMissingIngredientDtoPatterns on RecommendationMissingIngredientDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RecommendationMissingIngredientDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RecommendationMissingIngredientDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RecommendationMissingIngredientDto value)  $default,){
final _that = this;
switch (_that) {
case _RecommendationMissingIngredientDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RecommendationMissingIngredientDto value)?  $default,){
final _that = this;
switch (_that) {
case _RecommendationMissingIngredientDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'master_ingredient_id')  String? masterIngredientId,  String name, @JsonKey(fromJson: _asDoubleDefault)  double quantity,  String unit)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RecommendationMissingIngredientDto() when $default != null:
return $default(_that.masterIngredientId,_that.name,_that.quantity,_that.unit);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'master_ingredient_id')  String? masterIngredientId,  String name, @JsonKey(fromJson: _asDoubleDefault)  double quantity,  String unit)  $default,) {final _that = this;
switch (_that) {
case _RecommendationMissingIngredientDto():
return $default(_that.masterIngredientId,_that.name,_that.quantity,_that.unit);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'master_ingredient_id')  String? masterIngredientId,  String name, @JsonKey(fromJson: _asDoubleDefault)  double quantity,  String unit)?  $default,) {final _that = this;
switch (_that) {
case _RecommendationMissingIngredientDto() when $default != null:
return $default(_that.masterIngredientId,_that.name,_that.quantity,_that.unit);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RecommendationMissingIngredientDto extends RecommendationMissingIngredientDto {
  const _RecommendationMissingIngredientDto({@JsonKey(name: 'master_ingredient_id') this.masterIngredientId, required this.name, @JsonKey(fromJson: _asDoubleDefault) this.quantity = 0.0, this.unit = ''}): super._();
  factory _RecommendationMissingIngredientDto.fromJson(Map<String, dynamic> json) => _$RecommendationMissingIngredientDtoFromJson(json);

@override@JsonKey(name: 'master_ingredient_id') final  String? masterIngredientId;
@override final  String name;
@override@JsonKey(fromJson: _asDoubleDefault) final  double quantity;
@override@JsonKey() final  String unit;

/// Create a copy of RecommendationMissingIngredientDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RecommendationMissingIngredientDtoCopyWith<_RecommendationMissingIngredientDto> get copyWith => __$RecommendationMissingIngredientDtoCopyWithImpl<_RecommendationMissingIngredientDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RecommendationMissingIngredientDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RecommendationMissingIngredientDto&&(identical(other.masterIngredientId, masterIngredientId) || other.masterIngredientId == masterIngredientId)&&(identical(other.name, name) || other.name == name)&&(identical(other.quantity, quantity) || other.quantity == quantity)&&(identical(other.unit, unit) || other.unit == unit));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,masterIngredientId,name,quantity,unit);

@override
String toString() {
  return 'RecommendationMissingIngredientDto(masterIngredientId: $masterIngredientId, name: $name, quantity: $quantity, unit: $unit)';
}


}

/// @nodoc
abstract mixin class _$RecommendationMissingIngredientDtoCopyWith<$Res> implements $RecommendationMissingIngredientDtoCopyWith<$Res> {
  factory _$RecommendationMissingIngredientDtoCopyWith(_RecommendationMissingIngredientDto value, $Res Function(_RecommendationMissingIngredientDto) _then) = __$RecommendationMissingIngredientDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'master_ingredient_id') String? masterIngredientId, String name,@JsonKey(fromJson: _asDoubleDefault) double quantity, String unit
});




}
/// @nodoc
class __$RecommendationMissingIngredientDtoCopyWithImpl<$Res>
    implements _$RecommendationMissingIngredientDtoCopyWith<$Res> {
  __$RecommendationMissingIngredientDtoCopyWithImpl(this._self, this._then);

  final _RecommendationMissingIngredientDto _self;
  final $Res Function(_RecommendationMissingIngredientDto) _then;

/// Create a copy of RecommendationMissingIngredientDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? masterIngredientId = freezed,Object? name = null,Object? quantity = null,Object? unit = null,}) {
  return _then(_RecommendationMissingIngredientDto(
masterIngredientId: freezed == masterIngredientId ? _self.masterIngredientId : masterIngredientId // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,quantity: null == quantity ? _self.quantity : quantity // ignore: cast_nullable_to_non_nullable
as double,unit: null == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc
mixin _$RecommendationItemDto {

@JsonKey(name: 'recipe_id') String get recipeId;@JsonKey(name: 'recipe_name') String get recipeName; int get rank;@JsonKey(fromJson: _asDoubleDefault) double get score;@JsonKey(name: 'score_components') RecommendationScoreComponentsDto get scoreComponents;@JsonKey(name: 'missing_ingredients') List<RecommendationMissingIngredientDto> get missingIngredients;@JsonKey(name: 'near_expiry_ingredients') List<String> get nearExpiryIngredients; String get explanation; String get provider;@JsonKey(name: 'model_version') String get modelVersion;// Optional embedded dish for backward compatibility with legacy fixtures/mocks
 DishDto? get dish;
/// Create a copy of RecommendationItemDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecommendationItemDtoCopyWith<RecommendationItemDto> get copyWith => _$RecommendationItemDtoCopyWithImpl<RecommendationItemDto>(this as RecommendationItemDto, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RecommendationItemDto&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.rank, rank) || other.rank == rank)&&(identical(other.score, score) || other.score == score)&&(identical(other.scoreComponents, scoreComponents) || other.scoreComponents == scoreComponents)&&const DeepCollectionEquality().equals(other.missingIngredients, missingIngredients)&&const DeepCollectionEquality().equals(other.nearExpiryIngredients, nearExpiryIngredients)&&(identical(other.explanation, explanation) || other.explanation == explanation)&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.modelVersion, modelVersion) || other.modelVersion == modelVersion)&&(identical(other.dish, dish) || other.dish == dish));
}


@override
int get hashCode => Object.hash(runtimeType,recipeId,recipeName,rank,score,scoreComponents,const DeepCollectionEquality().hash(missingIngredients),const DeepCollectionEquality().hash(nearExpiryIngredients),explanation,provider,modelVersion,dish);

@override
String toString() {
  return 'RecommendationItemDto(recipeId: $recipeId, recipeName: $recipeName, rank: $rank, score: $score, scoreComponents: $scoreComponents, missingIngredients: $missingIngredients, nearExpiryIngredients: $nearExpiryIngredients, explanation: $explanation, provider: $provider, modelVersion: $modelVersion, dish: $dish)';
}


}

/// @nodoc
abstract mixin class $RecommendationItemDtoCopyWith<$Res>  {
  factory $RecommendationItemDtoCopyWith(RecommendationItemDto value, $Res Function(RecommendationItemDto) _then) = _$RecommendationItemDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName, int rank,@JsonKey(fromJson: _asDoubleDefault) double score,@JsonKey(name: 'score_components') RecommendationScoreComponentsDto scoreComponents,@JsonKey(name: 'missing_ingredients') List<RecommendationMissingIngredientDto> missingIngredients,@JsonKey(name: 'near_expiry_ingredients') List<String> nearExpiryIngredients, String explanation, String provider,@JsonKey(name: 'model_version') String modelVersion, DishDto? dish
});


$RecommendationScoreComponentsDtoCopyWith<$Res> get scoreComponents;$DishDtoCopyWith<$Res>? get dish;

}
/// @nodoc
class _$RecommendationItemDtoCopyWithImpl<$Res>
    implements $RecommendationItemDtoCopyWith<$Res> {
  _$RecommendationItemDtoCopyWithImpl(this._self, this._then);

  final RecommendationItemDto _self;
  final $Res Function(RecommendationItemDto) _then;

/// Create a copy of RecommendationItemDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recipeId = null,Object? recipeName = null,Object? rank = null,Object? score = null,Object? scoreComponents = null,Object? missingIngredients = null,Object? nearExpiryIngredients = null,Object? explanation = null,Object? provider = null,Object? modelVersion = null,Object? dish = freezed,}) {
  return _then(_self.copyWith(
recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,rank: null == rank ? _self.rank : rank // ignore: cast_nullable_to_non_nullable
as int,score: null == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double,scoreComponents: null == scoreComponents ? _self.scoreComponents : scoreComponents // ignore: cast_nullable_to_non_nullable
as RecommendationScoreComponentsDto,missingIngredients: null == missingIngredients ? _self.missingIngredients : missingIngredients // ignore: cast_nullable_to_non_nullable
as List<RecommendationMissingIngredientDto>,nearExpiryIngredients: null == nearExpiryIngredients ? _self.nearExpiryIngredients : nearExpiryIngredients // ignore: cast_nullable_to_non_nullable
as List<String>,explanation: null == explanation ? _self.explanation : explanation // ignore: cast_nullable_to_non_nullable
as String,provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,modelVersion: null == modelVersion ? _self.modelVersion : modelVersion // ignore: cast_nullable_to_non_nullable
as String,dish: freezed == dish ? _self.dish : dish // ignore: cast_nullable_to_non_nullable
as DishDto?,
  ));
}
/// Create a copy of RecommendationItemDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RecommendationScoreComponentsDtoCopyWith<$Res> get scoreComponents {
  
  return $RecommendationScoreComponentsDtoCopyWith<$Res>(_self.scoreComponents, (value) {
    return _then(_self.copyWith(scoreComponents: value));
  });
}/// Create a copy of RecommendationItemDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DishDtoCopyWith<$Res>? get dish {
    if (_self.dish == null) {
    return null;
  }

  return $DishDtoCopyWith<$Res>(_self.dish!, (value) {
    return _then(_self.copyWith(dish: value));
  });
}
}


/// Adds pattern-matching-related methods to [RecommendationItemDto].
extension RecommendationItemDtoPatterns on RecommendationItemDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RecommendationItemDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RecommendationItemDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RecommendationItemDto value)  $default,){
final _that = this;
switch (_that) {
case _RecommendationItemDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RecommendationItemDto value)?  $default,){
final _that = this;
switch (_that) {
case _RecommendationItemDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName,  int rank, @JsonKey(fromJson: _asDoubleDefault)  double score, @JsonKey(name: 'score_components')  RecommendationScoreComponentsDto scoreComponents, @JsonKey(name: 'missing_ingredients')  List<RecommendationMissingIngredientDto> missingIngredients, @JsonKey(name: 'near_expiry_ingredients')  List<String> nearExpiryIngredients,  String explanation,  String provider, @JsonKey(name: 'model_version')  String modelVersion,  DishDto? dish)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RecommendationItemDto() when $default != null:
return $default(_that.recipeId,_that.recipeName,_that.rank,_that.score,_that.scoreComponents,_that.missingIngredients,_that.nearExpiryIngredients,_that.explanation,_that.provider,_that.modelVersion,_that.dish);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName,  int rank, @JsonKey(fromJson: _asDoubleDefault)  double score, @JsonKey(name: 'score_components')  RecommendationScoreComponentsDto scoreComponents, @JsonKey(name: 'missing_ingredients')  List<RecommendationMissingIngredientDto> missingIngredients, @JsonKey(name: 'near_expiry_ingredients')  List<String> nearExpiryIngredients,  String explanation,  String provider, @JsonKey(name: 'model_version')  String modelVersion,  DishDto? dish)  $default,) {final _that = this;
switch (_that) {
case _RecommendationItemDto():
return $default(_that.recipeId,_that.recipeName,_that.rank,_that.score,_that.scoreComponents,_that.missingIngredients,_that.nearExpiryIngredients,_that.explanation,_that.provider,_that.modelVersion,_that.dish);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'recipe_id')  String recipeId, @JsonKey(name: 'recipe_name')  String recipeName,  int rank, @JsonKey(fromJson: _asDoubleDefault)  double score, @JsonKey(name: 'score_components')  RecommendationScoreComponentsDto scoreComponents, @JsonKey(name: 'missing_ingredients')  List<RecommendationMissingIngredientDto> missingIngredients, @JsonKey(name: 'near_expiry_ingredients')  List<String> nearExpiryIngredients,  String explanation,  String provider, @JsonKey(name: 'model_version')  String modelVersion,  DishDto? dish)?  $default,) {final _that = this;
switch (_that) {
case _RecommendationItemDto() when $default != null:
return $default(_that.recipeId,_that.recipeName,_that.rank,_that.score,_that.scoreComponents,_that.missingIngredients,_that.nearExpiryIngredients,_that.explanation,_that.provider,_that.modelVersion,_that.dish);case _:
  return null;

}
}

}

/// @nodoc


class _RecommendationItemDto extends RecommendationItemDto {
  const _RecommendationItemDto({@JsonKey(name: 'recipe_id') required this.recipeId, @JsonKey(name: 'recipe_name') required this.recipeName, this.rank = 1, @JsonKey(fromJson: _asDoubleDefault) this.score = 0.0, @JsonKey(name: 'score_components') this.scoreComponents = const RecommendationScoreComponentsDto(), @JsonKey(name: 'missing_ingredients') final  List<RecommendationMissingIngredientDto> missingIngredients = const <RecommendationMissingIngredientDto>[], @JsonKey(name: 'near_expiry_ingredients') final  List<String> nearExpiryIngredients = const <String>[], this.explanation = '', this.provider = '', @JsonKey(name: 'model_version') this.modelVersion = '', this.dish}): _missingIngredients = missingIngredients,_nearExpiryIngredients = nearExpiryIngredients,super._();
  

@override@JsonKey(name: 'recipe_id') final  String recipeId;
@override@JsonKey(name: 'recipe_name') final  String recipeName;
@override@JsonKey() final  int rank;
@override@JsonKey(fromJson: _asDoubleDefault) final  double score;
@override@JsonKey(name: 'score_components') final  RecommendationScoreComponentsDto scoreComponents;
 final  List<RecommendationMissingIngredientDto> _missingIngredients;
@override@JsonKey(name: 'missing_ingredients') List<RecommendationMissingIngredientDto> get missingIngredients {
  if (_missingIngredients is EqualUnmodifiableListView) return _missingIngredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_missingIngredients);
}

 final  List<String> _nearExpiryIngredients;
@override@JsonKey(name: 'near_expiry_ingredients') List<String> get nearExpiryIngredients {
  if (_nearExpiryIngredients is EqualUnmodifiableListView) return _nearExpiryIngredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_nearExpiryIngredients);
}

@override@JsonKey() final  String explanation;
@override@JsonKey() final  String provider;
@override@JsonKey(name: 'model_version') final  String modelVersion;
// Optional embedded dish for backward compatibility with legacy fixtures/mocks
@override final  DishDto? dish;

/// Create a copy of RecommendationItemDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RecommendationItemDtoCopyWith<_RecommendationItemDto> get copyWith => __$RecommendationItemDtoCopyWithImpl<_RecommendationItemDto>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RecommendationItemDto&&(identical(other.recipeId, recipeId) || other.recipeId == recipeId)&&(identical(other.recipeName, recipeName) || other.recipeName == recipeName)&&(identical(other.rank, rank) || other.rank == rank)&&(identical(other.score, score) || other.score == score)&&(identical(other.scoreComponents, scoreComponents) || other.scoreComponents == scoreComponents)&&const DeepCollectionEquality().equals(other._missingIngredients, _missingIngredients)&&const DeepCollectionEquality().equals(other._nearExpiryIngredients, _nearExpiryIngredients)&&(identical(other.explanation, explanation) || other.explanation == explanation)&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.modelVersion, modelVersion) || other.modelVersion == modelVersion)&&(identical(other.dish, dish) || other.dish == dish));
}


@override
int get hashCode => Object.hash(runtimeType,recipeId,recipeName,rank,score,scoreComponents,const DeepCollectionEquality().hash(_missingIngredients),const DeepCollectionEquality().hash(_nearExpiryIngredients),explanation,provider,modelVersion,dish);

@override
String toString() {
  return 'RecommendationItemDto(recipeId: $recipeId, recipeName: $recipeName, rank: $rank, score: $score, scoreComponents: $scoreComponents, missingIngredients: $missingIngredients, nearExpiryIngredients: $nearExpiryIngredients, explanation: $explanation, provider: $provider, modelVersion: $modelVersion, dish: $dish)';
}


}

/// @nodoc
abstract mixin class _$RecommendationItemDtoCopyWith<$Res> implements $RecommendationItemDtoCopyWith<$Res> {
  factory _$RecommendationItemDtoCopyWith(_RecommendationItemDto value, $Res Function(_RecommendationItemDto) _then) = __$RecommendationItemDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'recipe_id') String recipeId,@JsonKey(name: 'recipe_name') String recipeName, int rank,@JsonKey(fromJson: _asDoubleDefault) double score,@JsonKey(name: 'score_components') RecommendationScoreComponentsDto scoreComponents,@JsonKey(name: 'missing_ingredients') List<RecommendationMissingIngredientDto> missingIngredients,@JsonKey(name: 'near_expiry_ingredients') List<String> nearExpiryIngredients, String explanation, String provider,@JsonKey(name: 'model_version') String modelVersion, DishDto? dish
});


@override $RecommendationScoreComponentsDtoCopyWith<$Res> get scoreComponents;@override $DishDtoCopyWith<$Res>? get dish;

}
/// @nodoc
class __$RecommendationItemDtoCopyWithImpl<$Res>
    implements _$RecommendationItemDtoCopyWith<$Res> {
  __$RecommendationItemDtoCopyWithImpl(this._self, this._then);

  final _RecommendationItemDto _self;
  final $Res Function(_RecommendationItemDto) _then;

/// Create a copy of RecommendationItemDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recipeId = null,Object? recipeName = null,Object? rank = null,Object? score = null,Object? scoreComponents = null,Object? missingIngredients = null,Object? nearExpiryIngredients = null,Object? explanation = null,Object? provider = null,Object? modelVersion = null,Object? dish = freezed,}) {
  return _then(_RecommendationItemDto(
recipeId: null == recipeId ? _self.recipeId : recipeId // ignore: cast_nullable_to_non_nullable
as String,recipeName: null == recipeName ? _self.recipeName : recipeName // ignore: cast_nullable_to_non_nullable
as String,rank: null == rank ? _self.rank : rank // ignore: cast_nullable_to_non_nullable
as int,score: null == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double,scoreComponents: null == scoreComponents ? _self.scoreComponents : scoreComponents // ignore: cast_nullable_to_non_nullable
as RecommendationScoreComponentsDto,missingIngredients: null == missingIngredients ? _self._missingIngredients : missingIngredients // ignore: cast_nullable_to_non_nullable
as List<RecommendationMissingIngredientDto>,nearExpiryIngredients: null == nearExpiryIngredients ? _self._nearExpiryIngredients : nearExpiryIngredients // ignore: cast_nullable_to_non_nullable
as List<String>,explanation: null == explanation ? _self.explanation : explanation // ignore: cast_nullable_to_non_nullable
as String,provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,modelVersion: null == modelVersion ? _self.modelVersion : modelVersion // ignore: cast_nullable_to_non_nullable
as String,dish: freezed == dish ? _self.dish : dish // ignore: cast_nullable_to_non_nullable
as DishDto?,
  ));
}

/// Create a copy of RecommendationItemDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RecommendationScoreComponentsDtoCopyWith<$Res> get scoreComponents {
  
  return $RecommendationScoreComponentsDtoCopyWith<$Res>(_self.scoreComponents, (value) {
    return _then(_self.copyWith(scoreComponents: value));
  });
}/// Create a copy of RecommendationItemDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DishDtoCopyWith<$Res>? get dish {
    if (_self.dish == null) {
    return null;
  }

  return $DishDtoCopyWith<$Res>(_self.dish!, (value) {
    return _then(_self.copyWith(dish: value));
  });
}
}

/// @nodoc
mixin _$RecommendationListResponseDto {

 String get request; MockRecommendationAnalysisDto get analysis; List<RecommendationItemDto> get items;
/// Create a copy of RecommendationListResponseDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecommendationListResponseDtoCopyWith<RecommendationListResponseDto> get copyWith => _$RecommendationListResponseDtoCopyWithImpl<RecommendationListResponseDto>(this as RecommendationListResponseDto, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RecommendationListResponseDto&&(identical(other.request, request) || other.request == request)&&(identical(other.analysis, analysis) || other.analysis == analysis)&&const DeepCollectionEquality().equals(other.items, items));
}


@override
int get hashCode => Object.hash(runtimeType,request,analysis,const DeepCollectionEquality().hash(items));

@override
String toString() {
  return 'RecommendationListResponseDto(request: $request, analysis: $analysis, items: $items)';
}


}

/// @nodoc
abstract mixin class $RecommendationListResponseDtoCopyWith<$Res>  {
  factory $RecommendationListResponseDtoCopyWith(RecommendationListResponseDto value, $Res Function(RecommendationListResponseDto) _then) = _$RecommendationListResponseDtoCopyWithImpl;
@useResult
$Res call({
 String request, MockRecommendationAnalysisDto analysis, List<RecommendationItemDto> items
});


$MockRecommendationAnalysisDtoCopyWith<$Res> get analysis;

}
/// @nodoc
class _$RecommendationListResponseDtoCopyWithImpl<$Res>
    implements $RecommendationListResponseDtoCopyWith<$Res> {
  _$RecommendationListResponseDtoCopyWithImpl(this._self, this._then);

  final RecommendationListResponseDto _self;
  final $Res Function(RecommendationListResponseDto) _then;

/// Create a copy of RecommendationListResponseDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? request = null,Object? analysis = null,Object? items = null,}) {
  return _then(_self.copyWith(
request: null == request ? _self.request : request // ignore: cast_nullable_to_non_nullable
as String,analysis: null == analysis ? _self.analysis : analysis // ignore: cast_nullable_to_non_nullable
as MockRecommendationAnalysisDto,items: null == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<RecommendationItemDto>,
  ));
}
/// Create a copy of RecommendationListResponseDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$MockRecommendationAnalysisDtoCopyWith<$Res> get analysis {
  
  return $MockRecommendationAnalysisDtoCopyWith<$Res>(_self.analysis, (value) {
    return _then(_self.copyWith(analysis: value));
  });
}
}


/// Adds pattern-matching-related methods to [RecommendationListResponseDto].
extension RecommendationListResponseDtoPatterns on RecommendationListResponseDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RecommendationListResponseDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RecommendationListResponseDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RecommendationListResponseDto value)  $default,){
final _that = this;
switch (_that) {
case _RecommendationListResponseDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RecommendationListResponseDto value)?  $default,){
final _that = this;
switch (_that) {
case _RecommendationListResponseDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String request,  MockRecommendationAnalysisDto analysis,  List<RecommendationItemDto> items)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RecommendationListResponseDto() when $default != null:
return $default(_that.request,_that.analysis,_that.items);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String request,  MockRecommendationAnalysisDto analysis,  List<RecommendationItemDto> items)  $default,) {final _that = this;
switch (_that) {
case _RecommendationListResponseDto():
return $default(_that.request,_that.analysis,_that.items);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String request,  MockRecommendationAnalysisDto analysis,  List<RecommendationItemDto> items)?  $default,) {final _that = this;
switch (_that) {
case _RecommendationListResponseDto() when $default != null:
return $default(_that.request,_that.analysis,_that.items);case _:
  return null;

}
}

}

/// @nodoc


class _RecommendationListResponseDto extends RecommendationListResponseDto {
  const _RecommendationListResponseDto({this.request = '', this.analysis = const MockRecommendationAnalysisDto(), final  List<RecommendationItemDto> items = const <RecommendationItemDto>[]}): _items = items,super._();
  

@override@JsonKey() final  String request;
@override@JsonKey() final  MockRecommendationAnalysisDto analysis;
 final  List<RecommendationItemDto> _items;
@override@JsonKey() List<RecommendationItemDto> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


/// Create a copy of RecommendationListResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RecommendationListResponseDtoCopyWith<_RecommendationListResponseDto> get copyWith => __$RecommendationListResponseDtoCopyWithImpl<_RecommendationListResponseDto>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RecommendationListResponseDto&&(identical(other.request, request) || other.request == request)&&(identical(other.analysis, analysis) || other.analysis == analysis)&&const DeepCollectionEquality().equals(other._items, _items));
}


@override
int get hashCode => Object.hash(runtimeType,request,analysis,const DeepCollectionEquality().hash(_items));

@override
String toString() {
  return 'RecommendationListResponseDto(request: $request, analysis: $analysis, items: $items)';
}


}

/// @nodoc
abstract mixin class _$RecommendationListResponseDtoCopyWith<$Res> implements $RecommendationListResponseDtoCopyWith<$Res> {
  factory _$RecommendationListResponseDtoCopyWith(_RecommendationListResponseDto value, $Res Function(_RecommendationListResponseDto) _then) = __$RecommendationListResponseDtoCopyWithImpl;
@override @useResult
$Res call({
 String request, MockRecommendationAnalysisDto analysis, List<RecommendationItemDto> items
});


@override $MockRecommendationAnalysisDtoCopyWith<$Res> get analysis;

}
/// @nodoc
class __$RecommendationListResponseDtoCopyWithImpl<$Res>
    implements _$RecommendationListResponseDtoCopyWith<$Res> {
  __$RecommendationListResponseDtoCopyWithImpl(this._self, this._then);

  final _RecommendationListResponseDto _self;
  final $Res Function(_RecommendationListResponseDto) _then;

/// Create a copy of RecommendationListResponseDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? request = null,Object? analysis = null,Object? items = null,}) {
  return _then(_RecommendationListResponseDto(
request: null == request ? _self.request : request // ignore: cast_nullable_to_non_nullable
as String,analysis: null == analysis ? _self.analysis : analysis // ignore: cast_nullable_to_non_nullable
as MockRecommendationAnalysisDto,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<RecommendationItemDto>,
  ));
}

/// Create a copy of RecommendationListResponseDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$MockRecommendationAnalysisDtoCopyWith<$Res> get analysis {
  
  return $MockRecommendationAnalysisDtoCopyWith<$Res>(_self.analysis, (value) {
    return _then(_self.copyWith(analysis: value));
  });
}
}

// dart format on
