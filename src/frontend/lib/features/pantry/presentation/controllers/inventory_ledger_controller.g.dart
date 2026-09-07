// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'inventory_ledger_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// K-04 — the inventory ledger (`GET /inventory/ledger`). Pass `batchId` to
/// scope it to one batch, or `null` for the whole pantry. Supports
/// incremental paging via [loadMore].

@ProviderFor(InventoryLedgerController)
final inventoryLedgerControllerProvider = InventoryLedgerControllerFamily._();

/// K-04 — the inventory ledger (`GET /inventory/ledger`). Pass `batchId` to
/// scope it to one batch, or `null` for the whole pantry. Supports
/// incremental paging via [loadMore].
final class InventoryLedgerControllerProvider
    extends
        $AsyncNotifierProvider<
          InventoryLedgerController,
          Paginated<InventoryLedgerEntry>
        > {
  /// K-04 — the inventory ledger (`GET /inventory/ledger`). Pass `batchId` to
  /// scope it to one batch, or `null` for the whole pantry. Supports
  /// incremental paging via [loadMore].
  InventoryLedgerControllerProvider._({
    required InventoryLedgerControllerFamily super.from,
    required String? super.argument,
  }) : super(
         retry: null,
         name: r'inventoryLedgerControllerProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$inventoryLedgerControllerHash();

  @override
  String toString() {
    return r'inventoryLedgerControllerProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  InventoryLedgerController create() => InventoryLedgerController();

  @override
  bool operator ==(Object other) {
    return other is InventoryLedgerControllerProvider &&
        other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$inventoryLedgerControllerHash() =>
    r'56c307b5bd49d1dcea6c50df2376a82f70db5943';

/// K-04 — the inventory ledger (`GET /inventory/ledger`). Pass `batchId` to
/// scope it to one batch, or `null` for the whole pantry. Supports
/// incremental paging via [loadMore].

final class InventoryLedgerControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          InventoryLedgerController,
          AsyncValue<Paginated<InventoryLedgerEntry>>,
          Paginated<InventoryLedgerEntry>,
          FutureOr<Paginated<InventoryLedgerEntry>>,
          String?
        > {
  InventoryLedgerControllerFamily._()
    : super(
        retry: null,
        name: r'inventoryLedgerControllerProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// K-04 — the inventory ledger (`GET /inventory/ledger`). Pass `batchId` to
  /// scope it to one batch, or `null` for the whole pantry. Supports
  /// incremental paging via [loadMore].

  InventoryLedgerControllerProvider call(String? batchId) =>
      InventoryLedgerControllerProvider._(argument: batchId, from: this);

  @override
  String toString() => r'inventoryLedgerControllerProvider';
}

/// K-04 — the inventory ledger (`GET /inventory/ledger`). Pass `batchId` to
/// scope it to one batch, or `null` for the whole pantry. Supports
/// incremental paging via [loadMore].

abstract class _$InventoryLedgerController
    extends $AsyncNotifier<Paginated<InventoryLedgerEntry>> {
  late final _$args = ref.$arg as String?;
  String? get batchId => _$args;

  FutureOr<Paginated<InventoryLedgerEntry>> build(String? batchId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<Paginated<InventoryLedgerEntry>>,
              Paginated<InventoryLedgerEntry>
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<Paginated<InventoryLedgerEntry>>,
                Paginated<InventoryLedgerEntry>
              >,
              AsyncValue<Paginated<InventoryLedgerEntry>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
