import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/features/auth/presentation/controllers/auth_form.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'register_controller.g.dart';

/// Form state + submit for A-03. The "đồng ý điều khoản" checkbox is screen-local
/// state and passed into [submit]; everything else rides the shared
/// [AuthFormState].
@riverpod
class RegisterController extends _$RegisterController {
  @override
  AuthFormState build() => const AuthFormState();

  void toggleObscure() => state = state.copyWith(obscure: !state.obscure);

  Future<bool> submit({
    required String name,
    required String email,
    required String password,
    required bool agreedToTerms,
    required AppL10n l10n,
  }) async {
    final errors = <String, String>{
      if (name.trim().isEmpty) 'name': l10n.authEnterName,
      if (!isValidEmail(email)) 'email': l10n.authInvalidEmail,
      if (!isValidPassword(password)) 'password': l10n.authPasswordTooShort,
    };
    if (errors.isNotEmpty) {
      state = state.copyWith(fieldErrors: errors, formError: null);
      return false;
    }
    if (!agreedToTerms) {
      state = state.copyWith(
        formError: l10n.registerNeedTerms,
        fieldErrors: const {},
      );
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
          .register(name: name, email: email, password: password);
      return true;
    } on ValidationFailure catch (f) {
      state = state.copyWith(
        submitting: false,
        fieldErrors: f.fieldErrors,
        formError: f.fieldErrors.isEmpty ? f.localizedMessage(l10n) : null,
      );
      return false;
    } on Failure catch (f) {
      state = state.copyWith(
        submitting: false,
        formError: f.localizedMessage(l10n),
      );
      return false;
    }
  }
}
