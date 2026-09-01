import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/presentation/controllers/auth_form.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'change_password_controller.g.dart';

/// P-01a — change the password of the signed-in user.
///
/// Two steps: [requestOtp] issues a `CHANGE_PASSWORD` OTP to the account phone;
/// [submit] verifies it and sets the new password. The backend revokes every
/// session on success, so the screen signs the user out afterwards.
@riverpod
class ChangePasswordController extends _$ChangePasswordController {
  @override
  AuthFormState build() => const AuthFormState();

  void toggleObscure() => state = state.copyWith(obscure: !state.obscure);

  /// Step 1 — request the OTP. Returns `true` when it was sent.
  Future<bool> requestOtp(AppL10n l10n) async {
    state = state.copyWith(
      submitting: true,
      formError: null,
      fieldErrors: const {},
    );
    final res = await ref.read(authRepositoryProvider).requestPasswordChange();
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

  /// Step 2 — verify [otp] and set [newPassword]. Returns `true` on success.
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
    final res = await ref.read(authRepositoryProvider).confirmPasswordChange(
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
