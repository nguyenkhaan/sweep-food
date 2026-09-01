// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'forgot_password_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// A-04 step 1 — enter the account phone number. On success the backend has
/// sent a reset OTP; the screen routes to the reset-password screen with the
/// normalised phone.

@ProviderFor(ForgotPasswordController)
final forgotPasswordControllerProvider = ForgotPasswordControllerProvider._();

/// A-04 step 1 — enter the account phone number. On success the backend has
/// sent a reset OTP; the screen routes to the reset-password screen with the
/// normalised phone.
final class ForgotPasswordControllerProvider
    extends $NotifierProvider<ForgotPasswordController, AuthFormState> {
  /// A-04 step 1 — enter the account phone number. On success the backend has
  /// sent a reset OTP; the screen routes to the reset-password screen with the
  /// normalised phone.
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
  Override overrideWithValue(AuthFormState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AuthFormState>(value),
    );
  }
}

String _$forgotPasswordControllerHash() =>
    r'4bcf2b765179d33e02741cc1f69e62af87bc6296';

/// A-04 step 1 — enter the account phone number. On success the backend has
/// sent a reset OTP; the screen routes to the reset-password screen with the
/// normalised phone.

abstract class _$ForgotPasswordController extends $Notifier<AuthFormState> {
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
