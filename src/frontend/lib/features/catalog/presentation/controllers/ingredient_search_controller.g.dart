// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ingredient_search_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Autocomplete results for [query] (K-03). Empty query → a short popular list.

@ProviderFor(ingredientSearch)
final ingredientSearchProvider = IngredientSearchFamily._();

/// Autocomplete results for [query] (K-03). Empty query → a short popular list.

final class IngredientSearchProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Ingredient>>,
          List<Ingredient>,
          FutureOr<List<Ingredient>>
        >
    with $FutureModifier<List<Ingredient>>, $FutureProvider<List<Ingredient>> {
  /// Autocomplete results for [query] (K-03). Empty query → a short popular list.
  IngredientSearchProvider._({
    required IngredientSearchFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'ingredientSearchProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$ingredientSearchHash();

  @override
  String toString() {
    return r'ingredientSearchProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<List<Ingredient>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Ingredient>> create(Ref ref) {
    final argument = this.argument as String;
    return ingredientSearch(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is IngredientSearchProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$ingredientSearchHash() => r'9ae48e3edd734f75088759a3b40d9c1bfc3f49c4';

/// Autocomplete results for [query] (K-03). Empty query → a short popular list.

final class IngredientSearchFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<List<Ingredient>>, String> {
  IngredientSearchFamily._()
    : super(
        retry: null,
        name: r'ingredientSearchProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Autocomplete results for [query] (K-03). Empty query → a short popular list.

  IngredientSearchProvider call(String query) =>
      IngredientSearchProvider._(argument: query, from: this);

  @override
  String toString() => r'ingredientSearchProvider';
}
