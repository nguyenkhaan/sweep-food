// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'forgot_password_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(ForgotPasswordController)
final forgotPasswordControllerProvider = ForgotPasswordControllerProvider._();

final class ForgotPasswordControllerProvider
    extends $NotifierProvider<ForgotPasswordController, ForgotPasswordState> {
  ForgotPasswordControllerProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'forgotPasswordControllerProvider',
          isAutoDispose: true,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$forgotPasswordControllerHash();

  @$internal
  @override
  ForgotPasswordController create() => ForgotPasswordController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ForgotPasswordState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ForgotPasswordState>(value),
    );
  }
}

String _$forgotPasswordControllerHash() =>
    r'87c66cb0ffe7567573cf9a31e93780f5451c86b5';

abstract class _$ForgotPasswordController
    extends $Notifier<ForgotPasswordState> {
  ForgotPasswordState build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<ForgotPasswordState, ForgotPasswordState>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<ForgotPasswordState, ForgotPasswordState>,
        ForgotPasswordState,
        Object?,
        Object?>;
    element.handleCreate(ref, build);
  }
}
