import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/emerald_split_header.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/auth/presentation/controllers/change_phone_controller.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_form_error.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_text_field.dart';

/// P-01a — replace phone number (Concept B · Format 1).
class ChangePhoneScreen extends ConsumerStatefulWidget {
  const ChangePhoneScreen({super.key});

  @override
  ConsumerState<ChangePhoneScreen> createState() => _ChangePhoneScreenState();
}

class _ChangePhoneScreenState extends ConsumerState<ChangePhoneScreen> {
  final _phone = TextEditingController();
  final _otp = TextEditingController();
  bool _otpSent = false;

  @override
  void dispose() {
    _phone.dispose();
    _otp.dispose();
    super.dispose();
  }

  Future<void> _requestOtp() async {
    FocusScope.of(context).unfocus();
    final ok = await ref
        .read(changePhoneControllerProvider.notifier)
        .requestOtp(phone: _phone.text, l10n: context.l10n);
    if (ok && mounted) setState(() => _otpSent = true);
  }

  Future<void> _submit() async {
    FocusScope.of(context).unfocus();
    final ok = await ref
        .read(changePhoneControllerProvider.notifier)
        .submit(otp: _otp.text, l10n: context.l10n);
    if (ok && mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(context.l10n.changePhoneDone)));
      context.pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final state = ref.watch(changePhoneControllerProvider);
    final pendingPhone =
        ref.read(changePhoneControllerProvider.notifier).pendingPhone ??
        _phone.text.trim();

    return EmeraldSystemOverlay(
      child: Scaffold(
        backgroundColor: context.colors.surface,
        body: Column(
          children: [
            EmeraldSplitHeader(
              title: l10n.changePhoneTitle,
              subtitle: _otpSent
                  ? l10n.changePhoneOtpHint(pendingPhone)
                  : l10n.changePhoneIntro,
            ),
            Expanded(
              child: SafeArea(
                top: false,
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(
                    Gap.lg,
                    Gap.sm,
                    Gap.lg,
                    Gap.xl,
                  ),
                  children: [
                    Container(
                      padding: const EdgeInsets.all(Gap.md),
                      decoration: BoxDecoration(
                        color: context.colors.surfaceContainerLowest,
                        borderRadius: Radii.brXl,
                        border: Border.all(color: context.sweep.hairline),
                        boxShadow: Shadows.e1,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          if (!_otpSent) ...[
                            AuthTextField(
                              label: l10n.changePhoneNewLabel,
                              controller: _phone,
                              hintText: '0901 234 567',
                              prefixIcon: AppIcons.phone,
                              keyboardType: TextInputType.phone,
                              textInputAction: TextInputAction.done,
                              autofillHints: const [
                                AutofillHints.telephoneNumber,
                              ],
                              onSubmitted: (_) => _requestOtp(),
                              errorText: state.fieldErrors['phone'],
                            ),
                            if (state.formError != null) ...[
                              Gap.gapXs,
                              AuthFormError(state.formError!),
                            ],
                            Gap.gapMd,
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
                              prefixIcon: AppIcons.messageCode,
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
                              label: l10n.accountVerifyCta,
                              loading: state.submitting,
                              onPressed: state.submitting ? null : _submit,
                            ),
                            Gap.gapSm,
                            Center(
                              child: TextButton(
                                onPressed:
                                    state.submitting ? null : _requestOtp,
                                child: Text(l10n.authOtpResendCta),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
