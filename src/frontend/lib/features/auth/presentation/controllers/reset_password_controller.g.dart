// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'reset_password_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// A-04 step 2 — enter the reset OTP and a new password. On success the screen
/// returns to sign-in.

@ProviderFor(ResetPasswordController)
final resetPasswordControllerProvider = ResetPasswordControllerProvider._();

/// A-04 step 2 — enter the reset OTP and a new password. On success the screen
/// returns to sign-in.
final class ResetPasswordControllerProvider
    extends $NotifierProvider<ResetPasswordController, AuthFormState> {
  /// A-04 step 2 — enter the reset OTP and a new password. On success the screen
  /// returns to sign-in.
  ResetPasswordControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'resetPasswordControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$resetPasswordControllerHash();

  @$internal
  @override
  ResetPasswordController create() => ResetPasswordController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AuthFormState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AuthFormState>(value),
    );
  }
}

String _$resetPasswordControllerHash() =>
    r'0075bfe244b5f92a8bfd0adcbb7df1a3d69b5f3f';

/// A-04 step 2 — enter the reset OTP and a new password. On success the screen
/// returns to sign-in.

abstract class _$ResetPasswordController extends $Notifier<AuthFormState> {
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
