// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'register_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Form state + submit for A-03. The "đồng ý điều khoản" checkbox is screen-local
/// state and passed into [submit]; everything else rides the shared
/// [AuthFormState].

@ProviderFor(RegisterController)
final registerControllerProvider = RegisterControllerProvider._();

/// Form state + submit for A-03. The "đồng ý điều khoản" checkbox is screen-local
/// state and passed into [submit]; everything else rides the shared
/// [AuthFormState].
final class RegisterControllerProvider
    extends $NotifierProvider<RegisterController, AuthFormState> {
  /// Form state + submit for A-03. The "đồng ý điều khoản" checkbox is screen-local
  /// state and passed into [submit]; everything else rides the shared
  /// [AuthFormState].
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
    r'e5877a8a440bf6b11b45b77a3fc1ff57ebb58a1d';

/// Form state + submit for A-03. The "đồng ý điều khoản" checkbox is screen-local
/// state and passed into [submit]; everything else rides the shared
/// [AuthFormState].

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
