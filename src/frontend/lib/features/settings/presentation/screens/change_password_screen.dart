import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/auth/presentation/controllers/change_password_controller.dart';
import 'package:sweepfood/features/auth/presentation/controllers/session_controller.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_form_error.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_text_field.dart';

/// P-01a — change the password of the signed-in user. Step 1 sends an OTP to
/// the account phone; step 2 verifies it and sets the new password. The backend
/// revokes every session on success, so we sign the user out afterwards.
class ChangePasswordScreen extends ConsumerStatefulWidget {
  const ChangePasswordScreen({super.key});

  @override
  ConsumerState<ChangePasswordScreen> createState() =>
      _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends ConsumerState<ChangePasswordScreen> {
  final _otp = TextEditingController();
  final _password = TextEditingController();
  bool _otpSent = false;

  @override
  void dispose() {
    _otp.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _requestOtp() async {
    FocusScope.of(context).unfocus();
    final ok = await ref
        .read(changePasswordControllerProvider.notifier)
        .requestOtp(context.l10n);
    if (ok && mounted) setState(() => _otpSent = true);
  }

  Future<void> _submit() async {
    final phone = ref.read(sessionControllerProvider).asData?.value?.user.phone;
    if (phone == null) return;
    FocusScope.of(context).unfocus();
    final ok =
        await ref.read(changePasswordControllerProvider.notifier).submit(
              phone: phone,
              otp: _otp.text,
              newPassword: _password.text,
              l10n: context.l10n,
            );
    if (ok && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(context.l10n.changePasswordDone)),
      );
      await ref.read(sessionControllerProvider.notifier).logOut();
      if (mounted) context.go(Routes.login);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final state = ref.watch(changePasswordControllerProvider);
    final phone =
        ref.watch(sessionControllerProvider).asData?.value?.user.phone ?? '';

    return Scaffold(
      appBar: AppBar(title: Text(l10n.changePasswordTitle)),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.lg, Gap.xl, Gap.xl),
          children: [
            Text(
              _otpSent
                  ? l10n.changePasswordOtpHint
                  : l10n.changePasswordIntro(phone),
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            Gap.gapLg,
            if (!_otpSent) ...[
              if (state.formError != null) ...[
                AuthFormError(state.formError!),
                Gap.gapXs,
              ],
              PrimaryButton(
                label: l10n.accountSendCode,
                loading: state.submitting,
                onPressed: state.submitting ? null : _requestOtp,
              ),
            ] else ...[
              AuthTextField(
                label: l10n.authOtpLabel,
                controller: _otp,
                hintText: '000000',
                prefixIcon: Icons.sms_outlined,
                keyboardType: TextInputType.number,
                textInputAction: TextInputAction.next,
                autofillHints: const [AutofillHints.oneTimeCode],
                errorText: state.fieldErrors['otp'],
              ),
              Gap.gapMd,
              AuthTextField(
                label: l10n.changePasswordNewLabel,
                controller: _password,
                hintText: l10n.authPasswordHint,
                prefixIcon: Icons.lock_outline_rounded,
                obscureText: state.obscure,
                onToggleObscure: ref
                    .read(changePasswordControllerProvider.notifier)
                    .toggleObscure,
                textInputAction: TextInputAction.done,
                autofillHints: const [AutofillHints.newPassword],
                onSubmitted: (_) => _submit(),
                errorText: state.fieldErrors['password'],
              ),
              if (state.formError != null) ...[
                Gap.gapXs,
                AuthFormError(state.formError!),
              ],
              Gap.gapMd,
              PrimaryButton(
                label: l10n.accountVerifyCta,
                loading: state.submitting,
                onPressed: state.submitting ? null : _submit,
              ),
              Gap.gapSm,
              Center(
                child: TextButton(
                  onPressed: state.submitting ? null : _requestOtp,
                  child: Text(l10n.authOtpResendCta),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
