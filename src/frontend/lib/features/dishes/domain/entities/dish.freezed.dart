// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'dish.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Dish {
  String get id;
  String get name;
  int get servings;
  int get prepTimeMin;
  int get cookTimeMin;
  NutritionInfo get nutritionPerServing;
  String get cuisine;
  String get difficulty;
  String? get imageUrl;
  List<DishIngredient> get ingredients;
  List<CookingStep> get steps;

  /// Create a copy of Dish
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  $DishCopyWith<Dish> get copyWith =>
      _$DishCopyWithImpl<Dish>(this as Dish, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is Dish &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.servings, servings) ||
                other.servings == servings) &&
            (identical(other.prepTimeMin, prepTimeMin) ||
                other.prepTimeMin == prepTimeMin) &&
            (identical(other.cookTimeMin, cookTimeMin) ||
                other.cookTimeMin == cookTimeMin) &&
            (identical(other.nutritionPerServing, nutritionPerServing) ||
                other.nutritionPerServing == nutritionPerServing) &&
            (identical(other.cuisine, cuisine) || other.cuisine == cuisine) &&
            (identical(other.difficulty, difficulty) ||
                other.difficulty == difficulty) &&
            (identical(other.imageUrl, imageUrl) ||
                other.imageUrl == imageUrl) &&
            const DeepCollectionEquality()
                .equals(other.ingredients, ingredients) &&
            const DeepCollectionEquality().equals(other.steps, steps));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      name,
      servings,
      prepTimeMin,
      cookTimeMin,
      nutritionPerServing,
      cuisine,
      difficulty,
      imageUrl,
      const DeepCollectionEquality().hash(ingredients),
      const DeepCollectionEquality().hash(steps));

  @override
  String toString() {
    return 'Dish(id: $id, name: $name, servings: $servings, prepTimeMin: $prepTimeMin, cookTimeMin: $cookTimeMin, nutritionPerServing: $nutritionPerServing, cuisine: $cuisine, difficulty: $difficulty, imageUrl: $imageUrl, ingredients: $ingredients, steps: $steps)';
  }
}

/// @nodoc
abstract mixin class $DishCopyWith<$Res> {
  factory $DishCopyWith(Dish value, $Res Function(Dish) _then) =
      _$DishCopyWithImpl;
  @useResult
  $Res call(
      {String id,
      String name,
      int servings,
      int prepTimeMin,
      int cookTimeMin,
      NutritionInfo nutritionPerServing,
      String cuisine,
      String difficulty,
      String? imageUrl,
      List<DishIngredient> ingredients,
      List<CookingStep> steps});
}

/// @nodoc
class _$DishCopyWithImpl<$Res> implements $DishCopyWith<$Res> {
  _$DishCopyWithImpl(this._self, this._then);

  final Dish _self;
  final $Res Function(Dish) _then;

  /// Create a copy of Dish
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? servings = null,
    Object? prepTimeMin = null,
    Object? cookTimeMin = null,
    Object? nutritionPerServing = null,
    Object? cuisine = null,
    Object? difficulty = null,
    Object? imageUrl = freezed,
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
      nutritionPerServing: null == nutritionPerServing
          ? _self.nutritionPerServing
          : nutritionPerServing // ignore: cast_nullable_to_non_nullable
              as NutritionInfo,
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
      ingredients: null == ingredients
          ? _self.ingredients
          : ingredients // ignore: cast_nullable_to_non_nullable
              as List<DishIngredient>,
      steps: null == steps
          ? _self.steps
          : steps // ignore: cast_nullable_to_non_nullable
              as List<CookingStep>,
    ));
  }
}

/// Adds pattern-matching-related methods to [Dish].
extension DishPatterns on Dish {
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
    TResult Function(_Dish value)? $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _Dish() when $default != null:
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
    TResult Function(_Dish value) $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Dish():
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
    TResult? Function(_Dish value)? $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Dish() when $default != null:
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
            int prepTimeMin,
            int cookTimeMin,
            NutritionInfo nutritionPerServing,
            String cuisine,
            String difficulty,
            String? imageUrl,
            List<DishIngredient> ingredients,
            List<CookingStep> steps)?
        $default, {
    required TResult orElse(),
  }) {
    final _that = this;
    switch (_that) {
      case _Dish() when $default != null:
        return $default(
            _that.id,
            _that.name,
            _that.servings,
            _that.prepTimeMin,
            _that.cookTimeMin,
            _that.nutritionPerServing,
            _that.cuisine,
            _that.difficulty,
            _that.imageUrl,
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
            int prepTimeMin,
            int cookTimeMin,
            NutritionInfo nutritionPerServing,
            String cuisine,
            String difficulty,
            String? imageUrl,
            List<DishIngredient> ingredients,
            List<CookingStep> steps)
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Dish():
        return $default(
            _that.id,
            _that.name,
            _that.servings,
            _that.prepTimeMin,
            _that.cookTimeMin,
            _that.nutritionPerServing,
            _that.cuisine,
            _that.difficulty,
            _that.imageUrl,
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
            int prepTimeMin,
            int cookTimeMin,
            NutritionInfo nutritionPerServing,
            String cuisine,
            String difficulty,
            String? imageUrl,
            List<DishIngredient> ingredients,
            List<CookingStep> steps)?
        $default,
  ) {
    final _that = this;
    switch (_that) {
      case _Dish() when $default != null:
        return $default(
            _that.id,
            _that.name,
            _that.servings,
            _that.prepTimeMin,
            _that.cookTimeMin,
            _that.nutritionPerServing,
            _that.cuisine,
            _that.difficulty,
            _that.imageUrl,
            _that.ingredients,
            _that.steps);
      case _:
        return null;
    }
  }
}

/// @nodoc

class _Dish extends Dish {
  const _Dish(
      {required this.id,
      required this.name,
      required this.servings,
      required this.prepTimeMin,
      required this.cookTimeMin,
      required this.nutritionPerServing,
      this.cuisine = '',
      this.difficulty = '',
      this.imageUrl,
      final List<DishIngredient> ingredients = const <DishIngredient>[],
      final List<CookingStep> steps = const <CookingStep>[]})
      : _ingredients = ingredients,
        _steps = steps,
        super._();

  @override
  final String id;
  @override
  final String name;
  @override
  final int servings;
  @override
  final int prepTimeMin;
  @override
  final int cookTimeMin;
  @override
  final NutritionInfo nutritionPerServing;
  @override
  @JsonKey()
  final String cuisine;
  @override
  @JsonKey()
  final String difficulty;
  @override
  final String? imageUrl;
  final List<DishIngredient> _ingredients;
  @override
  @JsonKey()
  List<DishIngredient> get ingredients {
    if (_ingredients is EqualUnmodifiableListView) return _ingredients;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_ingredients);
  }

  final List<CookingStep> _steps;
  @override
  @JsonKey()
  List<CookingStep> get steps {
    if (_steps is EqualUnmodifiableListView) return _steps;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_steps);
  }

  /// Create a copy of Dish
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  @pragma('vm:prefer-inline')
  _$DishCopyWith<_Dish> get copyWith =>
      __$DishCopyWithImpl<_Dish>(this, _$identity);

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _Dish &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.servings, servings) ||
                other.servings == servings) &&
            (identical(other.prepTimeMin, prepTimeMin) ||
                other.prepTimeMin == prepTimeMin) &&
            (identical(other.cookTimeMin, cookTimeMin) ||
                other.cookTimeMin == cookTimeMin) &&
            (identical(other.nutritionPerServing, nutritionPerServing) ||
                other.nutritionPerServing == nutritionPerServing) &&
            (identical(other.cuisine, cuisine) || other.cuisine == cuisine) &&
            (identical(other.difficulty, difficulty) ||
                other.difficulty == difficulty) &&
            (identical(other.imageUrl, imageUrl) ||
                other.imageUrl == imageUrl) &&
            const DeepCollectionEquality()
                .equals(other._ingredients, _ingredients) &&
            const DeepCollectionEquality().equals(other._steps, _steps));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      name,
      servings,
      prepTimeMin,
      cookTimeMin,
      nutritionPerServing,
      cuisine,
      difficulty,
      imageUrl,
      const DeepCollectionEquality().hash(_ingredients),
      const DeepCollectionEquality().hash(_steps));

  @override
  String toString() {
    return 'Dish(id: $id, name: $name, servings: $servings, prepTimeMin: $prepTimeMin, cookTimeMin: $cookTimeMin, nutritionPerServing: $nutritionPerServing, cuisine: $cuisine, difficulty: $difficulty, imageUrl: $imageUrl, ingredients: $ingredients, steps: $steps)';
  }
}

/// @nodoc
abstract mixin class _$DishCopyWith<$Res> implements $DishCopyWith<$Res> {
  factory _$DishCopyWith(_Dish value, $Res Function(_Dish) _then) =
      __$DishCopyWithImpl;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      int servings,
      int prepTimeMin,
      int cookTimeMin,
      NutritionInfo nutritionPerServing,
      String cuisine,
      String difficulty,
      String? imageUrl,
      List<DishIngredient> ingredients,
      List<CookingStep> steps});
}

/// @nodoc
class __$DishCopyWithImpl<$Res> implements _$DishCopyWith<$Res> {
  __$DishCopyWithImpl(this._self, this._then);

  final _Dish _self;
  final $Res Function(_Dish) _then;

  /// Create a copy of Dish
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? servings = null,
    Object? prepTimeMin = null,
    Object? cookTimeMin = null,
    Object? nutritionPerServing = null,
    Object? cuisine = null,
    Object? difficulty = null,
    Object? imageUrl = freezed,
    Object? ingredients = null,
    Object? steps = null,
  }) {
    return _then(_Dish(
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
      nutritionPerServing: null == nutritionPerServing
          ? _self.nutritionPerServing
          : nutritionPerServing // ignore: cast_nullable_to_non_nullable
              as NutritionInfo,
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
      ingredients: null == ingredients
          ? _self._ingredients
          : ingredients // ignore: cast_nullable_to_non_nullable
              as List<DishIngredient>,
      steps: null == steps
          ? _self._steps
          : steps // ignore: cast_nullable_to_non_nullable
              as List<CookingStep>,
    ));
  }
}

// dart format on
