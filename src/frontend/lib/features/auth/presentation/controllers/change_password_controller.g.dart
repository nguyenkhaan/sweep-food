// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'change_password_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// P-01a — change the password of the signed-in user.
///
/// Two steps: [requestOtp] issues a `CHANGE_PASSWORD` OTP to the account phone;
/// [submit] verifies it and sets the new password. The backend revokes every
/// session on success, so the screen signs the user out afterwards.

@ProviderFor(ChangePasswordController)
final changePasswordControllerProvider = ChangePasswordControllerProvider._();

/// P-01a — change the password of the signed-in user.
///
/// Two steps: [requestOtp] issues a `CHANGE_PASSWORD` OTP to the account phone;
/// [submit] verifies it and sets the new password. The backend revokes every
/// session on success, so the screen signs the user out afterwards.
final class ChangePasswordControllerProvider
    extends $NotifierProvider<ChangePasswordController, AuthFormState> {
  /// P-01a — change the password of the signed-in user.
  ///
  /// Two steps: [requestOtp] issues a `CHANGE_PASSWORD` OTP to the account phone;
  /// [submit] verifies it and sets the new password. The backend revokes every
  /// session on success, so the screen signs the user out afterwards.
  ChangePasswordControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'changePasswordControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$changePasswordControllerHash();

  @$internal
  @override
  ChangePasswordController create() => ChangePasswordController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AuthFormState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AuthFormState>(value),
    );
  }
}

String _$changePasswordControllerHash() =>
    r'74aaddde0158a49cdc07dcbcc0a9f0d40699f1a2';

/// P-01a — change the password of the signed-in user.
///
/// Two steps: [requestOtp] issues a `CHANGE_PASSWORD` OTP to the account phone;
/// [submit] verifies it and sets the new password. The backend revokes every
/// session on success, so the screen signs the user out afterwards.

abstract class _$ChangePasswordController extends $Notifier<AuthFormState> {
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
