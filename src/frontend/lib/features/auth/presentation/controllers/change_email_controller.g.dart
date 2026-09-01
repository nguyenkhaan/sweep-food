// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'change_email_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// P-01a — add or replace the signed-in user's email.
///
/// Two steps: [requestOtp] validates the new address and sends an OTP to it;
/// [submit] verifies the OTP. On success the [SessionController] cache is
/// refreshed from the server.

@ProviderFor(ChangeEmailController)
final changeEmailControllerProvider = ChangeEmailControllerProvider._();

/// P-01a — add or replace the signed-in user's email.
///
/// Two steps: [requestOtp] validates the new address and sends an OTP to it;
/// [submit] verifies the OTP. On success the [SessionController] cache is
/// refreshed from the server.
final class ChangeEmailControllerProvider
    extends $NotifierProvider<ChangeEmailController, AuthFormState> {
  /// P-01a — add or replace the signed-in user's email.
  ///
  /// Two steps: [requestOtp] validates the new address and sends an OTP to it;
  /// [submit] verifies the OTP. On success the [SessionController] cache is
  /// refreshed from the server.
  ChangeEmailControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'changeEmailControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$changeEmailControllerHash();

  @$internal
  @override
  ChangeEmailController create() => ChangeEmailController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AuthFormState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AuthFormState>(value),
    );
  }
}

String _$changeEmailControllerHash() =>
    r'94c7703e5032258dac7cb2f34f7f529a20e6d870';

/// P-01a — add or replace the signed-in user's email.
///
/// Two steps: [requestOtp] validates the new address and sends an OTP to it;
/// [submit] verifies the OTP. On success the [SessionController] cache is
/// refreshed from the server.

abstract class _$ChangeEmailController extends $Notifier<AuthFormState> {
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
