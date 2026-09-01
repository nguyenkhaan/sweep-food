import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/presentation/controllers/auth_form.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'change_email_controller.g.dart';

/// P-01a — add or replace the signed-in user's email.
///
/// Two steps: [requestOtp] validates the new address and sends an OTP to it;
/// [submit] verifies the OTP. On success the [SessionController] cache is
/// refreshed from the server.
@riverpod
class ChangeEmailController extends _$ChangeEmailController {
  @override
  AuthFormState build() => const AuthFormState();

  /// Step 1 — validate [email] and request the OTP. Returns `true` when sent.
  Future<bool> requestOtp({required String email, required AppL10n l10n}) async {
    final trimmed = email.trim();
    if (!isValidEmail(trimmed)) {
      state = state.copyWith(
        fieldErrors: {'email': l10n.authInvalidEmail},
        formError: null,
      );
      return false;
    }

    state = state.copyWith(
      submitting: true,
      fieldErrors: const {},
      formError: null,
    );
    final res = await ref
        .read(authRepositoryProvider)
        .requestEmailChange(trimmed.toLowerCase());
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

  /// Step 2 — verify [otp] for the pending email. Returns `true` on success.
  Future<bool> submit({required String otp, required AppL10n l10n}) async {
    if (!isValidOtp(otp)) {
      state = state.copyWith(fieldErrors: {'otp': l10n.authOtpInvalid});
      return false;
    }

    state = state.copyWith(
      submitting: true,
      fieldErrors: const {},
      formError: null,
    );
    final res =
        await ref.read(authRepositoryProvider).confirmEmailChange(otp.trim());
    return res.fold(
      (f) {
        state = state.copyWith(
          submitting: false,
          formError: f.localizedMessage(l10n),
        );
        return false;
      },
      (_) async {
        await ref.read(sessionControllerProvider.notifier).refreshProfile();
        state = state.copyWith(submitting: false);
        return true;
      },
    );
  }
}
