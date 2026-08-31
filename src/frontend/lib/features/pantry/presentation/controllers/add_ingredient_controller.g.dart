// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'add_ingredient_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Form state for K-03 (add) and K-03 in edit mode (`editItemId != null`).

@ProviderFor(AddIngredientController)
final addIngredientControllerProvider = AddIngredientControllerFamily._();

/// Form state for K-03 (add) and K-03 in edit mode (`editItemId != null`).
final class AddIngredientControllerProvider
    extends $NotifierProvider<AddIngredientController, PantryItemDraft> {
  /// Form state for K-03 (add) and K-03 in edit mode (`editItemId != null`).
  AddIngredientControllerProvider._({
    required AddIngredientControllerFamily super.from,
    required String? super.argument,
  }) : super(
         retry: null,
         name: r'addIngredientControllerProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$addIngredientControllerHash();

  @override
  String toString() {
    return r'addIngredientControllerProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  AddIngredientController create() => AddIngredientController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(PantryItemDraft value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<PantryItemDraft>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is AddIngredientControllerProvider &&
        other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$addIngredientControllerHash() =>
    r'107d6e398134a55f3e9a390799438efd98d9a72c';

/// Form state for K-03 (add) and K-03 in edit mode (`editItemId != null`).

final class AddIngredientControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          AddIngredientController,
          PantryItemDraft,
          PantryItemDraft,
          PantryItemDraft,
          String?
        > {
  AddIngredientControllerFamily._()
    : super(
        retry: null,
        name: r'addIngredientControllerProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Form state for K-03 (add) and K-03 in edit mode (`editItemId != null`).

  AddIngredientControllerProvider call(String? editItemId) =>
      AddIngredientControllerProvider._(argument: editItemId, from: this);

  @override
  String toString() => r'addIngredientControllerProvider';
}

/// Form state for K-03 (add) and K-03 in edit mode (`editItemId != null`).

abstract class _$AddIngredientController extends $Notifier<PantryItemDraft> {
  late final _$args = ref.$arg as String?;
  String? get editItemId => _$args;

  PantryItemDraft build(String? editItemId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<PantryItemDraft, PantryItemDraft>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<PantryItemDraft, PantryItemDraft>,
              PantryItemDraft,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
