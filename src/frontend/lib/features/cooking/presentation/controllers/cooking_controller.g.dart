// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'cooking_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Drives the post-cook flow: preview → session → complete → expose the
/// [CookResult] for the D-05 / D-07 screen. Applying the result also
/// refreshes the pantry list, so the Home waste count picks it up.
///
/// Kept alive: the confirming widget (a bottom sheet) only `read`s this, so an
/// auto-dispose provider would be torn down mid-request.

@ProviderFor(CookingController)
final cookingControllerProvider = CookingControllerProvider._();

/// Drives the post-cook flow: preview → session → complete → expose the
/// [CookResult] for the D-05 / D-07 screen. Applying the result also
/// refreshes the pantry list, so the Home waste count picks it up.
///
/// Kept alive: the confirming widget (a bottom sheet) only `read`s this, so an
/// auto-dispose provider would be torn down mid-request.
final class CookingControllerProvider
    extends $NotifierProvider<CookingController, CookResult?> {
  /// Drives the post-cook flow: preview → session → complete → expose the
  /// [CookResult] for the D-05 / D-07 screen. Applying the result also
  /// refreshes the pantry list, so the Home waste count picks it up.
  ///
  /// Kept alive: the confirming widget (a bottom sheet) only `read`s this, so an
  /// auto-dispose provider would be torn down mid-request.
  CookingControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'cookingControllerProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$cookingControllerHash();

  @$internal
  @override
  CookingController create() => CookingController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(CookResult? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<CookResult?>(value),
    );
  }
}

String _$cookingControllerHash() => r'28c3a7707c11f9e541307a786f9cfbe5e6f6fc37';

/// Drives the post-cook flow: preview → session → complete → expose the
/// [CookResult] for the D-05 / D-07 screen. Applying the result also
/// refreshes the pantry list, so the Home waste count picks it up.
///
/// Kept alive: the confirming widget (a bottom sheet) only `read`s this, so an
/// auto-dispose provider would be torn down mid-request.

abstract class _$CookingController extends $Notifier<CookResult?> {
  CookResult? build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<CookResult?, CookResult?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<CookResult?, CookResult?>,
              CookResult?,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
