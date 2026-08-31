import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/presentation/controllers/auth_form.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'forgot_password_controller.g.dart';

/// A-04 step 1 — enter the account phone number. On success the backend has
/// sent a reset OTP; the screen routes to the reset-password screen with the
/// normalised phone.
@riverpod
class ForgotPasswordController extends _$ForgotPasswordController {
  @override
  AuthFormState build() => const AuthFormState();

  /// Returns the normalised E.164 phone on success, else `null`.
  Future<String?> submit(String phone, AppL10n l10n) async {
    if (!isValidPhone(phone)) {
      state = state.copyWith(fieldErrors: {'phone': l10n.authInvalidPhone});
      return null;
    }
    final e164 = normalizePhoneE164(phone);
    state = state.copyWith(
      submitting: true,
      fieldErrors: const {},
      formError: null,
    );
    final res =
        await ref.read(authRepositoryProvider).requestPasswordReset(e164);
    return res.fold(
      (f) {
        state = state.copyWith(
          submitting: false,
          formError: f.localizedMessage(l10n),
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
