// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'report_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$WasteBarDto {
  String get label;
  int get value;

  /// Create a copy of WasteBarDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $WasteBarDtoCopyWith<WasteBarDto> get copyWith =>
      _$WasteBarDtoCopyWithImpl<WasteBarDto>(this as WasteBarDto, _$identity);

  /// Serializes this WasteBarDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is WasteBarDto &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.value, value) || other.value == value));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, label, value);

  @override
  String toString() {
    return 'WasteBarDto(label: $label, value: $value)';
  }
}

/// @nodoc
abstract mixin class $WasteBarDtoCopyWith<$Res> {
  factory $WasteBarDtoCopyWith(
          WasteBarDto value, $Res Function(WasteBarDto) _then) =
      _$WasteBarDtoCopyWithImpl;
  @useResult
  $Res call({String label, int value});
}

/// @nodoc
class _$WasteBarDtoCopyWithImpl<$Res> implements $WasteBarDtoCopyWith<$Res> {
  _$WasteBarDtoCopyWithImpl(this._self, this._then);

  final WasteBarDto _self;
  final $Res Function(WasteBarDto) _then;

  /// Create a copy of WasteBarDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? label = null,
    Object? value = null,
  }) {
    return _then(_self.copyWith(
      label: null == label
          ? _self.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      value: null == value
          ? _self.value
          : value // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// Adds pattern-matching-related methods to [WasteBarDto].
extension WasteBarDtoPatterns on WasteBarDto {
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

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>(
    TResult Function(_WasteBarDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _WasteBarDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult map<TResult extends Object?>(
    TResult Function(_WasteBarDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteBarDto():
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>(
    TResult? Function(_WasteBarDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteBarDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>(
    TResult Function(String label, int value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _WasteBarDto() when $default != null:
        return $default(_that.label, _that.value);
      case _:
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

  @optionalTypeArgs
  TResult when<TResult extends Object?>(
    TResult Function(String label, int value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteBarDto():
        return $default(_that.label, _that.value);
      case _:
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

  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>(
    TResult? Function(String label, int value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteBarDto() when $default != null:
        return $default(_that.label, _that.value);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _WasteBarDto implements WasteBarDto {
  const _WasteBarDto({required this.label, required this.value});
  factory _WasteBarDto.fromJson(Map<String, dynamic> json) =>
      _$WasteBarDtoFromJson(json);

  @override
  final String label;
  @override
  final int value;

  /// Create a copy of WasteBarDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$WasteBarDtoCopyWith<_WasteBarDto> get copyWith =>
      __$WasteBarDtoCopyWithImpl<_WasteBarDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$WasteBarDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _WasteBarDto &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.value, value) || other.value == value));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, label, value);

  @override
  String toString() {
    return 'WasteBarDto(label: $label, value: $value)';
  }
}

/// @nodoc
abstract mixin class _$WasteBarDtoCopyWith<$Res>
    implements $WasteBarDtoCopyWith<$Res> {
  factory _$WasteBarDtoCopyWith(
          _WasteBarDto value, $Res Function(_WasteBarDto) _then) =
      __$WasteBarDtoCopyWithImpl;
  @override
  @useResult
  $Res call({String label, int value});
}

/// @nodoc
class __$WasteBarDtoCopyWithImpl<$Res> implements _$WasteBarDtoCopyWith<$Res> {
  __$WasteBarDtoCopyWithImpl(this._self, this._then);

  final _WasteBarDto _self;
  final $Res Function(_WasteBarDto) _then;

  /// Create a copy of WasteBarDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? label = null,
    Object? value = null,
  }) {
    return _then(_WasteBarDto(
      label: null == label
          ? _self.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      value: null == value
          ? _self.value
          : value // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
mixin _$WasteCategoryDto {
  String get category;
  int get count;

  /// Create a copy of WasteCategoryDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $WasteCategoryDtoCopyWith<WasteCategoryDto> get copyWith =>
      _$WasteCategoryDtoCopyWithImpl<WasteCategoryDto>(
          this as WasteCategoryDto, _$identity);

  /// Serializes this WasteCategoryDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is WasteCategoryDto &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.count, count) || other.count == count));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, category, count);

  @override
  String toString() {
    return 'WasteCategoryDto(category: $category, count: $count)';
  }
}

/// @nodoc
abstract mixin class $WasteCategoryDtoCopyWith<$Res> {
  factory $WasteCategoryDtoCopyWith(
          WasteCategoryDto value, $Res Function(WasteCategoryDto) _then) =
      _$WasteCategoryDtoCopyWithImpl;
  @useResult
  $Res call({String category, int count});
}

/// @nodoc
class _$WasteCategoryDtoCopyWithImpl<$Res>
    implements $WasteCategoryDtoCopyWith<$Res> {
  _$WasteCategoryDtoCopyWithImpl(this._self, this._then);

  final WasteCategoryDto _self;
  final $Res Function(WasteCategoryDto) _then;

  /// Create a copy of WasteCategoryDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? category = null,
    Object? count = null,
  }) {
    return _then(_self.copyWith(
      category: null == category
          ? _self.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      count: null == count
          ? _self.count
          : count // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// Adds pattern-matching-related methods to [WasteCategoryDto].
extension WasteCategoryDtoPatterns on WasteCategoryDto {
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

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>(
    TResult Function(_WasteCategoryDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _WasteCategoryDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult map<TResult extends Object?>(
    TResult Function(_WasteCategoryDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteCategoryDto():
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>(
    TResult? Function(_WasteCategoryDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteCategoryDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>(
    TResult Function(String category, int count)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _WasteCategoryDto() when $default != null:
        return $default(_that.category, _that.count);
      case _:
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

  @optionalTypeArgs
  TResult when<TResult extends Object?>(
    TResult Function(String category, int count) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteCategoryDto():
        return $default(_that.category, _that.count);
      case _:
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

  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>(
    TResult? Function(String category, int count)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteCategoryDto() when $default != null:
        return $default(_that.category, _that.count);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _WasteCategoryDto implements WasteCategoryDto {
  const _WasteCategoryDto({required this.category, required this.count});
  factory _WasteCategoryDto.fromJson(Map<String, dynamic> json) =>
      _$WasteCategoryDtoFromJson(json);

  @override
  final String category;
  @override
  final int count;

  /// Create a copy of WasteCategoryDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$WasteCategoryDtoCopyWith<_WasteCategoryDto> get copyWith =>
      __$WasteCategoryDtoCopyWithImpl<_WasteCategoryDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$WasteCategoryDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _WasteCategoryDto &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.count, count) || other.count == count));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, category, count);

  @override
  String toString() {
    return 'WasteCategoryDto(category: $category, count: $count)';
  }
}

/// @nodoc
abstract mixin class _$WasteCategoryDtoCopyWith<$Res>
    implements $WasteCategoryDtoCopyWith<$Res> {
  factory _$WasteCategoryDtoCopyWith(
          _WasteCategoryDto value, $Res Function(_WasteCategoryDto) _then) =
      __$WasteCategoryDtoCopyWithImpl;
  @override
  @useResult
  $Res call({String category, int count});
}

/// @nodoc
class __$WasteCategoryDtoCopyWithImpl<$Res>
    implements _$WasteCategoryDtoCopyWith<$Res> {
  __$WasteCategoryDtoCopyWithImpl(this._self, this._then);

  final _WasteCategoryDto _self;
  final $Res Function(_WasteCategoryDto) _then;

  /// Create a copy of WasteCategoryDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? category = null,
    Object? count = null,
  }) {
    return _then(_WasteCategoryDto(
      category: null == category
          ? _self.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      count: null == count
          ? _self.count
          : count // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
mixin _$WasteReductionSummaryDto {
  String get period;
  @JsonKey(name: 'period_label')
  String get periodLabel;
  @JsonKey(name: 'items_used_before_expiry')
  int get itemsUsedBeforeExpiry;
  @JsonKey(name: 'waste_avoided_kg')
  double get wasteAvoidedKg;
  @JsonKey(name: 'dishes_cooked')
  int get dishesCooked;
  @JsonKey(name: 'weekly_bars')
  List<WasteBarDto> get weeklyBars;
  @JsonKey(name: 'by_category')
  List<WasteCategoryDto> get byCategory;

  /// Create a copy of WasteReductionSummaryDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $WasteReductionSummaryDtoCopyWith<WasteReductionSummaryDto> get copyWith =>
      _$WasteReductionSummaryDtoCopyWithImpl<WasteReductionSummaryDto>(
          this as WasteReductionSummaryDto, _$identity);

  /// Serializes this WasteReductionSummaryDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is WasteReductionSummaryDto &&
            (identical(other.period, period) || other.period == period) &&
            (identical(other.periodLabel, periodLabel) ||
                other.periodLabel == periodLabel) &&
            (identical(other.itemsUsedBeforeExpiry, itemsUsedBeforeExpiry) ||
                other.itemsUsedBeforeExpiry == itemsUsedBeforeExpiry) &&
            (identical(other.wasteAvoidedKg, wasteAvoidedKg) ||
                other.wasteAvoidedKg == wasteAvoidedKg) &&
            (identical(other.dishesCooked, dishesCooked) ||
                other.dishesCooked == dishesCooked) &&
            const DeepCollectionEquality()
                .equals(other.weeklyBars, weeklyBars) &&
            const DeepCollectionEquality()
                .equals(other.byCategory, byCategory));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      period,
      periodLabel,
      itemsUsedBeforeExpiry,
      wasteAvoidedKg,
      dishesCooked,
      const DeepCollectionEquality().hash(weeklyBars),
      const DeepCollectionEquality().hash(byCategory));

  @override
  String toString() {
    return 'WasteReductionSummaryDto(period: $period, periodLabel: $periodLabel, itemsUsedBeforeExpiry: $itemsUsedBeforeExpiry, wasteAvoidedKg: $wasteAvoidedKg, dishesCooked: $dishesCooked, weeklyBars: $weeklyBars, byCategory: $byCategory)';
  }
}

/// @nodoc
abstract mixin class $WasteReductionSummaryDtoCopyWith<$Res> {
  factory $WasteReductionSummaryDtoCopyWith(WasteReductionSummaryDto value,
          $Res Function(WasteReductionSummaryDto) _then) =
      _$WasteReductionSummaryDtoCopyWithImpl;
  @useResult
  $Res call(
      {String period,
      @JsonKey(name: 'period_label') String periodLabel,
      @JsonKey(name: 'items_used_before_expiry') int itemsUsedBeforeExpiry,
      @JsonKey(name: 'waste_avoided_kg') double wasteAvoidedKg,
      @JsonKey(name: 'dishes_cooked') int dishesCooked,
      @JsonKey(name: 'weekly_bars') List<WasteBarDto> weeklyBars,
      @JsonKey(name: 'by_category') List<WasteCategoryDto> byCategory});
}

/// @nodoc
class _$WasteReductionSummaryDtoCopyWithImpl<$Res>
    implements $WasteReductionSummaryDtoCopyWith<$Res> {
  _$WasteReductionSummaryDtoCopyWithImpl(this._self, this._then);

  final WasteReductionSummaryDto _self;
  final $Res Function(WasteReductionSummaryDto) _then;

  /// Create a copy of WasteReductionSummaryDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? period = null,
    Object? periodLabel = null,
    Object? itemsUsedBeforeExpiry = null,
    Object? wasteAvoidedKg = null,
    Object? dishesCooked = null,
    Object? weeklyBars = null,
    Object? byCategory = null,
  }) {
    return _then(_self.copyWith(
      period: null == period
          ? _self.period
          : period // ignore: cast_nullable_to_non_nullable
              as String,
      periodLabel: null == periodLabel
          ? _self.periodLabel
          : periodLabel // ignore: cast_nullable_to_non_nullable
              as String,
      itemsUsedBeforeExpiry: null == itemsUsedBeforeExpiry
          ? _self.itemsUsedBeforeExpiry
          : itemsUsedBeforeExpiry // ignore: cast_nullable_to_non_nullable
              as int,
      wasteAvoidedKg: null == wasteAvoidedKg
          ? _self.wasteAvoidedKg
          : wasteAvoidedKg // ignore: cast_nullable_to_non_nullable
              as double,
      dishesCooked: null == dishesCooked
          ? _self.dishesCooked
          : dishesCooked // ignore: cast_nullable_to_non_nullable
              as int,
      weeklyBars: null == weeklyBars
          ? _self.weeklyBars
          : weeklyBars // ignore: cast_nullable_to_non_nullable
              as List<WasteBarDto>,
      byCategory: null == byCategory
          ? _self.byCategory
          : byCategory // ignore: cast_nullable_to_non_nullable
              as List<WasteCategoryDto>,
    ));
  }
}

/// Adds pattern-matching-related methods to [WasteReductionSummaryDto].
extension WasteReductionSummaryDtoPatterns on WasteReductionSummaryDto {
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

  @optionalTypeArgs
  TResult maybeMap<TResult extends Object?>(
    TResult Function(_WasteReductionSummaryDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _WasteReductionSummaryDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult map<TResult extends Object?>(
    TResult Function(_WasteReductionSummaryDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteReductionSummaryDto():
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult? mapOrNull<TResult extends Object?>(
    TResult? Function(_WasteReductionSummaryDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteReductionSummaryDto() when $default != null:
        return $default(_that);
      case _:
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

  @optionalTypeArgs
  TResult maybeWhen<TResult extends Object?>(
    TResult Function(
            String period,
            @JsonKey(name: 'period_label') String periodLabel,
            @JsonKey(name: 'items_used_before_expiry')
            int itemsUsedBeforeExpiry,
            @JsonKey(name: 'waste_avoided_kg') double wasteAvoidedKg,
            @JsonKey(name: 'dishes_cooked') int dishesCooked,
            @JsonKey(name: 'weekly_bars') List<WasteBarDto> weeklyBars,
            @JsonKey(name: 'by_category') List<WasteCategoryDto> byCategory)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _WasteReductionSummaryDto() when $default != null:
        return $default(
            _that.period,
            _that.periodLabel,
            _that.itemsUsedBeforeExpiry,
            _that.wasteAvoidedKg,
            _that.dishesCooked,
            _that.weeklyBars,
            _that.byCategory);
      case _:
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

  @optionalTypeArgs
  TResult when<TResult extends Object?>(
    TResult Function(
            String period,
            @JsonKey(name: 'period_label') String periodLabel,
            @JsonKey(name: 'items_used_before_expiry')
            int itemsUsedBeforeExpiry,
            @JsonKey(name: 'waste_avoided_kg') double wasteAvoidedKg,
            @JsonKey(name: 'dishes_cooked') int dishesCooked,
            @JsonKey(name: 'weekly_bars') List<WasteBarDto> weeklyBars,
            @JsonKey(name: 'by_category') List<WasteCategoryDto> byCategory)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteReductionSummaryDto():
        return $default(
            _that.period,
            _that.periodLabel,
            _that.itemsUsedBeforeExpiry,
            _that.wasteAvoidedKg,
            _that.dishesCooked,
            _that.weeklyBars,
            _that.byCategory);
      case _:
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

  @optionalTypeArgs
  TResult? whenOrNull<TResult extends Object?>(
    TResult? Function(
            String period,
            @JsonKey(name: 'period_label') String periodLabel,
            @JsonKey(name: 'items_used_before_expiry')
            int itemsUsedBeforeExpiry,
            @JsonKey(name: 'waste_avoided_kg') double wasteAvoidedKg,
            @JsonKey(name: 'dishes_cooked') int dishesCooked,
            @JsonKey(name: 'weekly_bars') List<WasteBarDto> weeklyBars,
            @JsonKey(name: 'by_category') List<WasteCategoryDto> byCategory)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _WasteReductionSummaryDto() when $default != null:
        return $default(
            _that.period,
            _that.periodLabel,
            _that.itemsUsedBeforeExpiry,
            _that.wasteAvoidedKg,
            _that.dishesCooked,
            _that.weeklyBars,
            _that.byCategory);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _WasteReductionSummaryDto extends WasteReductionSummaryDto {
  const _WasteReductionSummaryDto(
      {required this.period,
      @JsonKey(name: 'period_label') required this.periodLabel,
      @JsonKey(name: 'items_used_before_expiry')
      required this.itemsUsedBeforeExpiry,
      @JsonKey(name: 'waste_avoided_kg') required this.wasteAvoidedKg,
      @JsonKey(name: 'dishes_cooked') required this.dishesCooked,
      @JsonKey(name: 'weekly_bars')
      final List<WasteBarDto> weeklyBars = const <WasteBarDto>[],
      @JsonKey(name: 'by_category')
      final List<WasteCategoryDto> byCategory = const <WasteCategoryDto>[]})
      : _weeklyBars = weeklyBars,
        _byCategory = byCategory,
        super._();
  factory _WasteReductionSummaryDto.fromJson(Map<String, dynamic> json) =>
      _$WasteReductionSummaryDtoFromJson(json);

  @override
  final String period;
  @override
  @JsonKey(name: 'period_label')
  final String periodLabel;
  @override
  @JsonKey(name: 'items_used_before_expiry')
  final int itemsUsedBeforeExpiry;
  @override
  @JsonKey(name: 'waste_avoided_kg')
  final double wasteAvoidedKg;
  @override
  @JsonKey(name: 'dishes_cooked')
  final int dishesCooked;
  final List<WasteBarDto> _weeklyBars;
  @override
  @JsonKey(name: 'weekly_bars')
  List<WasteBarDto> get weeklyBars {
    if (_weeklyBars is EqualUnmodifiableListView) return _weeklyBars;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_weeklyBars);
  }

  final List<WasteCategoryDto> _byCategory;
  @override
  @JsonKey(name: 'by_category')
  List<WasteCategoryDto> get byCategory {
    if (_byCategory is EqualUnmodifiableListView) return _byCategory;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_byCategory);
  }

  /// Create a copy of WasteReductionSummaryDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$WasteReductionSummaryDtoCopyWith<_WasteReductionSummaryDto> get copyWith =>
      __$WasteReductionSummaryDtoCopyWithImpl<_WasteReductionSummaryDto>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$WasteReductionSummaryDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _WasteReductionSummaryDto &&
            (identical(other.period, period) || other.period == period) &&
            (identical(other.periodLabel, periodLabel) ||
                other.periodLabel == periodLabel) &&
            (identical(other.itemsUsedBeforeExpiry, itemsUsedBeforeExpiry) ||
                other.itemsUsedBeforeExpiry == itemsUsedBeforeExpiry) &&
            (identical(other.wasteAvoidedKg, wasteAvoidedKg) ||
                other.wasteAvoidedKg == wasteAvoidedKg) &&
            (identical(other.dishesCooked, dishesCooked) ||
                other.dishesCooked == dishesCooked) &&
            const DeepCollectionEquality()
                .equals(other._weeklyBars, _weeklyBars) &&
            const DeepCollectionEquality()
                .equals(other._byCategory, _byCategory));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      period,
      periodLabel,
      itemsUsedBeforeExpiry,
      wasteAvoidedKg,
      dishesCooked,
      const DeepCollectionEquality().hash(_weeklyBars),
      const DeepCollectionEquality().hash(_byCategory));

  @override
  String toString() {
    return 'WasteReductionSummaryDto(period: $period, periodLabel: $periodLabel, itemsUsedBeforeExpiry: $itemsUsedBeforeExpiry, wasteAvoidedKg: $wasteAvoidedKg, dishesCooked: $dishesCooked, weeklyBars: $weeklyBars, byCategory: $byCategory)';
  }
}

/// @nodoc
abstract mixin class _$WasteReductionSummaryDtoCopyWith<$Res>
    implements $WasteReductionSummaryDtoCopyWith<$Res> {
  factory _$WasteReductionSummaryDtoCopyWith(_WasteReductionSummaryDto value,
          $Res Function(_WasteReductionSummaryDto) _then) =
      __$WasteReductionSummaryDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String period,
      @JsonKey(name: 'period_label') String periodLabel,
      @JsonKey(name: 'items_used_before_expiry') int itemsUsedBeforeExpiry,
      @JsonKey(name: 'waste_avoided_kg') double wasteAvoidedKg,
      @JsonKey(name: 'dishes_cooked') int dishesCooked,
      @JsonKey(name: 'weekly_bars') List<WasteBarDto> weeklyBars,
      @JsonKey(name: 'by_category') List<WasteCategoryDto> byCategory});
}

/// @nodoc
class __$WasteReductionSummaryDtoCopyWithImpl<$Res>
    implements _$WasteReductionSummaryDtoCopyWith<$Res> {
  __$WasteReductionSummaryDtoCopyWithImpl(this._self, this._then);

  final _WasteReductionSummaryDto _self;
  final $Res Function(_WasteReductionSummaryDto) _then;

  /// Create a copy of WasteReductionSummaryDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? period = null,
    Object? periodLabel = null,
    Object? itemsUsedBeforeExpiry = null,
    Object? wasteAvoidedKg = null,
    Object? dishesCooked = null,
    Object? weeklyBars = null,
    Object? byCategory = null,
  }) {
    return _then(_WasteReductionSummaryDto(
      period: null == period
          ? _self.period
          : period // ignore: cast_nullable_to_non_nullable
              as String,
      periodLabel: null == periodLabel
          ? _self.periodLabel
          : periodLabel // ignore: cast_nullable_to_non_nullable
              as String,
      itemsUsedBeforeExpiry: null == itemsUsedBeforeExpiry
          ? _self.itemsUsedBeforeExpiry
          : itemsUsedBeforeExpiry // ignore: cast_nullable_to_non_nullable
              as int,
      wasteAvoidedKg: null == wasteAvoidedKg
          ? _self.wasteAvoidedKg
          : wasteAvoidedKg // ignore: cast_nullable_to_non_nullable
              as double,
      dishesCooked: null == dishesCooked
          ? _self.dishesCooked
          : dishesCooked // ignore: cast_nullable_to_non_nullable
              as int,
      weeklyBars: null == weeklyBars
          ? _self._weeklyBars
          : weeklyBars // ignore: cast_nullable_to_non_nullable
              as List<WasteBarDto>,
      byCategory: null == byCategory
          ? _self._byCategory
          : byCategory // ignore: cast_nullable_to_non_nullable
              as List<WasteCategoryDto>,
    ));
  }
}

// dart format on
