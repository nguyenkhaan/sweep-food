import 'package:frontend/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:frontend/features/auth/presentation/controllers/auth_form.dart';
import 'package:frontend/l10n/app_localizations.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'forgot_password_controller.g.dart';

/// A-04. Two visual states: the form, and the "đã gửi tới …" confirmation.
class ForgotPasswordState {
  const ForgotPasswordState({
    this.form = const AuthFormState(),
    this.sentToEmail,
  });

  final AuthFormState form;

  /// Non-null once the reset link request has been accepted — the screen then
  /// swaps to the confirmation card.
  final String? sentToEmail;

  bool get isSent => sentToEmail != null;

  ForgotPasswordState copyWith({AuthFormState? form, String? sentToEmail}) =>
      ForgotPasswordState(
        form: form ?? this.form,
        sentToEmail: sentToEmail ?? this.sentToEmail,
      );
}

@riverpod
class ForgotPasswordController extends _$ForgotPasswordController {
  @override
  ForgotPasswordState build() => const ForgotPasswordState();

  Future<void> submit(String email, AppL10n l10n) async {
    if (!isValidEmail(email)) {
      state = state.copyWith(
        form: state.form.copyWith(
          fieldErrors: {'email': l10n.authInvalidEmail},
        ),
      );
      return;
    }
    state = state.copyWith(
      form: state.form.copyWith(
        submitting: true,
        fieldErrors: const {},
        formError: null,
      ),
    );
    final res = await ref
        .read(authRepositoryProvider)
        .requestPasswordReset(email);
    state = res.fold(
      (f) => state.copyWith(
        form: state.form.copyWith(
          submitting: false,
          formError: f.localizedMessage(l10n),
        ),
      ),
      // Same confirmation whether or not the address exists (no account enum).
      (_) => state.copyWith(
        form: state.form.copyWith(submitting: false),
        sentToEmail: email.trim(),
      ),
    );
  }
}
