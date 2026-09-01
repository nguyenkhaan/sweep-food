import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/features/auth/presentation/controllers/auth_form.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'login_controller.g.dart';

/// Form state + submit for A-02. UI keeps the text in [TextEditingController]s;
/// this holds only what needs to survive a rebuild (obscure toggle, in-flight
/// flag, server errors).
@riverpod
class LoginController extends _$LoginController {
  @override
  AuthFormState build() => const AuthFormState();

  void toggleObscure() => state = state.copyWith(obscure: !state.obscure);

  /// Returns `true` on success so the screen can navigate.
  Future<bool> submit({
    required String email,
    required String password,
    required AppL10n l10n,
  }) async {
    final localErrors = <String, String>{
      if (!isValidEmail(email)) 'email': l10n.authInvalidEmail,
      if (password.isEmpty) 'password': l10n.authEnterPassword,
    };
    if (localErrors.isNotEmpty) {
      state = state.copyWith(fieldErrors: localErrors, formError: null);
      return false;
    }

    state = state.copyWith(
      submitting: true,
      fieldErrors: const {},
      formError: null,
    );
    try {
      await ref
          .read(sessionControllerProvider.notifier)
          .logIn(email: email, password: password);
      return true;
    } on Failure catch (f) {
      state = state.copyWith(
        submitting: false,
        formError: f.localizedMessage(l10n),
      );
      return false;
    } catch (_) {
      state = state.copyWith(submitting: false, formError: l10n.loginFailed);
      return false;
    }
  }
}
