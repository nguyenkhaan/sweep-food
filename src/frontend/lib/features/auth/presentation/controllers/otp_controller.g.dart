// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'otp_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// A-03 step 2 — enter the 6-digit registration OTP. On success the account is
/// verified and signed in via [SessionController.verifyRegister]; the router
/// then moves the user on to onboarding (no explicit navigation here).

@ProviderFor(OtpController)
final otpControllerProvider = OtpControllerProvider._();

/// A-03 step 2 — enter the 6-digit registration OTP. On success the account is
/// verified and signed in via [SessionController.verifyRegister]; the router
/// then moves the user on to onboarding (no explicit navigation here).
final class OtpControllerProvider
    extends $NotifierProvider<OtpController, AuthFormState> {
  /// A-03 step 2 — enter the 6-digit registration OTP. On success the account is
  /// verified and signed in via [SessionController.verifyRegister]; the router
  /// then moves the user on to onboarding (no explicit navigation here).
  OtpControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'otpControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$otpControllerHash();

  @$internal
  @override
  OtpController create() => OtpController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AuthFormState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AuthFormState>(value),
    );
  }
}

String _$otpControllerHash() => r'a6e7c4f778a491e62a5f185042cc86c5a7774250';

/// A-03 step 2 — enter the 6-digit registration OTP. On success the account is
/// verified and signed in via [SessionController.verifyRegister]; the router
/// then moves the user on to onboarding (no explicit navigation here).

abstract class _$OtpController extends $Notifier<AuthFormState> {
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
