// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'dish_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$DishDto {
  String get id;
  String get name;
  int get servings;
  @JsonKey(name: 'prep_time_min')
  int get prepTimeMin;
  @JsonKey(name: 'cook_time_min')
  int get cookTimeMin;
  String get cuisine;
  String get difficulty;
  @JsonKey(name: 'image_url')
  String? get imageUrl;
  @JsonKey(name: 'nutrition_per_serving')
  MacrosDto? get nutritionPerServing;
  List<DishIngredientDto> get ingredients;
  List<CookingStepDto> get steps;

  /// Create a copy of DishDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $DishDtoCopyWith<DishDto> get copyWith =>
      _$DishDtoCopyWithImpl<DishDto>(this as DishDto, _$identity);

  /// Serializes this DishDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is DishDto &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.servings, servings) ||
                other.servings == servings) &&
            (identical(other.prepTimeMin, prepTimeMin) ||
                other.prepTimeMin == prepTimeMin) &&
            (identical(other.cookTimeMin, cookTimeMin) ||
                other.cookTimeMin == cookTimeMin) &&
            (identical(other.cuisine, cuisine) || other.cuisine == cuisine) &&
            (identical(other.difficulty, difficulty) ||
                other.difficulty == difficulty) &&
            (identical(other.imageUrl, imageUrl) ||
                other.imageUrl == imageUrl) &&
            (identical(other.nutritionPerServing, nutritionPerServing) ||
                other.nutritionPerServing == nutritionPerServing) &&
            const DeepCollectionEquality()
                .equals(other.ingredients, ingredients) &&
            const DeepCollectionEquality().equals(other.steps, steps));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      name,
      servings,
      prepTimeMin,
      cookTimeMin,
      cuisine,
      difficulty,
      imageUrl,
      nutritionPerServing,
      const DeepCollectionEquality().hash(ingredients),
      const DeepCollectionEquality().hash(steps));

  @override
  String toString() {
    return 'DishDto(id: $id, name: $name, servings: $servings, prepTimeMin: $prepTimeMin, cookTimeMin: $cookTimeMin, cuisine: $cuisine, difficulty: $difficulty, imageUrl: $imageUrl, nutritionPerServing: $nutritionPerServing, ingredients: $ingredients, steps: $steps)';
  }
}

/// @nodoc
abstract mixin class $DishDtoCopyWith<$Res> {
  factory $DishDtoCopyWith(DishDto value, $Res Function(DishDto) _then) =
      _$DishDtoCopyWithImpl;
  @useResult
  $Res call(
      {String id,
      String name,
      int servings,
      @JsonKey(name: 'prep_time_min') int prepTimeMin,
      @JsonKey(name: 'cook_time_min') int cookTimeMin,
      String cuisine,
      String difficulty,
      @JsonKey(name: 'image_url') String? imageUrl,
      @JsonKey(name: 'nutrition_per_serving') MacrosDto? nutritionPerServing,
      List<DishIngredientDto> ingredients,
      List<CookingStepDto> steps});

  $MacrosDtoCopyWith<$Res>? get nutritionPerServing;
}

/// @nodoc
class _$DishDtoCopyWithImpl<$Res> implements $DishDtoCopyWith<$Res> {
  _$DishDtoCopyWithImpl(this._self, this._then);

  final DishDto _self;
  final $Res Function(DishDto) _then;

  /// Create a copy of DishDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? servings = null,
    Object? prepTimeMin = null,
    Object? cookTimeMin = null,
    Object? cuisine = null,
    Object? difficulty = null,
    Object? imageUrl = freezed,
    Object? nutritionPerServing = freezed,
    Object? ingredients = null,
    Object? steps = null,
  }) {
    return _then(_self.copyWith(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      servings: null == servings
          ? _self.servings
          : servings // ignore: cast_nullable_to_non_nullable
              as int,
      prepTimeMin: null == prepTimeMin
          ? _self.prepTimeMin
          : prepTimeMin // ignore: cast_nullable_to_non_nullable
              as int,
      cookTimeMin: null == cookTimeMin
          ? _self.cookTimeMin
          : cookTimeMin // ignore: cast_nullable_to_non_nullable
              as int,
      cuisine: null == cuisine
          ? _self.cuisine
          : cuisine // ignore: cast_nullable_to_non_nullable
              as String,
      difficulty: null == difficulty
          ? _self.difficulty
          : difficulty // ignore: cast_nullable_to_non_nullable
              as String,
      imageUrl: freezed == imageUrl
          ? _self.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      nutritionPerServing: freezed == nutritionPerServing
          ? _self.nutritionPerServing
          : nutritionPerServing // ignore: cast_nullable_to_non_nullable
              as MacrosDto?,
      ingredients: null == ingredients
          ? _self.ingredients
          : ingredients // ignore: cast_nullable_to_non_nullable
              as List<DishIngredientDto>,
      steps: null == steps
          ? _self.steps
          : steps // ignore: cast_nullable_to_non_nullable
              as List<CookingStepDto>,
    ));
  }

  /// Create a copy of DishDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $MacrosDtoCopyWith<$Res>? get nutritionPerServing {
    if (_self.nutritionPerServing == null) {
      return null;
    }

    return $MacrosDtoCopyWith<$Res>(_self.nutritionPerServing!, (value) {
      return _then(_self.copyWith(nutritionPerServing: value));
    });
  }
}

/// Adds pattern-matching-related methods to [DishDto].
extension DishDtoPatterns on DishDto {
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
    TResult Function(_DishDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _DishDto() when $default != null:
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
    TResult Function(_DishDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _DishDto():
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
    TResult? Function(_DishDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _DishDto() when $default != null:
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
            String id,
            String name,
            int servings,
            @JsonKey(name: 'prep_time_min') int prepTimeMin,
            @JsonKey(name: 'cook_time_min') int cookTimeMin,
            String cuisine,
            String difficulty,
            @JsonKey(name: 'image_url') String? imageUrl,
            @JsonKey(name: 'nutrition_per_serving')
            MacrosDto? nutritionPerServing,
            List<DishIngredientDto> ingredients,
            List<CookingStepDto> steps)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _DishDto() when $default != null:
        return $default(
            _that.id,
            _that.name,
            _that.servings,
            _that.prepTimeMin,
            _that.cookTimeMin,
            _that.cuisine,
            _that.difficulty,
            _that.imageUrl,
            _that.nutritionPerServing,
            _that.ingredients,
            _that.steps);
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
            String id,
            String name,
            int servings,
            @JsonKey(name: 'prep_time_min') int prepTimeMin,
            @JsonKey(name: 'cook_time_min') int cookTimeMin,
            String cuisine,
            String difficulty,
            @JsonKey(name: 'image_url') String? imageUrl,
            @JsonKey(name: 'nutrition_per_serving')
            MacrosDto? nutritionPerServing,
            List<DishIngredientDto> ingredients,
            List<CookingStepDto> steps)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _DishDto():
        return $default(
            _that.id,
            _that.name,
            _that.servings,
            _that.prepTimeMin,
            _that.cookTimeMin,
            _that.cuisine,
            _that.difficulty,
            _that.imageUrl,
            _that.nutritionPerServing,
            _that.ingredients,
            _that.steps);
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
            String id,
            String name,
            int servings,
            @JsonKey(name: 'prep_time_min') int prepTimeMin,
            @JsonKey(name: 'cook_time_min') int cookTimeMin,
            String cuisine,
            String difficulty,
            @JsonKey(name: 'image_url') String? imageUrl,
            @JsonKey(name: 'nutrition_per_serving')
            MacrosDto? nutritionPerServing,
            List<DishIngredientDto> ingredients,
            List<CookingStepDto> steps)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _DishDto() when $default != null:
        return $default(
            _that.id,
            _that.name,
            _that.servings,
            _that.prepTimeMin,
            _that.cookTimeMin,
            _that.cuisine,
            _that.difficulty,
            _that.imageUrl,
            _that.nutritionPerServing,
            _that.ingredients,
            _that.steps);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _DishDto extends DishDto {
  const _DishDto(
      {required this.id,
      required this.name,
      this.servings = 1,
      @JsonKey(name: 'prep_time_min') this.prepTimeMin = 0,
      @JsonKey(name: 'cook_time_min') this.cookTimeMin = 0,
      this.cuisine = '',
      this.difficulty = '',
      @JsonKey(name: 'image_url') this.imageUrl,
      @JsonKey(name: 'nutrition_per_serving') this.nutritionPerServing,
      final List<DishIngredientDto> ingredients = const <DishIngredientDto>[],
      final List<CookingStepDto> steps = const <CookingStepDto>[]})
      : _ingredients = ingredients,
        _steps = steps,
        super._();
  factory _DishDto.fromJson(Map<String, dynamic> json) =>
      _$DishDtoFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  @JsonKey()
  final int servings;
  @override
  @JsonKey(name: 'prep_time_min')
  final int prepTimeMin;
  @override
  @JsonKey(name: 'cook_time_min')
  final int cookTimeMin;
  @override
  @JsonKey()
  final String cuisine;
  @override
  @JsonKey()
  final String difficulty;
  @override
  @JsonKey(name: 'image_url')
  final String? imageUrl;
  @override
  @JsonKey(name: 'nutrition_per_serving')
  final MacrosDto? nutritionPerServing;
  final List<DishIngredientDto> _ingredients;
  @override
  @JsonKey()
  List<DishIngredientDto> get ingredients {
    if (_ingredients is EqualUnmodifiableListView) return _ingredients;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_ingredients);
  }

  final List<CookingStepDto> _steps;
  @override
  @JsonKey()
  List<CookingStepDto> get steps {
    if (_steps is EqualUnmodifiableListView) return _steps;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_steps);
  }

  /// Create a copy of DishDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$DishDtoCopyWith<_DishDto> get copyWith =>
      __$DishDtoCopyWithImpl<_DishDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$DishDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _DishDto &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.servings, servings) ||
                other.servings == servings) &&
            (identical(other.prepTimeMin, prepTimeMin) ||
                other.prepTimeMin == prepTimeMin) &&
            (identical(other.cookTimeMin, cookTimeMin) ||
                other.cookTimeMin == cookTimeMin) &&
            (identical(other.cuisine, cuisine) || other.cuisine == cuisine) &&
            (identical(other.difficulty, difficulty) ||
                other.difficulty == difficulty) &&
            (identical(other.imageUrl, imageUrl) ||
                other.imageUrl == imageUrl) &&
            (identical(other.nutritionPerServing, nutritionPerServing) ||
                other.nutritionPerServing == nutritionPerServing) &&
            const DeepCollectionEquality()
                .equals(other._ingredients, _ingredients) &&
            const DeepCollectionEquality().equals(other._steps, _steps));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      name,
      servings,
      prepTimeMin,
      cookTimeMin,
      cuisine,
      difficulty,
      imageUrl,
      nutritionPerServing,
      const DeepCollectionEquality().hash(_ingredients),
      const DeepCollectionEquality().hash(_steps));

  @override
  String toString() {
    return 'DishDto(id: $id, name: $name, servings: $servings, prepTimeMin: $prepTimeMin, cookTimeMin: $cookTimeMin, cuisine: $cuisine, difficulty: $difficulty, imageUrl: $imageUrl, nutritionPerServing: $nutritionPerServing, ingredients: $ingredients, steps: $steps)';
  }
}

/// @nodoc
abstract mixin class _$DishDtoCopyWith<$Res> implements $DishDtoCopyWith<$Res> {
  factory _$DishDtoCopyWith(_DishDto value, $Res Function(_DishDto) _then) =
      __$DishDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      int servings,
      @JsonKey(name: 'prep_time_min') int prepTimeMin,
      @JsonKey(name: 'cook_time_min') int cookTimeMin,
      String cuisine,
      String difficulty,
      @JsonKey(name: 'image_url') String? imageUrl,
      @JsonKey(name: 'nutrition_per_serving') MacrosDto? nutritionPerServing,
      List<DishIngredientDto> ingredients,
      List<CookingStepDto> steps});

  @override
  $MacrosDtoCopyWith<$Res>? get nutritionPerServing;
}

/// @nodoc
class __$DishDtoCopyWithImpl<$Res> implements _$DishDtoCopyWith<$Res> {
  __$DishDtoCopyWithImpl(this._self, this._then);

  final _DishDto _self;
  final $Res Function(_DishDto) _then;

  /// Create a copy of DishDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? servings = null,
    Object? prepTimeMin = null,
    Object? cookTimeMin = null,
    Object? cuisine = null,
    Object? difficulty = null,
    Object? imageUrl = freezed,
    Object? nutritionPerServing = freezed,
    Object? ingredients = null,
    Object? steps = null,
  }) {
    return _then(_DishDto(
      id: null == id
          ? _self.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      servings: null == servings
          ? _self.servings
          : servings // ignore: cast_nullable_to_non_nullable
              as int,
      prepTimeMin: null == prepTimeMin
          ? _self.prepTimeMin
          : prepTimeMin // ignore: cast_nullable_to_non_nullable
              as int,
      cookTimeMin: null == cookTimeMin
          ? _self.cookTimeMin
          : cookTimeMin // ignore: cast_nullable_to_non_nullable
              as int,
      cuisine: null == cuisine
          ? _self.cuisine
          : cuisine // ignore: cast_nullable_to_non_nullable
              as String,
      difficulty: null == difficulty
          ? _self.difficulty
          : difficulty // ignore: cast_nullable_to_non_nullable
              as String,
      imageUrl: freezed == imageUrl
          ? _self.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String?,
      nutritionPerServing: freezed == nutritionPerServing
          ? _self.nutritionPerServing
          : nutritionPerServing // ignore: cast_nullable_to_non_nullable
              as MacrosDto?,
      ingredients: null == ingredients
          ? _self._ingredients
          : ingredients // ignore: cast_nullable_to_non_nullable
              as List<DishIngredientDto>,
      steps: null == steps
          ? _self._steps
          : steps // ignore: cast_nullable_to_non_nullable
              as List<CookingStepDto>,
    ));
  }

  /// Create a copy of DishDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $MacrosDtoCopyWith<$Res>? get nutritionPerServing {
    if (_self.nutritionPerServing == null) {
      return null;
    }

    return $MacrosDtoCopyWith<$Res>(_self.nutritionPerServing!, (value) {
      return _then(_self.copyWith(nutritionPerServing: value));
    });
  }
}

/// @nodoc
mixin _$DishIngredientDto {
  String get name;
  double get quantity;
  String get unit;
  @JsonKey(name: 'is_seasoning')
  bool get isSeasoning;
  @JsonKey(name: 'available_in_pantry')
  bool get availableInPantry;
  @JsonKey(name: 'missing_qty')
  double get missingQty;
  @JsonKey(name: 'near_expiry')
  bool get nearExpiry;
  @JsonKey(name: 'pantry_item_id')
  String? get pantryItemId;

  /// Create a copy of DishIngredientDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $DishIngredientDtoCopyWith<DishIngredientDto> get copyWith =>
      _$DishIngredientDtoCopyWithImpl<DishIngredientDto>(
          this as DishIngredientDto, _$identity);

  /// Serializes this DishIngredientDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is DishIngredientDto &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.quantity, quantity) ||
                other.quantity == quantity) &&
            (identical(other.unit, unit) || other.unit == unit) &&
            (identical(other.isSeasoning, isSeasoning) ||
                other.isSeasoning == isSeasoning) &&
            (identical(other.availableInPantry, availableInPantry) ||
                other.availableInPantry == availableInPantry) &&
            (identical(other.missingQty, missingQty) ||
                other.missingQty == missingQty) &&
            (identical(other.nearExpiry, nearExpiry) ||
                other.nearExpiry == nearExpiry) &&
            (identical(other.pantryItemId, pantryItemId) ||
                other.pantryItemId == pantryItemId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, name, quantity, unit,
      isSeasoning, availableInPantry, missingQty, nearExpiry, pantryItemId);

  @override
  String toString() {
    return 'DishIngredientDto(name: $name, quantity: $quantity, unit: $unit, isSeasoning: $isSeasoning, availableInPantry: $availableInPantry, missingQty: $missingQty, nearExpiry: $nearExpiry, pantryItemId: $pantryItemId)';
  }
}

/// @nodoc
abstract mixin class $DishIngredientDtoCopyWith<$Res> {
  factory $DishIngredientDtoCopyWith(
          DishIngredientDto value, $Res Function(DishIngredientDto) _then) =
      _$DishIngredientDtoCopyWithImpl;
  @useResult
  $Res call(
      {String name,
      double quantity,
      String unit,
      @JsonKey(name: 'is_seasoning') bool isSeasoning,
      @JsonKey(name: 'available_in_pantry') bool availableInPantry,
      @JsonKey(name: 'missing_qty') double missingQty,
      @JsonKey(name: 'near_expiry') bool nearExpiry,
      @JsonKey(name: 'pantry_item_id') String? pantryItemId});
}

/// @nodoc
class _$DishIngredientDtoCopyWithImpl<$Res>
    implements $DishIngredientDtoCopyWith<$Res> {
  _$DishIngredientDtoCopyWithImpl(this._self, this._then);

  final DishIngredientDto _self;
  final $Res Function(DishIngredientDto) _then;

  /// Create a copy of DishIngredientDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? quantity = null,
    Object? unit = null,
    Object? isSeasoning = null,
    Object? availableInPantry = null,
    Object? missingQty = null,
    Object? nearExpiry = null,
    Object? pantryItemId = freezed,
  }) {
    return _then(_self.copyWith(
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      quantity: null == quantity
          ? _self.quantity
          : quantity // ignore: cast_nullable_to_non_nullable
              as double,
      unit: null == unit
          ? _self.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      isSeasoning: null == isSeasoning
          ? _self.isSeasoning
          : isSeasoning // ignore: cast_nullable_to_non_nullable
              as bool,
      availableInPantry: null == availableInPantry
          ? _self.availableInPantry
          : availableInPantry // ignore: cast_nullable_to_non_nullable
              as bool,
      missingQty: null == missingQty
          ? _self.missingQty
          : missingQty // ignore: cast_nullable_to_non_nullable
              as double,
      nearExpiry: null == nearExpiry
          ? _self.nearExpiry
          : nearExpiry // ignore: cast_nullable_to_non_nullable
              as bool,
      pantryItemId: freezed == pantryItemId
          ? _self.pantryItemId
          : pantryItemId // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// Adds pattern-matching-related methods to [DishIngredientDto].
extension DishIngredientDtoPatterns on DishIngredientDto {
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
    TResult Function(_DishIngredientDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _DishIngredientDto() when $default != null:
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
    TResult Function(_DishIngredientDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _DishIngredientDto():
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
    TResult? Function(_DishIngredientDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _DishIngredientDto() when $default != null:
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
            double quantity,
            String unit,
            @JsonKey(name: 'is_seasoning') bool isSeasoning,
            @JsonKey(name: 'available_in_pantry') bool availableInPantry,
            @JsonKey(name: 'missing_qty') double missingQty,
            @JsonKey(name: 'near_expiry') bool nearExpiry,
            @JsonKey(name: 'pantry_item_id') String? pantryItemId)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _DishIngredientDto() when $default != null:
        return $default(
            _that.name,
            _that.quantity,
            _that.unit,
            _that.isSeasoning,
            _that.availableInPantry,
            _that.missingQty,
            _that.nearExpiry,
            _that.pantryItemId);
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
            double quantity,
            String unit,
            @JsonKey(name: 'is_seasoning') bool isSeasoning,
            @JsonKey(name: 'available_in_pantry') bool availableInPantry,
            @JsonKey(name: 'missing_qty') double missingQty,
            @JsonKey(name: 'near_expiry') bool nearExpiry,
            @JsonKey(name: 'pantry_item_id') String? pantryItemId)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _DishIngredientDto():
        return $default(
            _that.name,
            _that.quantity,
            _that.unit,
            _that.isSeasoning,
            _that.availableInPantry,
            _that.missingQty,
            _that.nearExpiry,
            _that.pantryItemId);
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
            double quantity,
            String unit,
            @JsonKey(name: 'is_seasoning') bool isSeasoning,
            @JsonKey(name: 'available_in_pantry') bool availableInPantry,
            @JsonKey(name: 'missing_qty') double missingQty,
            @JsonKey(name: 'near_expiry') bool nearExpiry,
            @JsonKey(name: 'pantry_item_id') String? pantryItemId)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _DishIngredientDto() when $default != null:
        return $default(
            _that.name,
            _that.quantity,
            _that.unit,
            _that.isSeasoning,
            _that.availableInPantry,
            _that.missingQty,
            _that.nearExpiry,
            _that.pantryItemId);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _DishIngredientDto extends DishIngredientDto {
  const _DishIngredientDto(
      {required this.name,
      this.quantity = 0,
      this.unit = 'g',
      @JsonKey(name: 'is_seasoning') this.isSeasoning = false,
      @JsonKey(name: 'available_in_pantry') this.availableInPantry = false,
      @JsonKey(name: 'missing_qty') this.missingQty = 0,
      @JsonKey(name: 'near_expiry') this.nearExpiry = false,
      @JsonKey(name: 'pantry_item_id') this.pantryItemId})
      : super._();
  factory _DishIngredientDto.fromJson(Map<String, dynamic> json) =>
      _$DishIngredientDtoFromJson(json);

  @override
  final String name;
  @override
  @JsonKey()
  final double quantity;
  @override
  @JsonKey()
  final String unit;
  @override
  @JsonKey(name: 'is_seasoning')
  final bool isSeasoning;
  @override
  @JsonKey(name: 'available_in_pantry')
  final bool availableInPantry;
  @override
  @JsonKey(name: 'missing_qty')
  final double missingQty;
  @override
  @JsonKey(name: 'near_expiry')
  final bool nearExpiry;
  @override
  @JsonKey(name: 'pantry_item_id')
  final String? pantryItemId;

  /// Create a copy of DishIngredientDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$DishIngredientDtoCopyWith<_DishIngredientDto> get copyWith =>
      __$DishIngredientDtoCopyWithImpl<_DishIngredientDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$DishIngredientDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _DishIngredientDto &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.quantity, quantity) ||
                other.quantity == quantity) &&
            (identical(other.unit, unit) || other.unit == unit) &&
            (identical(other.isSeasoning, isSeasoning) ||
                other.isSeasoning == isSeasoning) &&
            (identical(other.availableInPantry, availableInPantry) ||
                other.availableInPantry == availableInPantry) &&
            (identical(other.missingQty, missingQty) ||
                other.missingQty == missingQty) &&
            (identical(other.nearExpiry, nearExpiry) ||
                other.nearExpiry == nearExpiry) &&
            (identical(other.pantryItemId, pantryItemId) ||
                other.pantryItemId == pantryItemId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, name, quantity, unit,
      isSeasoning, availableInPantry, missingQty, nearExpiry, pantryItemId);

  @override
  String toString() {
    return 'DishIngredientDto(name: $name, quantity: $quantity, unit: $unit, isSeasoning: $isSeasoning, availableInPantry: $availableInPantry, missingQty: $missingQty, nearExpiry: $nearExpiry, pantryItemId: $pantryItemId)';
  }
}

/// @nodoc
abstract mixin class _$DishIngredientDtoCopyWith<$Res>
    implements $DishIngredientDtoCopyWith<$Res> {
  factory _$DishIngredientDtoCopyWith(
          _DishIngredientDto value, $Res Function(_DishIngredientDto) _then) =
      __$DishIngredientDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String name,
      double quantity,
      String unit,
      @JsonKey(name: 'is_seasoning') bool isSeasoning,
      @JsonKey(name: 'available_in_pantry') bool availableInPantry,
      @JsonKey(name: 'missing_qty') double missingQty,
      @JsonKey(name: 'near_expiry') bool nearExpiry,
      @JsonKey(name: 'pantry_item_id') String? pantryItemId});
}

/// @nodoc
class __$DishIngredientDtoCopyWithImpl<$Res>
    implements _$DishIngredientDtoCopyWith<$Res> {
  __$DishIngredientDtoCopyWithImpl(this._self, this._then);

  final _DishIngredientDto _self;
  final $Res Function(_DishIngredientDto) _then;

  /// Create a copy of DishIngredientDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? name = null,
    Object? quantity = null,
    Object? unit = null,
    Object? isSeasoning = null,
    Object? availableInPantry = null,
    Object? missingQty = null,
    Object? nearExpiry = null,
    Object? pantryItemId = freezed,
  }) {
    return _then(_DishIngredientDto(
      name: null == name
          ? _self.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      quantity: null == quantity
          ? _self.quantity
          : quantity // ignore: cast_nullable_to_non_nullable
              as double,
      unit: null == unit
          ? _self.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      isSeasoning: null == isSeasoning
          ? _self.isSeasoning
          : isSeasoning // ignore: cast_nullable_to_non_nullable
              as bool,
      availableInPantry: null == availableInPantry
          ? _self.availableInPantry
          : availableInPantry // ignore: cast_nullable_to_non_nullable
              as bool,
      missingQty: null == missingQty
          ? _self.missingQty
          : missingQty // ignore: cast_nullable_to_non_nullable
              as double,
      nearExpiry: null == nearExpiry
          ? _self.nearExpiry
          : nearExpiry // ignore: cast_nullable_to_non_nullable
              as bool,
      pantryItemId: freezed == pantryItemId
          ? _self.pantryItemId
          : pantryItemId // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
mixin _$CookingStepDto {
  int get order;
  String get text;
  @JsonKey(name: 'duration_min')
  int? get durationMin;

  /// Create a copy of CookingStepDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $CookingStepDtoCopyWith<CookingStepDto> get copyWith =>
      _$CookingStepDtoCopyWithImpl<CookingStepDto>(
          this as CookingStepDto, _$identity);

  /// Serializes this CookingStepDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is CookingStepDto &&
            (identical(other.order, order) || other.order == order) &&
            (identical(other.text, text) || other.text == text) &&
            (identical(other.durationMin, durationMin) ||
                other.durationMin == durationMin));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, order, text, durationMin);

  @override
  String toString() {
    return 'CookingStepDto(order: $order, text: $text, durationMin: $durationMin)';
  }
}

/// @nodoc
abstract mixin class $CookingStepDtoCopyWith<$Res> {
  factory $CookingStepDtoCopyWith(
          CookingStepDto value, $Res Function(CookingStepDto) _then) =
      _$CookingStepDtoCopyWithImpl;
  @useResult
  $Res call(
      {int order,
      String text,
      @JsonKey(name: 'duration_min') int? durationMin});
}

/// @nodoc
class _$CookingStepDtoCopyWithImpl<$Res>
    implements $CookingStepDtoCopyWith<$Res> {
  _$CookingStepDtoCopyWithImpl(this._self, this._then);

  final CookingStepDto _self;
  final $Res Function(CookingStepDto) _then;

  /// Create a copy of CookingStepDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? order = null,
    Object? text = null,
    Object? durationMin = freezed,
  }) {
    return _then(_self.copyWith(
      order: null == order
          ? _self.order
          : order // ignore: cast_nullable_to_non_nullable
              as int,
      text: null == text
          ? _self.text
          : text // ignore: cast_nullable_to_non_nullable
              as String,
      durationMin: freezed == durationMin
          ? _self.durationMin
          : durationMin // ignore: cast_nullable_to_non_nullable
              as int?,
    ));
  }
}

/// Adds pattern-matching-related methods to [CookingStepDto].
extension CookingStepDtoPatterns on CookingStepDto {
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
    TResult Function(_CookingStepDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _CookingStepDto() when $default != null:
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
    TResult Function(_CookingStepDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookingStepDto():
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
    TResult? Function(_CookingStepDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookingStepDto() when $default != null:
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
    TResult Function(int order, String text,
            @JsonKey(name: 'duration_min') int? durationMin)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _CookingStepDto() when $default != null:
        return $default(_that.order, _that.text, _that.durationMin);
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
    TResult Function(int order, String text,
            @JsonKey(name: 'duration_min') int? durationMin)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookingStepDto():
        return $default(_that.order, _that.text, _that.durationMin);
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
    TResult? Function(int order, String text,
            @JsonKey(name: 'duration_min') int? durationMin)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _CookingStepDto() when $default != null:
        return $default(_that.order, _that.text, _that.durationMin);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _CookingStepDto extends CookingStepDto {
  const _CookingStepDto(
      {required this.order,
      required this.text,
      @JsonKey(name: 'duration_min') this.durationMin})
      : super._();
  factory _CookingStepDto.fromJson(Map<String, dynamic> json) =>
      _$CookingStepDtoFromJson(json);

  @override
  final int order;
  @override
  final String text;
  @override
  @JsonKey(name: 'duration_min')
  final int? durationMin;

  /// Create a copy of CookingStepDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$CookingStepDtoCopyWith<_CookingStepDto> get copyWith =>
      __$CookingStepDtoCopyWithImpl<_CookingStepDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$CookingStepDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _CookingStepDto &&
            (identical(other.order, order) || other.order == order) &&
            (identical(other.text, text) || other.text == text) &&
            (identical(other.durationMin, durationMin) ||
                other.durationMin == durationMin));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, order, text, durationMin);

  @override
  String toString() {
    return 'CookingStepDto(order: $order, text: $text, durationMin: $durationMin)';
  }
}

/// @nodoc
abstract mixin class _$CookingStepDtoCopyWith<$Res>
    implements $CookingStepDtoCopyWith<$Res> {
  factory _$CookingStepDtoCopyWith(
          _CookingStepDto value, $Res Function(_CookingStepDto) _then) =
      __$CookingStepDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {int order,
      String text,
      @JsonKey(name: 'duration_min') int? durationMin});
}

/// @nodoc
class __$CookingStepDtoCopyWithImpl<$Res>
    implements _$CookingStepDtoCopyWith<$Res> {
  __$CookingStepDtoCopyWithImpl(this._self, this._then);

  final _CookingStepDto _self;
  final $Res Function(_CookingStepDto) _then;

  /// Create a copy of CookingStepDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? order = null,
    Object? text = null,
    Object? durationMin = freezed,
  }) {
    return _then(_CookingStepDto(
      order: null == order
          ? _self.order
          : order // ignore: cast_nullable_to_non_nullable
              as int,
      text: null == text
          ? _self.text
          : text // ignore: cast_nullable_to_non_nullable
              as String,
      durationMin: freezed == durationMin
          ? _self.durationMin
          : durationMin // ignore: cast_nullable_to_non_nullable
              as int?,
    ));
  }
}

/// @nodoc
mixin _$MacrosDto {
  @JsonKey(name: 'energy_kcal')
  double get energyKcal;
  @JsonKey(name: 'protein_g')
  double get proteinG;
  @JsonKey(name: 'carb_g')
  double get carbG;
  @JsonKey(name: 'lipid_g')
  double get lipidG;

  /// Create a copy of MacrosDto
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $MacrosDtoCopyWith<MacrosDto> get copyWith =>
      _$MacrosDtoCopyWithImpl<MacrosDto>(this as MacrosDto, _$identity);

  /// Serializes this MacrosDto to a JSON map.
  Map<String, dynamic> toJson();

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is MacrosDto &&
            (identical(other.energyKcal, energyKcal) ||
                other.energyKcal == energyKcal) &&
            (identical(other.proteinG, proteinG) ||
                other.proteinG == proteinG) &&
            (identical(other.carbG, carbG) || other.carbG == carbG) &&
            (identical(other.lipidG, lipidG) || other.lipidG == lipidG));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, energyKcal, proteinG, carbG, lipidG);

  @override
  String toString() {
    return 'MacrosDto(energyKcal: $energyKcal, proteinG: $proteinG, carbG: $carbG, lipidG: $lipidG)';
  }
}

/// @nodoc
abstract mixin class $MacrosDtoCopyWith<$Res> {
  factory $MacrosDtoCopyWith(MacrosDto value, $Res Function(MacrosDto) _then) =
      _$MacrosDtoCopyWithImpl;
  @useResult
  $Res call(
      {@JsonKey(name: 'energy_kcal') double energyKcal,
      @JsonKey(name: 'protein_g') double proteinG,
      @JsonKey(name: 'carb_g') double carbG,
      @JsonKey(name: 'lipid_g') double lipidG});
}

/// @nodoc
class _$MacrosDtoCopyWithImpl<$Res> implements $MacrosDtoCopyWith<$Res> {
  _$MacrosDtoCopyWithImpl(this._self, this._then);

  final MacrosDto _self;
  final $Res Function(MacrosDto) _then;

  /// Create a copy of MacrosDto
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? energyKcal = null,
    Object? proteinG = null,
    Object? carbG = null,
    Object? lipidG = null,
  }) {
    return _then(_self.copyWith(
      energyKcal: null == energyKcal
          ? _self.energyKcal
          : energyKcal // ignore: cast_nullable_to_non_nullable
              as double,
      proteinG: null == proteinG
          ? _self.proteinG
          : proteinG // ignore: cast_nullable_to_non_nullable
              as double,
      carbG: null == carbG
          ? _self.carbG
          : carbG // ignore: cast_nullable_to_non_nullable
              as double,
      lipidG: null == lipidG
          ? _self.lipidG
          : lipidG // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// Adds pattern-matching-related methods to [MacrosDto].
extension MacrosDtoPatterns on MacrosDto {
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
    TResult Function(_MacrosDto value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _MacrosDto() when $default != null:
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
    TResult Function(_MacrosDto value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _MacrosDto():
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
    TResult? Function(_MacrosDto value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _MacrosDto() when $default != null:
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
            @JsonKey(name: 'energy_kcal') double energyKcal,
            @JsonKey(name: 'protein_g') double proteinG,
            @JsonKey(name: 'carb_g') double carbG,
            @JsonKey(name: 'lipid_g') double lipidG)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _MacrosDto() when $default != null:
        return $default(
            _that.energyKcal, _that.proteinG, _that.carbG, _that.lipidG);
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
            @JsonKey(name: 'energy_kcal') double energyKcal,
            @JsonKey(name: 'protein_g') double proteinG,
            @JsonKey(name: 'carb_g') double carbG,
            @JsonKey(name: 'lipid_g') double lipidG)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _MacrosDto():
        return $default(
            _that.energyKcal, _that.proteinG, _that.carbG, _that.lipidG);
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
            @JsonKey(name: 'energy_kcal') double energyKcal,
            @JsonKey(name: 'protein_g') double proteinG,
            @JsonKey(name: 'carb_g') double carbG,
            @JsonKey(name: 'lipid_g') double lipidG)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _MacrosDto() when $default != null:
        return $default(
            _that.energyKcal, _that.proteinG, _that.carbG, _that.lipidG);
      case _:
        return null;
    }
  }
}

/// @nodoc
@JsonSerializable()
class _MacrosDto extends MacrosDto {
  const _MacrosDto(
      {@JsonKey(name: 'energy_kcal') this.energyKcal = 0,
      @JsonKey(name: 'protein_g') this.proteinG = 0,
      @JsonKey(name: 'carb_g') this.carbG = 0,
      @JsonKey(name: 'lipid_g') this.lipidG = 0})
      : super._();
  factory _MacrosDto.fromJson(Map<String, dynamic> json) =>
      _$MacrosDtoFromJson(json);

  @override
  @JsonKey(name: 'energy_kcal')
  final double energyKcal;
  @override
  @JsonKey(name: 'protein_g')
  final double proteinG;
  @override
  @JsonKey(name: 'carb_g')
  final double carbG;
  @override
  @JsonKey(name: 'lipid_g')
  final double lipidG;

  /// Create a copy of MacrosDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$MacrosDtoCopyWith<_MacrosDto> get copyWith =>
      __$MacrosDtoCopyWithImpl<_MacrosDto>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$MacrosDtoToJson(
      this,
    );
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _MacrosDto &&
            (identical(other.energyKcal, energyKcal) ||
                other.energyKcal == energyKcal) &&
            (identical(other.proteinG, proteinG) ||
                other.proteinG == proteinG) &&
            (identical(other.carbG, carbG) || other.carbG == carbG) &&
            (identical(other.lipidG, lipidG) || other.lipidG == lipidG));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, energyKcal, proteinG, carbG, lipidG);

  @override
  String toString() {
    return 'MacrosDto(energyKcal: $energyKcal, proteinG: $proteinG, carbG: $carbG, lipidG: $lipidG)';
  }
}

/// @nodoc
abstract mixin class _$MacrosDtoCopyWith<$Res>
    implements $MacrosDtoCopyWith<$Res> {
  factory _$MacrosDtoCopyWith(
          _MacrosDto value, $Res Function(_MacrosDto) _then) =
      __$MacrosDtoCopyWithImpl;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'energy_kcal') double energyKcal,
      @JsonKey(name: 'protein_g') double proteinG,
      @JsonKey(name: 'carb_g') double carbG,
      @JsonKey(name: 'lipid_g') double lipidG});
}

/// @nodoc
class __$MacrosDtoCopyWithImpl<$Res> implements _$MacrosDtoCopyWith<$Res> {
  __$MacrosDtoCopyWithImpl(this._self, this._then);

  final _MacrosDto _self;
  final $Res Function(_MacrosDto) _then;

  /// Create a copy of MacrosDto
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? energyKcal = null,
    Object? proteinG = null,
    Object? carbG = null,
    Object? lipidG = null,
  }) {
    return _then(_MacrosDto(
      energyKcal: null == energyKcal
          ? _self.energyKcal
          : energyKcal // ignore: cast_nullable_to_non_nullable
              as double,
      proteinG: null == proteinG
          ? _self.proteinG
          : proteinG // ignore: cast_nullable_to_non_nullable
              as double,
      carbG: null == carbG
          ? _self.carbG
          : carbG // ignore: cast_nullable_to_non_nullable
              as double,
      lipidG: null == lipidG
          ? _self.lipidG
          : lipidG // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

// dart format on
