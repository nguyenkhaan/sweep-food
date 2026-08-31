// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'register_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Form state + submit for A-03 step 1. The "đồng ý điều khoản" checkbox is
/// screen-local state and passed into [submit]. On success the account exists
/// (unverified) and an OTP has been sent — the screen then routes to the OTP
/// screen with the normalised phone + password.

@ProviderFor(RegisterController)
final registerControllerProvider = RegisterControllerProvider._();

/// Form state + submit for A-03 step 1. The "đồng ý điều khoản" checkbox is
/// screen-local state and passed into [submit]. On success the account exists
/// (unverified) and an OTP has been sent — the screen then routes to the OTP
/// screen with the normalised phone + password.
final class RegisterControllerProvider
    extends $NotifierProvider<RegisterController, AuthFormState> {
  /// Form state + submit for A-03 step 1. The "đồng ý điều khoản" checkbox is
  /// screen-local state and passed into [submit]. On success the account exists
  /// (unverified) and an OTP has been sent — the screen then routes to the OTP
  /// screen with the normalised phone + password.
  RegisterControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'registerControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$registerControllerHash();

  @$internal
  @override
  RegisterController create() => RegisterController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AuthFormState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AuthFormState>(value),
    );
  }
}

String _$registerControllerHash() =>
    r'd49c5bd6a3e56c35ff401e95749304843f908ba6';

/// Form state + submit for A-03 step 1. The "đồng ý điều khoản" checkbox is
/// screen-local state and passed into [submit]. On success the account exists
/// (unverified) and an OTP has been sent — the screen then routes to the OTP
/// screen with the normalised phone + password.

abstract class _$RegisterController extends $Notifier<AuthFormState> {
  AuthFormState build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AuthFormState, AuthFormState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AuthFormState, AuthFormState>,
              AuthFormState,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
