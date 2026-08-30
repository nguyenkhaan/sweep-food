// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pantry_item_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// A single pantry item for the detail screen (K-02), read from the loaded list.
/// Returns `null` if the id isn't in the list (e.g. after it was deleted).

@ProviderFor(pantryItemById)
final pantryItemByIdProvider = PantryItemByIdFamily._();

/// A single pantry item for the detail screen (K-02), read from the loaded list.
/// Returns `null` if the id isn't in the list (e.g. after it was deleted).

final class PantryItemByIdProvider
    extends $FunctionalProvider<PantryItem?, PantryItem?, PantryItem?>
    with $Provider<PantryItem?> {
  /// A single pantry item for the detail screen (K-02), read from the loaded list.
  /// Returns `null` if the id isn't in the list (e.g. after it was deleted).
  PantryItemByIdProvider._({
    required PantryItemByIdFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'pantryItemByIdProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$pantryItemByIdHash();

  @override
  String toString() {
    return r'pantryItemByIdProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $ProviderElement<PantryItem?> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  PantryItem? create(Ref ref) {
    final argument = this.argument as String;
    return pantryItemById(ref, argument);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(PantryItem? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<PantryItem?>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is PantryItemByIdProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$pantryItemByIdHash() => r'38b67e89ecfcf04b4cc6b0764f4ae570f81ee7ea';

/// A single pantry item for the detail screen (K-02), read from the loaded list.
/// Returns `null` if the id isn't in the list (e.g. after it was deleted).

final class PantryItemByIdFamily extends $Family
    with $FunctionalFamilyOverride<PantryItem?, String> {
  PantryItemByIdFamily._()
    : super(
        retry: null,
        name: r'pantryItemByIdProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// A single pantry item for the detail screen (K-02), read from the loaded list.
  /// Returns `null` if the id isn't in the list (e.g. after it was deleted).

  PantryItemByIdProvider call(String id) =>
      PantryItemByIdProvider._(argument: id, from: this);

  @override
  String toString() => r'pantryItemByIdProvider';
}
