// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pantry_list_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(PantryFilterController)
final pantryFilterControllerProvider = PantryFilterControllerProvider._();

final class PantryFilterControllerProvider
    extends $NotifierProvider<PantryFilterController, PantryFilter> {
  PantryFilterControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'pantryFilterControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$pantryFilterControllerHash();

  @$internal
  @override
  PantryFilterController create() => PantryFilterController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(PantryFilter value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<PantryFilter>(value),
    );
  }
}

String _$pantryFilterControllerHash() =>
    r'e83bad1e3d3737ccab0eb2be0289e7e35826a476';

abstract class _$PantryFilterController extends $Notifier<PantryFilter> {
  PantryFilter build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<PantryFilter, PantryFilter>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<PantryFilter, PantryFilter>,
              PantryFilter,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// Loads the full active pantry list (mock returns everything) and owns the
/// mutations. Filtering/sorting is applied client-side by [pantryListView].

@ProviderFor(PantryListController)
final pantryListControllerProvider = PantryListControllerProvider._();

/// Loads the full active pantry list (mock returns everything) and owns the
/// mutations. Filtering/sorting is applied client-side by [pantryListView].
final class PantryListControllerProvider
    extends $AsyncNotifierProvider<PantryListController, List<PantryItem>> {
  /// Loads the full active pantry list (mock returns everything) and owns the
  /// mutations. Filtering/sorting is applied client-side by [pantryListView].
  PantryListControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'pantryListControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$pantryListControllerHash();

  @$internal
  @override
  PantryListController create() => PantryListController();
}

String _$pantryListControllerHash() =>
    r'4d0ab01c107040b1e64de6d821e67a1a19ef3e58';

/// Loads the full active pantry list (mock returns everything) and owns the
/// mutations. Filtering/sorting is applied client-side by [pantryListView].

abstract class _$PantryListController extends $AsyncNotifier<List<PantryItem>> {
  FutureOr<List<PantryItem>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<List<PantryItem>>, List<PantryItem>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<PantryItem>>, List<PantryItem>>,
              AsyncValue<List<PantryItem>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// The filtered + sorted list the K-01 screen renders.

@ProviderFor(pantryListView)
final pantryListViewProvider = PantryListViewProvider._();

/// The filtered + sorted list the K-01 screen renders.

final class PantryListViewProvider
    extends
        $FunctionalProvider<
          List<PantryItem>,
          List<PantryItem>,
          List<PantryItem>
        >
    with $Provider<List<PantryItem>> {
  /// The filtered + sorted list the K-01 screen renders.
  PantryListViewProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'pantryListViewProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$pantryListViewHash();

  @$internal
  @override
  $ProviderElement<List<PantryItem>> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  List<PantryItem> create(Ref ref) {
    return pantryListView(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(List<PantryItem> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<List<PantryItem>>(value),
    );
  }
}

String _$pantryListViewHash() => r'a8f0676329f7ccb9f1ac4949e6d22779f07f82c4';

/// Per-tier counts for the segmented control chips.

@ProviderFor(pantryTierCounts)
final pantryTierCountsProvider = PantryTierCountsProvider._();

/// Per-tier counts for the segmented control chips.

final class PantryTierCountsProvider
    extends
        $FunctionalProvider<
          Map<StorageTier?, int>,
          Map<StorageTier?, int>,
          Map<StorageTier?, int>
        >
    with $Provider<Map<StorageTier?, int>> {
  /// Per-tier counts for the segmented control chips.
  PantryTierCountsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'pantryTierCountsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$pantryTierCountsHash();

  @$internal
  @override
  $ProviderElement<Map<StorageTier?, int>> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  Map<StorageTier?, int> create(Ref ref) {
    return pantryTierCounts(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(Map<StorageTier?, int> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<Map<StorageTier?, int>>(value),
    );
  }
}

String _$pantryTierCountsHash() => r'f6d3fb4034b792509b52a99e19a1387b3ae6dca6';

/// `GET /pantry/summary` (Home dashboard; also invalidated after mutations).

@ProviderFor(pantrySummary)
final pantrySummaryProvider = PantrySummaryProvider._();

/// `GET /pantry/summary` (Home dashboard; also invalidated after mutations).

final class PantrySummaryProvider
    extends
        $FunctionalProvider<
          AsyncValue<PantrySummary>,
          PantrySummary,
          FutureOr<PantrySummary>
        >
    with $FutureModifier<PantrySummary>, $FutureProvider<PantrySummary> {
  /// `GET /pantry/summary` (Home dashboard; also invalidated after mutations).
  PantrySummaryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'pantrySummaryProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$pantrySummaryHash();

  @$internal
  @override
  $FutureProviderElement<PantrySummary> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<PantrySummary> create(Ref ref) {
    return pantrySummary(ref);
  }
}

String _$pantrySummaryHash() => r'ebc24cbddc7f291d1ca0d90c68bc0a040310ff2c';
