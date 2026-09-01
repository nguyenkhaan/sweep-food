// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'edit_profile_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// P-01a — edit the signed-in user's display name via `PATCH /users/profile`.
/// On success the [SessionController] cache is refreshed from the response.

@ProviderFor(EditProfileController)
final editProfileControllerProvider = EditProfileControllerProvider._();

/// P-01a — edit the signed-in user's display name via `PATCH /users/profile`.
/// On success the [SessionController] cache is refreshed from the response.
final class EditProfileControllerProvider
    extends $NotifierProvider<EditProfileController, AuthFormState> {
  /// P-01a — edit the signed-in user's display name via `PATCH /users/profile`.
  /// On success the [SessionController] cache is refreshed from the response.
  EditProfileControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'editProfileControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$editProfileControllerHash();

  @$internal
  @override
  EditProfileController create() => EditProfileController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AuthFormState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AuthFormState>(value),
    );
  }
}

String _$editProfileControllerHash() =>
    r'bb4b9747d9d278a619ec8629fa0b94296fd58bc8';

/// P-01a — edit the signed-in user's display name via `PATCH /users/profile`.
/// On success the [SessionController] cache is refreshed from the response.

abstract class _$EditProfileController extends $Notifier<AuthFormState> {
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
