import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/auth/presentation/controllers/otp_controller.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_form_error.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_text_field.dart';

/// Registration-step-2 arguments passed via `GoRouter` `extra`.
typedef OtpArgs = ({String phone, String password});

/// A-03 step 2. Enter the 6-digit registration OTP. On success the session
/// flips and `appRedirect` moves the router on to onboarding.
class OtpScreen extends ConsumerStatefulWidget {
  const OtpScreen({required this.args, super.key});

  final OtpArgs? args;

  @override
  ConsumerState<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends ConsumerState<OtpScreen> {
  final _otp = TextEditingController();

  @override
  void dispose() {
    _otp.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final args = widget.args;
    if (args == null) return;
    FocusScope.of(context).unfocus();
    await ref.read(otpControllerProvider.notifier).submit(
          phone: args.phone,
          password: args.password,
          otp: _otp.text,
          l10n: context.l10n,
        );
  }

  Future<void> _resend() async {
    final args = widget.args;
    if (args == null) return;
    await ref
        .read(otpControllerProvider.notifier)
        .resend(phone: args.phone, l10n: context.l10n);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(context.l10n.authOtpResent)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final args = widget.args;
    final state = ref.watch(otpControllerProvider);

    return Scaffold(
      appBar: AppBar(leading: const BackButton()),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.xs, Gap.xl, Gap.xl),
          children: [
            Text(
              l10n.authOtpTitle,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            Gap.gapXxs,
            Text(
              args == null
                  ? l10n.authOtpMissingArgs
                  : l10n.authOtpSubtitle(args.phone),
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
                textInputAction: TextInputAction.done,
                autofillHints: const [AutofillHints.oneTimeCode],
                onSubmitted: (_) => _submit(),
                errorText: state.fieldErrors['otp'],
              ),
              if (state.formError != null) ...[
                Gap.gapXs,
                AuthFormError(state.formError!),
              ],
              Gap.gapMd,
              PrimaryButton(
                label: l10n.authOtpConfirm,
                loading: state.submitting,
                onPressed: state.submitting ? null : _submit,
              ),
              Gap.gapXs,
              Center(
                child: TextButton(
                  onPressed: state.submitting ? null : _resend,
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
