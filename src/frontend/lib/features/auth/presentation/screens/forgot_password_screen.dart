import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/auth/presentation/controllers/forgot_password_controller.dart';
import 'package:sweepfood/features/auth/presentation/screens/reset_password_screen.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_form_error.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_split_scaffold.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_text_field.dart';

/// A-04 step 1 — Concept B Culinary Split Hero.
class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _phone = TextEditingController();

  @override
  void dispose() {
    _phone.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    FocusScope.of(context).unfocus();
    final phone = await ref
        .read(forgotPasswordControllerProvider.notifier)
        .submit(_phone.text, context.l10n);
    if (phone != null && mounted) {
      context.push(
        Routes.resetPassword,
        extra: ResetPasswordArgs(phone: phone),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final state = ref.watch(forgotPasswordControllerProvider);

    return AuthSplitScaffold(
      title: l10n.authForgotTitle,
      subtitle: l10n.forgotSubtitle,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AuthTextField(
            label: l10n.authPhone,
            controller: _phone,
            hintText: '0901 234 567',
            prefixIcon: AppIcons.phone,
            keyboardType: TextInputType.phone,
            textInputAction: TextInputAction.done,
            autofillHints: const [AutofillHints.telephoneNumber],
            onSubmitted: (_) => _submit(),
            errorText: state.fieldErrors['phone'],
          ),
          if (state.formError != null) ...[
            Gap.gapXs,
            AuthFormError(state.formError!),
          ],
          Gap.gapLg,
          AuthPrimaryButton(
            label: l10n.forgotSendCode,
            loading: state.submitting,
            onPressed: state.submitting ? null : _submit,
          ),
          Gap.gapMd,
          Center(
            child: TextButton(
              style: TextButton.styleFrom(minimumSize: const Size(48, 48)),
              onPressed: () => context.pop(),
              child: Text(l10n.forgotBackToLogin),
            ),
          ),
        ],
      ),
    );
  }
}
