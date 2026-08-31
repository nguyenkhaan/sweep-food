import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/presentation/controllers/auth_form.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'otp_controller.g.dart';

/// A-03 step 2 — enter the 6-digit registration OTP. On success the account is
/// verified and signed in via [SessionController.verifyRegister]; the router
/// then moves the user on to onboarding (no explicit navigation here).
@riverpod
class OtpController extends _$OtpController {
  @override
  AuthFormState build() => const AuthFormState();

  Future<void> submit({
    required String phone,
    required String password,
    required String otp,
    required AppL10n l10n,
  }) async {
    if (!isValidOtp(otp)) {
      state = state.copyWith(fieldErrors: {'otp': l10n.authOtpInvalid});
      return;
    }
    state = state.copyWith(
      submitting: true,
      fieldErrors: const {},
      formError: null,
    );
    try {
      await ref.read(sessionControllerProvider.notifier).verifyRegister(
            phone: phone,
            otp: otp.trim(),
            password: password,
          );
      // Success: session flips, router redirects. Leave `submitting` true so
      // the button stays disabled through the transition.
    } on Failure catch (f) {
      state = state.copyWith(
        submitting: false,
        formError: f.localizedMessage(l10n),
      );
    }
  }

  /// Request a fresh OTP for the unverified account.
  Future<void> resend({required String phone, required AppL10n l10n}) async {
    state = state.copyWith(formError: null);
    final res = await ref.read(authRepositoryProvider).resendRegisterOtp(phone);
    res.fold(
      (f) => state = state.copyWith(formError: f.localizedMessage(l10n)),
      (_) => state = state.copyWith(formError: null),
    );
  }
}
