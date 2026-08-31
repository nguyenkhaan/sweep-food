// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'subscription_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// P-02. Loads the current plan; falls back to the free default if the call
/// fails (the MVP is free either way).

@ProviderFor(SubscriptionController)
final subscriptionControllerProvider = SubscriptionControllerProvider._();

/// P-02. Loads the current plan; falls back to the free default if the call
/// fails (the MVP is free either way).
final class SubscriptionControllerProvider
    extends $AsyncNotifierProvider<SubscriptionController, Subscription> {
  /// P-02. Loads the current plan; falls back to the free default if the call
  /// fails (the MVP is free either way).
  SubscriptionControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'subscriptionControllerProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$subscriptionControllerHash();

  @$internal
  @override
  SubscriptionController create() => SubscriptionController();
}

String _$subscriptionControllerHash() =>
    r'c116c770894539811f95b8ed2c0f895df1f1066f';

/// P-02. Loads the current plan; falls back to the free default if the call
/// fails (the MVP is free either way).

abstract class _$SubscriptionController extends $AsyncNotifier<Subscription> {
  FutureOr<Subscription> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<Subscription>, Subscription>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<Subscription>, Subscription>,
              AsyncValue<Subscription>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
