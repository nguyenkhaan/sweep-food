import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/presentation/controllers/auth_form.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'register_controller.g.dart';

/// Form state + submit for A-03 step 1. The "đồng ý điều khoản" checkbox is
/// screen-local state and passed into [submit]. On success the account exists
/// (unverified) and an OTP has been sent — the screen then routes to the OTP
/// screen with the normalised phone + password.
@riverpod
class RegisterController extends _$RegisterController {
  @override
  AuthFormState build() => const AuthFormState();

  void toggleObscure() => state = state.copyWith(obscure: !state.obscure);

  /// Returns the normalised E.164 phone on success (so the screen can navigate
  /// to OTP verification), or `null` when the form should stay put.
  Future<String?> submit({
    required String name,
    required String phone,
    required String password,
    required bool agreedToTerms,
    required AppL10n l10n,
  }) async {
    final errors = <String, String>{
      if (name.trim().isEmpty) 'name': l10n.authEnterName,
      if (!isValidPhone(phone)) 'phone': l10n.authInvalidPhone,
      if (!isValidPassword(password)) 'password': l10n.authPasswordTooShort,
    };
    if (errors.isNotEmpty) {
      state = state.copyWith(fieldErrors: errors, formError: null);
      return null;
    }
    if (!agreedToTerms) {
      state = state.copyWith(
        formError: l10n.registerNeedTerms,
        fieldErrors: const {},
      );
      return null;
    }

    final e164 = normalizePhoneE164(phone);
    state = state.copyWith(
      submitting: true,
      fieldErrors: const {},
      formError: null,
    );
    final res = await ref.read(authRepositoryProvider).register(
          phone: e164,
          password: password,
          name: name.trim(),
        );
    return res.fold(
      (f) {
        state = state.copyWith(
          submitting: false,
          fieldErrors: f is ValidationFailure ? f.fieldErrors : const {},
          formError: (f is ValidationFailure && f.fieldErrors.isNotEmpty)
              ? null
              : f.localizedMessage(l10n),
        );
        return null;
      },
      (_) {
        state = state.copyWith(submitting: false);
        return e164;
      },
    );
  }
}
