// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'change_phone_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// P-01a — replace the signed-in user's phone number.
///
/// Two steps: [requestOtp] normalises the new number to E.164 and sends an OTP
/// to it; [submit] verifies the OTP. On success the [SessionController] cache is
/// refreshed from the server (the JWT itself stays valid).

@ProviderFor(ChangePhoneController)
final changePhoneControllerProvider = ChangePhoneControllerProvider._();

/// P-01a — replace the signed-in user's phone number.
///
/// Two steps: [requestOtp] normalises the new number to E.164 and sends an OTP
/// to it; [submit] verifies the OTP. On success the [SessionController] cache is
/// refreshed from the server (the JWT itself stays valid).
final class ChangePhoneControllerProvider
    extends $NotifierProvider<ChangePhoneController, AuthFormState> {
  /// P-01a — replace the signed-in user's phone number.
  ///
  /// Two steps: [requestOtp] normalises the new number to E.164 and sends an OTP
  /// to it; [submit] verifies the OTP. On success the [SessionController] cache is
  /// refreshed from the server (the JWT itself stays valid).
  ChangePhoneControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'changePhoneControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$changePhoneControllerHash();

  @$internal
  @override
  ChangePhoneController create() => ChangePhoneController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AuthFormState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AuthFormState>(value),
    );
  }
}

String _$changePhoneControllerHash() =>
    r'489524a5d3a4378fccb039e48f8bac058f0c368d';

/// P-01a — replace the signed-in user's phone number.
///
/// Two steps: [requestOtp] normalises the new number to E.164 and sends an OTP
/// to it; [submit] verifies the OTP. On success the [SessionController] cache is
/// refreshed from the server (the JWT itself stays valid).

abstract class _$ChangePhoneController extends $Notifier<AuthFormState> {
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
