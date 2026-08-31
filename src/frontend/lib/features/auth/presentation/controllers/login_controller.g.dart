// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'login_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Form state + submit for A-02. UI keeps the text in [TextEditingController]s;
/// this holds only what needs to survive a rebuild (obscure toggle, in-flight
/// flag, server errors).

@ProviderFor(LoginController)
final loginControllerProvider = LoginControllerProvider._();

/// Form state + submit for A-02. UI keeps the text in [TextEditingController]s;
/// this holds only what needs to survive a rebuild (obscure toggle, in-flight
/// flag, server errors).
final class LoginControllerProvider
    extends $NotifierProvider<LoginController, AuthFormState> {
  /// Form state + submit for A-02. UI keeps the text in [TextEditingController]s;
  /// this holds only what needs to survive a rebuild (obscure toggle, in-flight
  /// flag, server errors).
  LoginControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'loginControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$loginControllerHash();

  @$internal
  @override
  LoginController create() => LoginController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AuthFormState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AuthFormState>(value),
    );
  }
}

String _$loginControllerHash() => r'3ed8af0b4a40c0c96386051a4e5f378f38747832';

/// Form state + submit for A-02. UI keeps the text in [TextEditingController]s;
/// this holds only what needs to survive a rebuild (obscure toggle, in-flight
/// flag, server errors).

abstract class _$LoginController extends $Notifier<AuthFormState> {
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
