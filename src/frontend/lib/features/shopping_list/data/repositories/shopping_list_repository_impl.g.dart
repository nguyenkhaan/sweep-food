// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'shopping_list_repository_impl.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(shoppingListRepository)
final shoppingListRepositoryProvider = ShoppingListRepositoryProvider._();

final class ShoppingListRepositoryProvider
    extends
        $FunctionalProvider<
          ShoppingListRepository,
          ShoppingListRepository,
          ShoppingListRepository
        >
    with $Provider<ShoppingListRepository> {
  ShoppingListRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'shoppingListRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$shoppingListRepositoryHash();

  @$internal
  @override
  $ProviderElement<ShoppingListRepository> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  ShoppingListRepository create(Ref ref) {
    return shoppingListRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ShoppingListRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ShoppingListRepository>(value),
    );
  }
}

String _$shoppingListRepositoryHash() =>
    r'08e305f710442b687a3419ebdfc3c749737e4cdd';
