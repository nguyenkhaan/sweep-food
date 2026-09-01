import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:sweepfood/features/auth/presentation/controllers/auth_form.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

part 'change_phone_controller.g.dart';

/// P-01a — replace the signed-in user's phone number.
///
/// Two steps: [requestOtp] normalises the new number to E.164 and sends an OTP
/// to it; [submit] verifies the OTP. On success the [SessionController] cache is
/// refreshed from the server (the JWT itself stays valid).
@riverpod
class ChangePhoneController extends _$ChangePhoneController {
  @override
  AuthFormState build() => const AuthFormState();

  /// The E.164 number the last [requestOtp] sent an OTP to (for the hint text).
  String? get pendingPhone => _pendingPhone;
  String? _pendingPhone;

  /// Step 1 — validate [phone] and request the OTP. Returns `true` when sent.
  Future<bool> requestOtp({required String phone, required AppL10n l10n}) async {
    if (!isValidPhone(phone)) {
      state = state.copyWith(
        fieldErrors: {'phone': l10n.authInvalidPhone},
        formError: null,
      );
      return false;
    }

    final e164 = normalizePhoneE164(phone);
    state = state.copyWith(
      submitting: true,
      fieldErrors: const {},
      formError: null,
    );
    final res =
        await ref.read(authRepositoryProvider).requestPhoneChange(e164);
    return res.fold(
      (f) {
        state = state.copyWith(
          submitting: false,
          formError: f.localizedMessage(l10n),
        );
        return false;
      },
      (_) {
        _pendingPhone = e164;
        state = state.copyWith(submitting: false);
        return true;
      },
    );
  }

  /// Step 2 — verify [otp] for the pending phone. Returns `true` on success.
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
        await ref.read(authRepositoryProvider).confirmPhoneChange(otp.trim());
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
