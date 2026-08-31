// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'shopping_list_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// B-01 toggle: show the "đã có trong kho" lines or hide them (default hidden).

@ProviderFor(ShoppingListShowInStock)
final shoppingListShowInStockProvider = ShoppingListShowInStockProvider._();

/// B-01 toggle: show the "đã có trong kho" lines or hide them (default hidden).
final class ShoppingListShowInStockProvider
    extends $NotifierProvider<ShoppingListShowInStock, bool> {
  /// B-01 toggle: show the "đã có trong kho" lines or hide them (default hidden).
  ShoppingListShowInStockProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'shoppingListShowInStockProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$shoppingListShowInStockHash();

  @$internal
  @override
  ShoppingListShowInStock create() => ShoppingListShowInStock();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(bool value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<bool>(value),
    );
  }
}

String _$shoppingListShowInStockHash() =>
    r'c0fbd9725a2f1de9bb4791f6e5d7a595e2ed2764';

/// B-01 toggle: show the "đã có trong kho" lines or hide them (default hidden).

abstract class _$ShoppingListShowInStock extends $Notifier<bool> {
  bool build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<bool, bool>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<bool, bool>,
              bool,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// B-01. Loads the current list; check-off / add / remove update optimistically
/// and roll back on failure.

@ProviderFor(ShoppingListController)
final shoppingListControllerProvider = ShoppingListControllerProvider._();

/// B-01. Loads the current list; check-off / add / remove update optimistically
/// and roll back on failure.
final class ShoppingListControllerProvider
    extends $AsyncNotifierProvider<ShoppingListController, ShoppingList> {
  /// B-01. Loads the current list; check-off / add / remove update optimistically
  /// and roll back on failure.
  ShoppingListControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'shoppingListControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$shoppingListControllerHash();

  @$internal
  @override
  ShoppingListController create() => ShoppingListController();
}

String _$shoppingListControllerHash() =>
    r'f01ac3b3f8a34c5afc5ea19acd6a57b62efd811d';

/// B-01. Loads the current list; check-off / add / remove update optimistically
/// and roll back on failure.

abstract class _$ShoppingListController extends $AsyncNotifier<ShoppingList> {
  FutureOr<ShoppingList> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<ShoppingList>, ShoppingList>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<ShoppingList>, ShoppingList>,
              AsyncValue<ShoppingList>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
