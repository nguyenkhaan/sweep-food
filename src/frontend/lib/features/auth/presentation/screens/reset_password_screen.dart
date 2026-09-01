import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/auth/presentation/controllers/reset_password_controller.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_form_error.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_text_field.dart';

/// Argument passed to [ResetPasswordScreen] via `GoRouter` `extra`.
class ResetPasswordArgs {
  const ResetPasswordArgs({required this.phone});

  final String phone;
}

/// A-04 step 2 — enter the reset OTP and a new password. On success returns to
/// sign-in.
class ResetPasswordScreen extends ConsumerStatefulWidget {
  const ResetPasswordScreen({required this.args, super.key});

  final ResetPasswordArgs? args;

  @override
  ConsumerState<ResetPasswordScreen> createState() =>
      _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends ConsumerState<ResetPasswordScreen> {
  final _otp = TextEditingController();
  final _password = TextEditingController();

  @override
  void dispose() {
    _otp.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final args = widget.args;
    if (args == null) return;
    FocusScope.of(context).unfocus();
    final ok = await ref.read(resetPasswordControllerProvider.notifier).submit(
          phone: args.phone,
          otp: _otp.text,
          newPassword: _password.text,
          l10n: context.l10n,
        );
    if (ok && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(context.l10n.resetPasswordDone)),
      );
      context.go(Routes.login);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final args = widget.args;
    final state = ref.watch(resetPasswordControllerProvider);

    return Scaffold(
      appBar: AppBar(leading: const BackButton()),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.xs, Gap.xl, Gap.xl),
          children: [
            Text(
              l10n.resetPasswordTitle,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            Gap.gapXxs,
            Text(
              args == null
                  ? l10n.authOtpMissingArgs
                  : l10n.resetPasswordSubtitle(args.phone),
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            Gap.gapXl,
            if (args != null) ...[
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
                label: l10n.resetPasswordNewLabel,
                controller: _password,
                hintText: l10n.authPasswordHint,
                prefixIcon: Icons.lock_outline_rounded,
                obscureText: state.obscure,
                onToggleObscure: ref
                    .read(resetPasswordControllerProvider.notifier)
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
                label: l10n.resetPasswordCta,
                loading: state.submitting,
                onPressed: state.submitting ? null : _submit,
              ),
            ],
            Gap.gapMd,
            Center(
              child: TextButton(
                onPressed: () => context.go(Routes.login),
                child: Text(l10n.forgotBackToLogin),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
