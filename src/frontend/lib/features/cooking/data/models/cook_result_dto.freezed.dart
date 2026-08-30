// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'cook_result_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$CookResultDto {
  @JsonKey(name: 'dish_id')
  String get dishId;
  @JsonKey(name: 'dish_name')
  String get dishName;
  List<PantryChangeDto> get changes;
  @JsonKey(name: 'updated_pantry_items')
  List<PantryItemDto> get updatedPantryItems;
  @JsonKey(name: 'depleted_item_ids')
  List<String> get depletedItemIds;
  @JsonKey(name: 'near_expiry_used_count')
  int get nearExpiryUsedCount;
  @JsonKey(name: 'waste_avoided_grams')
  double get wasteAvoidedGrams;
  @JsonKey(name: 'leftover_servings')
  int get leftoverServings;

  /// Create a copy of CookResultDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $CookResultDtoCopyWith<CookResultDto> get copyWith =>
      _$CookResultDtoCopyWithImpl<CookResultDto>(
          this as CookResultDto, _$identity);

  /// Serializes this CookResultDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is CookResultDto &&
            (identical(other.dishId, dishId) || other.dishId == dishId) &&
            (identical(other.dishName, dishName) ||
                other.dishName == dishName) &&
            const DeepCollectionEquality().equals(other.changes, changes) &&
            const DeepCollectionEquality()
                .equals(other.updatedPantryItems, updatedPantryItems) &&
            const DeepCollectionEquality()
                .equals(other.depletedItemIds, depletedItemIds) &&
            (identical(other.nearExpiryUsedCount, nearExpiryUsedCount) ||
                other.nearExpiryUsedCount == nearExpiryUsedCount) &&
            (identical(other.wasteAvoidedGrams, wasteAvoidedGrams) ||
                other.wasteAvoidedGrams == wasteAvoidedGrams) &&
            (identical(other.leftoverServings, leftoverServings) ||
                other.leftoverServings == leftoverServings));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      dishId,
      dishName,
      const DeepCollectionEquality().hash(changes),
      const DeepCollectionEquality().hash(updatedPantryItems),
      const DeepCollectionEquality().hash(depletedItemIds),
      nearExpiryUsedCount,
      wasteAvoidedGrams,
      leftoverServings);

  @override
  String toString() {
    return 'CookResultDto(dishId: $dishId, dishName: $dishName, changes: $changes, updatedPantryItems: $updatedPantryItems, depletedItemIds: $depletedItemIds, nearExpiryUsedCount: $nearExpiryUsedCount, wasteAvoidedGrams: $wasteAvoidedGrams, leftoverServings: $leftoverServings)';
  }
}

/// @nodoc
abstract mixin class $CookResultDtoCopyWith<$Res> {
  factory $CookResultDtoCopyWith(
          CookResultDto value, $Res Function(CookResultDto) _then) =
      _$CookResultDtoCopyWithImpl;
  @useResult
  $Res call(
      {@JsonKey(name: 'dish_id') String dishId,
      @JsonKey(name: 'dish_name') String dishName,
      List<PantryChangeDto> changes,
      @JsonKey(name: 'updated_pantry_items')
      List<PantryItemDto> updatedPantryItems,
      @JsonKey(name: 'depleted_item_ids') List<String> depletedItemIds,
      @JsonKey(name: 'near_expiry_used_count') int nearExpiryUsedCount,
      @JsonKey(name: 'waste_avoided_grams') double wasteAvoidedGrams,
      @JsonKey(name: 'leftover_servings') int leftoverServings});
}

/// @nodoc
class _$CookResultDtoCopyWithImpl<$Res>
    implements $CookResultDtoCopyWith<$Res> {
  _$CookResultDtoCopyWithImpl(this._self, this._then);

  final CookResultDto _self;
  final $Res Function(CookResultDto) _then;

  /// Create a copy of CookResultDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? dishId = null,
    Object? dishName = null,
    Object? changes = null,
    Object? updatedPantryItems = null,
    Object? depletedItemIds = null,
    Object? nearExpiryUsedCount = null,
    Object? wasteAvoidedGrams = null,
    Object? leftoverServings = null,
  }) {
    return _then(_self.copyWith(
      dishId: null == dishId
          ? _self.dishId
          : dishId // ignore: cast_nullable_to_non_nullable
              as String,
      dishName: null == dishName
          ? _self.dishName
          : dishName // ignore: cast_nullable_to_non_nullable
              as String,
      changes: null == changes
          ? _self.changes
          : changes // ignore: cast_nullable_to_non_nullable
              as List<PantryChangeDto>,
      updatedPantryItems: null == updatedPantryItems
          ? _self.updatedPantryItems
          : updatedPantryItems // ignore: cast_nullable_to_non_nullable
              as List<PantryItemDto>,
      depletedItemIds: null == depletedItemIds
          ? _self.depletedItemIds
          : depletedItemIds // ignore: cast_nullable_to_non_nullable
              as List<String>,
      nearExpiryUsedCount: null == nearExpiryUsedCount
          ? _self.nearExpiryUsedCount
          : nearExpiryUsedCount // ignore: cast_nullable_to_non_nullable
              as int,
      wasteAvoidedGrams: null == wasteAvoidedGrams
          ? _self.wasteAvoidedGrams
          : wasteAvoidedGrams // ignore: cast_nullable_to_non_nullable
              as double,
      leftoverServings: null == leftoverServings
          ? _self.leftoverServings
          : leftoverServings // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// Adds pattern-matching-related methods to [CookResultDto].
extension CookResultDtoPatterns on CookResultDto {
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
    TResult Function(_CookResultDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _CookResultDto() when $default != null:
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
    TResult Function(_CookResultDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookResultDto():
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
    TResult? Function(_CookResultDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookResultDto() when $default != null:
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
            @JsonKey(name: 'dish_id') String dishId,
            @JsonKey(name: 'dish_name') String dishName,
            List<PantryChangeDto> changes,
            @JsonKey(name: 'updated_pantry_items')
            List<PantryItemDto> updatedPantryItems,
            @JsonKey(name: 'depleted_item_ids') List<String> depletedItemIds,
            @JsonKey(name: 'near_expiry_used_count') int nearExpiryUsedCount,
            @JsonKey(name: 'waste_avoided_grams') double wasteAvoidedGrams,
            @JsonKey(name: 'leftover_servings') int leftoverServings)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _CookResultDto() when $default != null:
        return $default(
            _that.dishId,
            _that.dishName,
            _that.changes,
            _that.updatedPantryItems,
            _that.depletedItemIds,
            _that.nearExpiryUsedCount,
            _that.wasteAvoidedGrams,
            _that.leftoverServings);
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
            @JsonKey(name: 'dish_id') String dishId,
            @JsonKey(name: 'dish_name') String dishName,
            List<PantryChangeDto> changes,
            @JsonKey(name: 'updated_pantry_items')
            List<PantryItemDto> updatedPantryItems,
            @JsonKey(name: 'depleted_item_ids') List<String> depletedItemIds,
            @JsonKey(name: 'near_expiry_used_count') int nearExpiryUsedCount,
            @JsonKey(name: 'waste_avoided_grams') double wasteAvoidedGrams,
            @JsonKey(name: 'leftover_servings') int leftoverServings)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookResultDto():
        return $default(
            _that.dishId,
            _that.dishName,
            _that.changes,
            _that.updatedPantryItems,
            _that.depletedItemIds,
            _that.nearExpiryUsedCount,
            _that.wasteAvoidedGrams,
            _that.leftoverServings);
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
            @JsonKey(name: 'dish_id') String dishId,
            @JsonKey(name: 'dish_name') String dishName,
            List<PantryChangeDto> changes,
            @JsonKey(name: 'updated_pantry_items')
            List<PantryItemDto> updatedPantryItems,
            @JsonKey(name: 'depleted_item_ids') List<String> depletedItemIds,
            @JsonKey(name: 'near_expiry_used_count') int nearExpiryUsedCount,
            @JsonKey(name: 'waste_avoided_grams') double wasteAvoidedGrams,
            @JsonKey(name: 'leftover_servings') int leftoverServings)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookResultDto() when $default != null:
        return $default(
            _that.dishId,
            _that.dishName,
            _that.changes,
            _that.updatedPantryItems,
            _that.depletedItemIds,
            _that.nearExpiryUsedCount,
            _that.wasteAvoidedGrams,
            _that.leftoverServings);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _CookResultDto extends CookResultDto {
  const _CookResultDto(
      {@JsonKey(name: 'dish_id') this.dishId = '',
      @JsonKey(name: 'dish_name') this.dishName = '',
      final List<PantryChangeDto> changes = const <PantryChangeDto>[],
      @JsonKey(name: 'updated_pantry_items')
      final List<PantryItemDto> updatedPantryItems = const <PantryItemDto>[],
      @JsonKey(name: 'depleted_item_ids')
      final List<String> depletedItemIds = const <String>[],
      @JsonKey(name: 'near_expiry_used_count') this.nearExpiryUsedCount = 0,
      @JsonKey(name: 'waste_avoided_grams') this.wasteAvoidedGrams = 0,
      @JsonKey(name: 'leftover_servings') this.leftoverServings = 0})
      : _changes = changes,
        _updatedPantryItems = updatedPantryItems,
        _depletedItemIds = depletedItemIds,
        super._();
  factory _CookResultDto.fromJson(Map<String, dynamic> json) =>
      _$CookResultDtoFromJson(json);

  @override
  @JsonKey(name: 'dish_id')
  final String dishId;
  @override
  @JsonKey(name: 'dish_name')
  final String dishName;
  final List<PantryChangeDto> _changes;
  @override
  @JsonKey()
  List<PantryChangeDto> get changes {
    if (_changes is EqualUnmodifiableListView) return _changes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_changes);
  }

  final List<PantryItemDto> _updatedPantryItems;
  @override
  @JsonKey(name: 'updated_pantry_items')
  List<PantryItemDto> get updatedPantryItems {
    if (_updatedPantryItems is EqualUnmodifiableListView)
      return _updatedPantryItems;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_updatedPantryItems);
  }

  final List<String> _depletedItemIds;
  @override
  @JsonKey(name: 'depleted_item_ids')
  List<String> get depletedItemIds {
    if (_depletedItemIds is EqualUnmodifiableListView) return _depletedItemIds;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_depletedItemIds);
  }

  @override
  @JsonKey(name: 'near_expiry_used_count')
  final int nearExpiryUsedCount;
  @override
  @JsonKey(name: 'waste_avoided_grams')
  final double wasteAvoidedGrams;
  @override
  @JsonKey(name: 'leftover_servings')
  final int leftoverServings;

  /// Create a copy of CookResultDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$CookResultDtoCopyWith<_CookResultDto> get copyWith =>
      __$CookResultDtoCopyWithImpl<_CookResultDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$CookResultDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _CookResultDto &&
            (identical(other.dishId, dishId) || other.dishId == dishId) &&
            (identical(other.dishName, dishName) ||
                other.dishName == dishName) &&
            const DeepCollectionEquality().equals(other._changes, _changes) &&
            const DeepCollectionEquality()
                .equals(other._updatedPantryItems, _updatedPantryItems) &&
            const DeepCollectionEquality()
                .equals(other._depletedItemIds, _depletedItemIds) &&
            (identical(other.nearExpiryUsedCount, nearExpiryUsedCount) ||
                other.nearExpiryUsedCount == nearExpiryUsedCount) &&
            (identical(other.wasteAvoidedGrams, wasteAvoidedGrams) ||
                other.wasteAvoidedGrams == wasteAvoidedGrams) &&
            (identical(other.leftoverServings, leftoverServings) ||
                other.leftoverServings == leftoverServings));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      dishId,
      dishName,
      const DeepCollectionEquality().hash(_changes),
      const DeepCollectionEquality().hash(_updatedPantryItems),
      const DeepCollectionEquality().hash(_depletedItemIds),
      nearExpiryUsedCount,
      wasteAvoidedGrams,
      leftoverServings);

  @override
  String toString() {
    return 'CookResultDto(dishId: $dishId, dishName: $dishName, changes: $changes, updatedPantryItems: $updatedPantryItems, depletedItemIds: $depletedItemIds, nearExpiryUsedCount: $nearExpiryUsedCount, wasteAvoidedGrams: $wasteAvoidedGrams, leftoverServings: $leftoverServings)';
  }
}

/// @nodoc
abstract mixin class _$CookResultDtoCopyWith<$Res>
    implements $CookResultDtoCopyWith<$Res> {
  factory _$CookResultDtoCopyWith(
          _CookResultDto value, $Res Function(_CookResultDto) _then) =
      __$CookResultDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'dish_id') String dishId,
      @JsonKey(name: 'dish_name') String dishName,
      List<PantryChangeDto> changes,
      @JsonKey(name: 'updated_pantry_items')
      List<PantryItemDto> updatedPantryItems,
      @JsonKey(name: 'depleted_item_ids') List<String> depletedItemIds,
      @JsonKey(name: 'near_expiry_used_count') int nearExpiryUsedCount,
      @JsonKey(name: 'waste_avoided_grams') double wasteAvoidedGrams,
      @JsonKey(name: 'leftover_servings') int leftoverServings});
}

/// @nodoc
class __$CookResultDtoCopyWithImpl<$Res>
    implements _$CookResultDtoCopyWith<$Res> {
  __$CookResultDtoCopyWithImpl(this._self, this._then);

  final _CookResultDto _self;
  final $Res Function(_CookResultDto) _then;

  /// Create a copy of CookResultDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? dishId = null,
    Object? dishName = null,
    Object? changes = null,
    Object? updatedPantryItems = null,
    Object? depletedItemIds = null,
    Object? nearExpiryUsedCount = null,
    Object? wasteAvoidedGrams = null,
    Object? leftoverServings = null,
  }) {
    return _then(_CookResultDto(
      dishId: null == dishId
          ? _self.dishId
          : dishId // ignore: cast_nullable_to_non_nullable
              as String,
      dishName: null == dishName
          ? _self.dishName
          : dishName // ignore: cast_nullable_to_non_nullable
              as String,
      changes: null == changes
          ? _self._changes
          : changes // ignore: cast_nullable_to_non_nullable
              as List<PantryChangeDto>,
      updatedPantryItems: null == updatedPantryItems
          ? _self._updatedPantryItems
          : updatedPantryItems // ignore: cast_nullable_to_non_nullable
              as List<PantryItemDto>,
      depletedItemIds: null == depletedItemIds
          ? _self._depletedItemIds
          : depletedItemIds // ignore: cast_nullable_to_non_nullable
              as List<String>,
      nearExpiryUsedCount: null == nearExpiryUsedCount
          ? _self.nearExpiryUsedCount
          : nearExpiryUsedCount // ignore: cast_nullable_to_non_nullable
              as int,
      wasteAvoidedGrams: null == wasteAvoidedGrams
          ? _self.wasteAvoidedGrams
          : wasteAvoidedGrams // ignore: cast_nullable_to_non_nullable
              as double,
      leftoverServings: null == leftoverServings
          ? _self.leftoverServings
          : leftoverServings // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
mixin _$PantryChangeDto {
  String get name;
  String get unit;
  double get before;
  double get after;
  @JsonKey(name: 'near_expiry_used')
  bool get nearExpiryUsed;
  @JsonKey(name: 'pantry_item_id')
  String? get pantryItemId;

  /// Create a copy of PantryChangeDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $PantryChangeDtoCopyWith<PantryChangeDto> get copyWith =>
      _$PantryChangeDtoCopyWithImpl<PantryChangeDto>(
          this as PantryChangeDto, _$identity);

  /// Serializes this PantryChangeDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is PantryChangeDto &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.unit, unit) || other.unit == unit) &&
            (identical(other.before, before) || other.before == before) &&
            (identical(other.after, after) || other.after == after) &&
            (identical(other.nearExpiryUsed, nearExpiryUsed) ||
                other.nearExpiryUsed == nearExpiryUsed) &&
            (identical(other.pantryItemId, pantryItemId) ||
                other.pantryItemId == pantryItemId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, name, unit, before, after, nearExpiryUsed, pantryItemId);

  @override
  String toString() {
    return 'PantryChangeDto(name: $name, unit: $unit, before: $before, after: $after, nearExpiryUsed: $nearExpiryUsed, pantryItemId: $pantryItemId)';
  }
}

/// @nodoc
abstract mixin class $PantryChangeDtoCopyWith<$Res> {
  factory $PantryChangeDtoCopyWith(
          PantryChangeDto value, $Res Function(PantryChangeDto) _then) =
      _$PantryChangeDtoCopyWithImpl;
  @useResult
  $Res call(
      {String name,
      String unit,
      double before,
      double after,
      @JsonKey(name: 'near_expiry_used') bool nearExpiryUsed,
      @JsonKey(name: 'pantry_item_id') String? pantryItemId});
}

/// @nodoc
class _$PantryChangeDtoCopyWithImpl<$Res>
    implements $PantryChangeDtoCopyWith<$Res> {
  _$PantryChangeDtoCopyWithImpl(this._self, this._then);

  final PantryChangeDto _self;
  final $Res Function(PantryChangeDto) _then;

  /// Create a copy of PantryChangeDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? unit = null,
    Object? before = null,
    Object? after = null,
    Object? nearExpiryUsed = null,
    Object? pantryItemId = freezed,
  }) {
    return _then(_self.copyWith(
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      unit: null == unit
          ? _self.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      before: null == before
          ? _self.before
          : before // ignore: cast_nullable_to_non_nullable
              as double,
      after: null == after
          ? _self.after
          : after // ignore: cast_nullable_to_non_nullable
              as double,
      nearExpiryUsed: null == nearExpiryUsed
          ? _self.nearExpiryUsed
          : nearExpiryUsed // ignore: cast_nullable_to_non_nullable
              as bool,
      pantryItemId: freezed == pantryItemId
          ? _self.pantryItemId
          : pantryItemId // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// Adds pattern-matching-related methods to [PantryChangeDto].
extension PantryChangeDtoPatterns on PantryChangeDto {
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
    TResult Function(_PantryChangeDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _PantryChangeDto() when $default != null:
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
    TResult Function(_PantryChangeDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _PantryChangeDto():
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
    TResult? Function(_PantryChangeDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _PantryChangeDto() when $default != null:
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
            String name,
            String unit,
            double before,
            double after,
            @JsonKey(name: 'near_expiry_used') bool nearExpiryUsed,
            @JsonKey(name: 'pantry_item_id') String? pantryItemId)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _PantryChangeDto() when $default != null:
        return $default(_that.name, _that.unit, _that.before, _that.after,
            _that.nearExpiryUsed, _that.pantryItemId);
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
            String name,
            String unit,
            double before,
            double after,
            @JsonKey(name: 'near_expiry_used') bool nearExpiryUsed,
            @JsonKey(name: 'pantry_item_id') String? pantryItemId)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _PantryChangeDto():
        return $default(_that.name, _that.unit, _that.before, _that.after,
            _that.nearExpiryUsed, _that.pantryItemId);
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
            String name,
            String unit,
            double before,
            double after,
            @JsonKey(name: 'near_expiry_used') bool nearExpiryUsed,
            @JsonKey(name: 'pantry_item_id') String? pantryItemId)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _PantryChangeDto() when $default != null:
        return $default(_that.name, _that.unit, _that.before, _that.after,
            _that.nearExpiryUsed, _that.pantryItemId);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _PantryChangeDto extends PantryChangeDto {
  const _PantryChangeDto(
      {required this.name,
      this.unit = 'g',
      this.before = 0,
      this.after = 0,
      @JsonKey(name: 'near_expiry_used') this.nearExpiryUsed = false,
      @JsonKey(name: 'pantry_item_id') this.pantryItemId})
      : super._();
  factory _PantryChangeDto.fromJson(Map<String, dynamic> json) =>
      _$PantryChangeDtoFromJson(json);

  @override
  final String name;
  @override
  @JsonKey()
  final String unit;
  @override
  @JsonKey()
  final double before;
  @override
  @JsonKey()
  final double after;
  @override
  @JsonKey(name: 'near_expiry_used')
  final bool nearExpiryUsed;
  @override
  @JsonKey(name: 'pantry_item_id')
  final String? pantryItemId;

  /// Create a copy of PantryChangeDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$PantryChangeDtoCopyWith<_PantryChangeDto> get copyWith =>
      __$PantryChangeDtoCopyWithImpl<_PantryChangeDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$PantryChangeDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _PantryChangeDto &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.unit, unit) || other.unit == unit) &&
            (identical(other.before, before) || other.before == before) &&
            (identical(other.after, after) || other.after == after) &&
            (identical(other.nearExpiryUsed, nearExpiryUsed) ||
                other.nearExpiryUsed == nearExpiryUsed) &&
            (identical(other.pantryItemId, pantryItemId) ||
                other.pantryItemId == pantryItemId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, name, unit, before, after, nearExpiryUsed, pantryItemId);

  @override
  String toString() {
    return 'PantryChangeDto(name: $name, unit: $unit, before: $before, after: $after, nearExpiryUsed: $nearExpiryUsed, pantryItemId: $pantryItemId)';
  }
}

/// @nodoc
abstract mixin class _$PantryChangeDtoCopyWith<$Res>
    implements $PantryChangeDtoCopyWith<$Res> {
  factory _$PantryChangeDtoCopyWith(
          _PantryChangeDto value, $Res Function(_PantryChangeDto) _then) =
      __$PantryChangeDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String name,
      String unit,
      double before,
      double after,
      @JsonKey(name: 'near_expiry_used') bool nearExpiryUsed,
      @JsonKey(name: 'pantry_item_id') String? pantryItemId});
}

/// @nodoc
class __$PantryChangeDtoCopyWithImpl<$Res>
    implements _$PantryChangeDtoCopyWith<$Res> {
  __$PantryChangeDtoCopyWithImpl(this._self, this._then);

  final _PantryChangeDto _self;
  final $Res Function(_PantryChangeDto) _then;

  /// Create a copy of PantryChangeDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? name = null,
    Object? unit = null,
    Object? before = null,
    Object? after = null,
    Object? nearExpiryUsed = null,
    Object? pantryItemId = freezed,
  }) {
    return _then(_PantryChangeDto(
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      unit: null == unit
          ? _self.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      before: null == before
          ? _self.before
          : before // ignore: cast_nullable_to_non_nullable
              as double,
      after: null == after
          ? _self.after
          : after // ignore: cast_nullable_to_non_nullable
              as double,
      nearExpiryUsed: null == nearExpiryUsed
          ? _self.nearExpiryUsed
          : nearExpiryUsed // ignore: cast_nullable_to_non_nullable
              as bool,
      pantryItemId: freezed == pantryItemId
          ? _self.pantryItemId
          : pantryItemId // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

// dart format on
