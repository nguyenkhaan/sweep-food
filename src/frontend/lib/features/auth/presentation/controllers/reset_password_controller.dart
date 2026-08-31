import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/presentation/controllers/auth_form.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'reset_password_controller.g.dart';

/// A-04 step 2 — enter the reset OTP and a new password. On success the screen
/// returns to sign-in.
@riverpod
class ResetPasswordController extends _$ResetPasswordController {
  @override
  AuthFormState build() => const AuthFormState();

  void toggleObscure() => state = state.copyWith(obscure: !state.obscure);

  /// Returns `true` on success so the screen can navigate back to sign-in.
  Future<bool> submit({
    required String phone,
    required String otp,
    required String newPassword,
    required AppL10n l10n,
  }) async {
    final errors = <String, String>{
      if (!isValidOtp(otp)) 'otp': l10n.authOtpInvalid,
      if (!isValidPassword(newPassword)) 'password': l10n.authPasswordTooShort,
    };
    if (errors.isNotEmpty) {
      state = state.copyWith(fieldErrors: errors, formError: null);
      return false;
    }
    state = state.copyWith(
      submitting: true,
      fieldErrors: const {},
      formError: null,
    );
    final res = await ref.read(authRepositoryProvider).confirmPasswordReset(
          phone: phone,
          otp: otp.trim(),
          newPassword: newPassword,
        );
    return res.fold(
      (f) {
        state = state.copyWith(
          submitting: false,
          formError: f.localizedMessage(l10n),
        );
        return false;
      },
      (_) {
        state = state.copyWith(submitting: false);
        return true;
      },
    );
  }
}
