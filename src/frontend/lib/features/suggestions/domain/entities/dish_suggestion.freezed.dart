// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'dish_suggestion.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$DishSuggestion {

 Dish get dish; ScoreBreakdown get breakdown;/// Stable position returned by the AI service after feasibility re-ranking.
 int get rank;/// Raw LightGBM score. This is intentionally not presented as a percent.
 double get rankScore; RecommendationRankingFeatures get rankingFeatures; List<RecommendationIngredient> get matchedIngredients; List<RecommendationIngredient> get missingIngredients; List<RecommendationIngredient> get optionalIngredients; String get statusBadge; String get provider; String get modelVersion; String get rankerModel; double get totalLatencyMs;/// Names of near-expiry pantry ingredients this dish would use.
 List<String> get nearExpiryIngredients;/// Share of the dish's ingredients already in the pantry (`0..1`).
 double get availabilityRatio;/// How many ingredients still need buying.
 int get toBuyCount;/// Server-provided score override; falls back to [breakdown.scoreOutOf100].
 int? get scoreOverride;/// Human-readable explanation from recommendation engine / mock provider.
 String? get explanation;/// True if the score and ranking are from a mock provider (`analysis.is_mock`).
 bool get isMock;
/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DishSuggestionCopyWith<DishSuggestion> get copyWith => _$DishSuggestionCopyWithImpl<DishSuggestion>(this as DishSuggestion, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DishSuggestion&&(identical(other.dish, dish) || other.dish == dish)&&(identical(other.breakdown, breakdown) || other.breakdown == breakdown)&&(identical(other.rank, rank) || other.rank == rank)&&(identical(other.rankScore, rankScore) || other.rankScore == rankScore)&&(identical(other.rankingFeatures, rankingFeatures) || other.rankingFeatures == rankingFeatures)&&const DeepCollectionEquality().equals(other.matchedIngredients, matchedIngredients)&&const DeepCollectionEquality().equals(other.missingIngredients, missingIngredients)&&const DeepCollectionEquality().equals(other.optionalIngredients, optionalIngredients)&&(identical(other.statusBadge, statusBadge) || other.statusBadge == statusBadge)&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.modelVersion, modelVersion) || other.modelVersion == modelVersion)&&(identical(other.rankerModel, rankerModel) || other.rankerModel == rankerModel)&&(identical(other.totalLatencyMs, totalLatencyMs) || other.totalLatencyMs == totalLatencyMs)&&const DeepCollectionEquality().equals(other.nearExpiryIngredients, nearExpiryIngredients)&&(identical(other.availabilityRatio, availabilityRatio) || other.availabilityRatio == availabilityRatio)&&(identical(other.toBuyCount, toBuyCount) || other.toBuyCount == toBuyCount)&&(identical(other.scoreOverride, scoreOverride) || other.scoreOverride == scoreOverride)&&(identical(other.explanation, explanation) || other.explanation == explanation)&&(identical(other.isMock, isMock) || other.isMock == isMock));
}


@override
int get hashCode => Object.hashAll([runtimeType,dish,breakdown,rank,rankScore,rankingFeatures,const DeepCollectionEquality().hash(matchedIngredients),const DeepCollectionEquality().hash(missingIngredients),const DeepCollectionEquality().hash(optionalIngredients),statusBadge,provider,modelVersion,rankerModel,totalLatencyMs,const DeepCollectionEquality().hash(nearExpiryIngredients),availabilityRatio,toBuyCount,scoreOverride,explanation,isMock]);

@override
String toString() {
  return 'DishSuggestion(dish: $dish, breakdown: $breakdown, rank: $rank, rankScore: $rankScore, rankingFeatures: $rankingFeatures, matchedIngredients: $matchedIngredients, missingIngredients: $missingIngredients, optionalIngredients: $optionalIngredients, statusBadge: $statusBadge, provider: $provider, modelVersion: $modelVersion, rankerModel: $rankerModel, totalLatencyMs: $totalLatencyMs, nearExpiryIngredients: $nearExpiryIngredients, availabilityRatio: $availabilityRatio, toBuyCount: $toBuyCount, scoreOverride: $scoreOverride, explanation: $explanation, isMock: $isMock)';
}


}

/// @nodoc
abstract mixin class $DishSuggestionCopyWith<$Res>  {
  factory $DishSuggestionCopyWith(DishSuggestion value, $Res Function(DishSuggestion) _then) = _$DishSuggestionCopyWithImpl;
@useResult
$Res call({
 Dish dish, ScoreBreakdown breakdown, int rank, double rankScore, RecommendationRankingFeatures rankingFeatures, List<RecommendationIngredient> matchedIngredients, List<RecommendationIngredient> missingIngredients, List<RecommendationIngredient> optionalIngredients, String statusBadge, String provider, String modelVersion, String rankerModel, double totalLatencyMs, List<String> nearExpiryIngredients, double availabilityRatio, int toBuyCount, int? scoreOverride, String? explanation, bool isMock
});


$DishCopyWith<$Res> get dish;$ScoreBreakdownCopyWith<$Res> get breakdown;

}
/// @nodoc
class _$DishSuggestionCopyWithImpl<$Res>
    implements $DishSuggestionCopyWith<$Res> {
  _$DishSuggestionCopyWithImpl(this._self, this._then);

  final DishSuggestion _self;
  final $Res Function(DishSuggestion) _then;

/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? dish = null,Object? breakdown = null,Object? rank = null,Object? rankScore = null,Object? rankingFeatures = null,Object? matchedIngredients = null,Object? missingIngredients = null,Object? optionalIngredients = null,Object? statusBadge = null,Object? provider = null,Object? modelVersion = null,Object? rankerModel = null,Object? totalLatencyMs = null,Object? nearExpiryIngredients = null,Object? availabilityRatio = null,Object? toBuyCount = null,Object? scoreOverride = freezed,Object? explanation = freezed,Object? isMock = null,}) {
  return _then(_self.copyWith(
dish: null == dish ? _self.dish : dish // ignore: cast_nullable_to_non_nullable
as Dish,breakdown: null == breakdown ? _self.breakdown : breakdown // ignore: cast_nullable_to_non_nullable
as ScoreBreakdown,rank: null == rank ? _self.rank : rank // ignore: cast_nullable_to_non_nullable
as int,rankScore: null == rankScore ? _self.rankScore : rankScore // ignore: cast_nullable_to_non_nullable
as double,rankingFeatures: null == rankingFeatures ? _self.rankingFeatures : rankingFeatures // ignore: cast_nullable_to_non_nullable
as RecommendationRankingFeatures,matchedIngredients: null == matchedIngredients ? _self.matchedIngredients : matchedIngredients // ignore: cast_nullable_to_non_nullable
as List<RecommendationIngredient>,missingIngredients: null == missingIngredients ? _self.missingIngredients : missingIngredients // ignore: cast_nullable_to_non_nullable
as List<RecommendationIngredient>,optionalIngredients: null == optionalIngredients ? _self.optionalIngredients : optionalIngredients // ignore: cast_nullable_to_non_nullable
as List<RecommendationIngredient>,statusBadge: null == statusBadge ? _self.statusBadge : statusBadge // ignore: cast_nullable_to_non_nullable
as String,provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,modelVersion: null == modelVersion ? _self.modelVersion : modelVersion // ignore: cast_nullable_to_non_nullable
as String,rankerModel: null == rankerModel ? _self.rankerModel : rankerModel // ignore: cast_nullable_to_non_nullable
as String,totalLatencyMs: null == totalLatencyMs ? _self.totalLatencyMs : totalLatencyMs // ignore: cast_nullable_to_non_nullable
as double,nearExpiryIngredients: null == nearExpiryIngredients ? _self.nearExpiryIngredients : nearExpiryIngredients // ignore: cast_nullable_to_non_nullable
as List<String>,availabilityRatio: null == availabilityRatio ? _self.availabilityRatio : availabilityRatio // ignore: cast_nullable_to_non_nullable
as double,toBuyCount: null == toBuyCount ? _self.toBuyCount : toBuyCount // ignore: cast_nullable_to_non_nullable
as int,scoreOverride: freezed == scoreOverride ? _self.scoreOverride : scoreOverride // ignore: cast_nullable_to_non_nullable
as int?,explanation: freezed == explanation ? _self.explanation : explanation // ignore: cast_nullable_to_non_nullable
as String?,isMock: null == isMock ? _self.isMock : isMock // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}
/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DishCopyWith<$Res> get dish {
  
  return $DishCopyWith<$Res>(_self.dish, (value) {
    return _then(_self.copyWith(dish: value));
  });
}/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ScoreBreakdownCopyWith<$Res> get breakdown {
  
  return $ScoreBreakdownCopyWith<$Res>(_self.breakdown, (value) {
    return _then(_self.copyWith(breakdown: value));
  });
}
}


/// Adds pattern-matching-related methods to [DishSuggestion].
extension DishSuggestionPatterns on DishSuggestion {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DishSuggestion value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DishSuggestion() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DishSuggestion value)  $default,){
final _that = this;
switch (_that) {
case _DishSuggestion():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DishSuggestion value)?  $default,){
final _that = this;
switch (_that) {
case _DishSuggestion() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( Dish dish,  ScoreBreakdown breakdown,  int rank,  double rankScore,  RecommendationRankingFeatures rankingFeatures,  List<RecommendationIngredient> matchedIngredients,  List<RecommendationIngredient> missingIngredients,  List<RecommendationIngredient> optionalIngredients,  String statusBadge,  String provider,  String modelVersion,  String rankerModel,  double totalLatencyMs,  List<String> nearExpiryIngredients,  double availabilityRatio,  int toBuyCount,  int? scoreOverride,  String? explanation,  bool isMock)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DishSuggestion() when $default != null:
return $default(_that.dish,_that.breakdown,_that.rank,_that.rankScore,_that.rankingFeatures,_that.matchedIngredients,_that.missingIngredients,_that.optionalIngredients,_that.statusBadge,_that.provider,_that.modelVersion,_that.rankerModel,_that.totalLatencyMs,_that.nearExpiryIngredients,_that.availabilityRatio,_that.toBuyCount,_that.scoreOverride,_that.explanation,_that.isMock);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( Dish dish,  ScoreBreakdown breakdown,  int rank,  double rankScore,  RecommendationRankingFeatures rankingFeatures,  List<RecommendationIngredient> matchedIngredients,  List<RecommendationIngredient> missingIngredients,  List<RecommendationIngredient> optionalIngredients,  String statusBadge,  String provider,  String modelVersion,  String rankerModel,  double totalLatencyMs,  List<String> nearExpiryIngredients,  double availabilityRatio,  int toBuyCount,  int? scoreOverride,  String? explanation,  bool isMock)  $default,) {final _that = this;
switch (_that) {
case _DishSuggestion():
return $default(_that.dish,_that.breakdown,_that.rank,_that.rankScore,_that.rankingFeatures,_that.matchedIngredients,_that.missingIngredients,_that.optionalIngredients,_that.statusBadge,_that.provider,_that.modelVersion,_that.rankerModel,_that.totalLatencyMs,_that.nearExpiryIngredients,_that.availabilityRatio,_that.toBuyCount,_that.scoreOverride,_that.explanation,_that.isMock);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( Dish dish,  ScoreBreakdown breakdown,  int rank,  double rankScore,  RecommendationRankingFeatures rankingFeatures,  List<RecommendationIngredient> matchedIngredients,  List<RecommendationIngredient> missingIngredients,  List<RecommendationIngredient> optionalIngredients,  String statusBadge,  String provider,  String modelVersion,  String rankerModel,  double totalLatencyMs,  List<String> nearExpiryIngredients,  double availabilityRatio,  int toBuyCount,  int? scoreOverride,  String? explanation,  bool isMock)?  $default,) {final _that = this;
switch (_that) {
case _DishSuggestion() when $default != null:
return $default(_that.dish,_that.breakdown,_that.rank,_that.rankScore,_that.rankingFeatures,_that.matchedIngredients,_that.missingIngredients,_that.optionalIngredients,_that.statusBadge,_that.provider,_that.modelVersion,_that.rankerModel,_that.totalLatencyMs,_that.nearExpiryIngredients,_that.availabilityRatio,_that.toBuyCount,_that.scoreOverride,_that.explanation,_that.isMock);case _:
  return null;

}
}

}

/// @nodoc


class _DishSuggestion extends DishSuggestion {
  const _DishSuggestion({required this.dish, required this.breakdown, this.rank = 1, this.rankScore = 0, this.rankingFeatures = const RecommendationRankingFeatures(), final  List<RecommendationIngredient> matchedIngredients = const <RecommendationIngredient>[], final  List<RecommendationIngredient> missingIngredients = const <RecommendationIngredient>[], final  List<RecommendationIngredient> optionalIngredients = const <RecommendationIngredient>[], this.statusBadge = '', this.provider = '', this.modelVersion = '', this.rankerModel = '', this.totalLatencyMs = 0, final  List<String> nearExpiryIngredients = const <String>[], this.availabilityRatio = 0, this.toBuyCount = 0, this.scoreOverride, this.explanation, this.isMock = false}): _matchedIngredients = matchedIngredients,_missingIngredients = missingIngredients,_optionalIngredients = optionalIngredients,_nearExpiryIngredients = nearExpiryIngredients,super._();
  

@override final  Dish dish;
@override final  ScoreBreakdown breakdown;
/// Stable position returned by the AI service after feasibility re-ranking.
@override@JsonKey() final  int rank;
/// Raw LightGBM score. This is intentionally not presented as a percent.
@override@JsonKey() final  double rankScore;
@override@JsonKey() final  RecommendationRankingFeatures rankingFeatures;
 final  List<RecommendationIngredient> _matchedIngredients;
@override@JsonKey() List<RecommendationIngredient> get matchedIngredients {
  if (_matchedIngredients is EqualUnmodifiableListView) return _matchedIngredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_matchedIngredients);
}

 final  List<RecommendationIngredient> _missingIngredients;
@override@JsonKey() List<RecommendationIngredient> get missingIngredients {
  if (_missingIngredients is EqualUnmodifiableListView) return _missingIngredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_missingIngredients);
}

 final  List<RecommendationIngredient> _optionalIngredients;
@override@JsonKey() List<RecommendationIngredient> get optionalIngredients {
  if (_optionalIngredients is EqualUnmodifiableListView) return _optionalIngredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_optionalIngredients);
}

@override@JsonKey() final  String statusBadge;
@override@JsonKey() final  String provider;
@override@JsonKey() final  String modelVersion;
@override@JsonKey() final  String rankerModel;
@override@JsonKey() final  double totalLatencyMs;
/// Names of near-expiry pantry ingredients this dish would use.
 final  List<String> _nearExpiryIngredients;
/// Names of near-expiry pantry ingredients this dish would use.
@override@JsonKey() List<String> get nearExpiryIngredients {
  if (_nearExpiryIngredients is EqualUnmodifiableListView) return _nearExpiryIngredients;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_nearExpiryIngredients);
}

/// Share of the dish's ingredients already in the pantry (`0..1`).
@override@JsonKey() final  double availabilityRatio;
/// How many ingredients still need buying.
@override@JsonKey() final  int toBuyCount;
/// Server-provided score override; falls back to [breakdown.scoreOutOf100].
@override final  int? scoreOverride;
/// Human-readable explanation from recommendation engine / mock provider.
@override final  String? explanation;
/// True if the score and ranking are from a mock provider (`analysis.is_mock`).
@override@JsonKey() final  bool isMock;

/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DishSuggestionCopyWith<_DishSuggestion> get copyWith => __$DishSuggestionCopyWithImpl<_DishSuggestion>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DishSuggestion&&(identical(other.dish, dish) || other.dish == dish)&&(identical(other.breakdown, breakdown) || other.breakdown == breakdown)&&(identical(other.rank, rank) || other.rank == rank)&&(identical(other.rankScore, rankScore) || other.rankScore == rankScore)&&(identical(other.rankingFeatures, rankingFeatures) || other.rankingFeatures == rankingFeatures)&&const DeepCollectionEquality().equals(other._matchedIngredients, _matchedIngredients)&&const DeepCollectionEquality().equals(other._missingIngredients, _missingIngredients)&&const DeepCollectionEquality().equals(other._optionalIngredients, _optionalIngredients)&&(identical(other.statusBadge, statusBadge) || other.statusBadge == statusBadge)&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.modelVersion, modelVersion) || other.modelVersion == modelVersion)&&(identical(other.rankerModel, rankerModel) || other.rankerModel == rankerModel)&&(identical(other.totalLatencyMs, totalLatencyMs) || other.totalLatencyMs == totalLatencyMs)&&const DeepCollectionEquality().equals(other._nearExpiryIngredients, _nearExpiryIngredients)&&(identical(other.availabilityRatio, availabilityRatio) || other.availabilityRatio == availabilityRatio)&&(identical(other.toBuyCount, toBuyCount) || other.toBuyCount == toBuyCount)&&(identical(other.scoreOverride, scoreOverride) || other.scoreOverride == scoreOverride)&&(identical(other.explanation, explanation) || other.explanation == explanation)&&(identical(other.isMock, isMock) || other.isMock == isMock));
}


@override
int get hashCode => Object.hashAll([runtimeType,dish,breakdown,rank,rankScore,rankingFeatures,const DeepCollectionEquality().hash(_matchedIngredients),const DeepCollectionEquality().hash(_missingIngredients),const DeepCollectionEquality().hash(_optionalIngredients),statusBadge,provider,modelVersion,rankerModel,totalLatencyMs,const DeepCollectionEquality().hash(_nearExpiryIngredients),availabilityRatio,toBuyCount,scoreOverride,explanation,isMock]);

@override
String toString() {
  return 'DishSuggestion(dish: $dish, breakdown: $breakdown, rank: $rank, rankScore: $rankScore, rankingFeatures: $rankingFeatures, matchedIngredients: $matchedIngredients, missingIngredients: $missingIngredients, optionalIngredients: $optionalIngredients, statusBadge: $statusBadge, provider: $provider, modelVersion: $modelVersion, rankerModel: $rankerModel, totalLatencyMs: $totalLatencyMs, nearExpiryIngredients: $nearExpiryIngredients, availabilityRatio: $availabilityRatio, toBuyCount: $toBuyCount, scoreOverride: $scoreOverride, explanation: $explanation, isMock: $isMock)';
}


}

/// @nodoc
abstract mixin class _$DishSuggestionCopyWith<$Res> implements $DishSuggestionCopyWith<$Res> {
  factory _$DishSuggestionCopyWith(_DishSuggestion value, $Res Function(_DishSuggestion) _then) = __$DishSuggestionCopyWithImpl;
@override @useResult
$Res call({
 Dish dish, ScoreBreakdown breakdown, int rank, double rankScore, RecommendationRankingFeatures rankingFeatures, List<RecommendationIngredient> matchedIngredients, List<RecommendationIngredient> missingIngredients, List<RecommendationIngredient> optionalIngredients, String statusBadge, String provider, String modelVersion, String rankerModel, double totalLatencyMs, List<String> nearExpiryIngredients, double availabilityRatio, int toBuyCount, int? scoreOverride, String? explanation, bool isMock
});


@override $DishCopyWith<$Res> get dish;@override $ScoreBreakdownCopyWith<$Res> get breakdown;

}
/// @nodoc
class __$DishSuggestionCopyWithImpl<$Res>
    implements _$DishSuggestionCopyWith<$Res> {
  __$DishSuggestionCopyWithImpl(this._self, this._then);

  final _DishSuggestion _self;
  final $Res Function(_DishSuggestion) _then;

/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? dish = null,Object? breakdown = null,Object? rank = null,Object? rankScore = null,Object? rankingFeatures = null,Object? matchedIngredients = null,Object? missingIngredients = null,Object? optionalIngredients = null,Object? statusBadge = null,Object? provider = null,Object? modelVersion = null,Object? rankerModel = null,Object? totalLatencyMs = null,Object? nearExpiryIngredients = null,Object? availabilityRatio = null,Object? toBuyCount = null,Object? scoreOverride = freezed,Object? explanation = freezed,Object? isMock = null,}) {
  return _then(_DishSuggestion(
dish: null == dish ? _self.dish : dish // ignore: cast_nullable_to_non_nullable
as Dish,breakdown: null == breakdown ? _self.breakdown : breakdown // ignore: cast_nullable_to_non_nullable
as ScoreBreakdown,rank: null == rank ? _self.rank : rank // ignore: cast_nullable_to_non_nullable
as int,rankScore: null == rankScore ? _self.rankScore : rankScore // ignore: cast_nullable_to_non_nullable
as double,rankingFeatures: null == rankingFeatures ? _self.rankingFeatures : rankingFeatures // ignore: cast_nullable_to_non_nullable
as RecommendationRankingFeatures,matchedIngredients: null == matchedIngredients ? _self._matchedIngredients : matchedIngredients // ignore: cast_nullable_to_non_nullable
as List<RecommendationIngredient>,missingIngredients: null == missingIngredients ? _self._missingIngredients : missingIngredients // ignore: cast_nullable_to_non_nullable
as List<RecommendationIngredient>,optionalIngredients: null == optionalIngredients ? _self._optionalIngredients : optionalIngredients // ignore: cast_nullable_to_non_nullable
as List<RecommendationIngredient>,statusBadge: null == statusBadge ? _self.statusBadge : statusBadge // ignore: cast_nullable_to_non_nullable
as String,provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,modelVersion: null == modelVersion ? _self.modelVersion : modelVersion // ignore: cast_nullable_to_non_nullable
as String,rankerModel: null == rankerModel ? _self.rankerModel : rankerModel // ignore: cast_nullable_to_non_nullable
as String,totalLatencyMs: null == totalLatencyMs ? _self.totalLatencyMs : totalLatencyMs // ignore: cast_nullable_to_non_nullable
as double,nearExpiryIngredients: null == nearExpiryIngredients ? _self._nearExpiryIngredients : nearExpiryIngredients // ignore: cast_nullable_to_non_nullable
as List<String>,availabilityRatio: null == availabilityRatio ? _self.availabilityRatio : availabilityRatio // ignore: cast_nullable_to_non_nullable
as double,toBuyCount: null == toBuyCount ? _self.toBuyCount : toBuyCount // ignore: cast_nullable_to_non_nullable
as int,scoreOverride: freezed == scoreOverride ? _self.scoreOverride : scoreOverride // ignore: cast_nullable_to_non_nullable
as int?,explanation: freezed == explanation ? _self.explanation : explanation // ignore: cast_nullable_to_non_nullable
as String?,isMock: null == isMock ? _self.isMock : isMock // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DishCopyWith<$Res> get dish {
  
  return $DishCopyWith<$Res>(_self.dish, (value) {
    return _then(_self.copyWith(dish: value));
  });
}/// Create a copy of DishSuggestion
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ScoreBreakdownCopyWith<$Res> get breakdown {
  
  return $ScoreBreakdownCopyWith<$Res>(_self.breakdown, (value) {
    return _then(_self.copyWith(breakdown: value));
  });
}
}

// dart format on
