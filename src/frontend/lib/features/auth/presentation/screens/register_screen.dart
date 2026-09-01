import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/primary_button.dart';
import 'package:sweepfood/features/auth/presentation/controllers/register_controller.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_form_error.dart';
import 'package:sweepfood/features/auth/presentation/widgets/auth_text_field.dart';

/// A-03 Tạo tài khoản.
class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _agree = false;

  @override
  void dispose() {
    _name.dispose();
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    FocusScope.of(context).unfocus();
    await ref
        .read(registerControllerProvider.notifier)
        .submit(
          name: _name.text,
          email: _email.text,
          password: _password.text,
          agreedToTerms: _agree,
          l10n: context.l10n,
        );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final state = ref.watch(registerControllerProvider);

    return Scaffold(
      appBar: AppBar(leading: const BackButton()),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.xs, Gap.xl, Gap.xl),
          children: [
            Text(
              l10n.authCreateAccount,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            Gap.gapXxs,
            Text(
              l10n.registerSubtitle,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            Gap.gapXl,
            AuthTextField(
              label: l10n.authFullName,
              controller: _name,
              hintText: l10n.authFullNameHint,
              prefixIcon: Icons.person_outline_rounded,
              textCapitalization: TextCapitalization.words,
              textInputAction: TextInputAction.next,
              autofillHints: const [AutofillHints.name],
              errorText: state.fieldErrors['name'],
            ),
            Gap.gapMd,
            AuthTextField(
              label: l10n.authEmail,
              controller: _email,
              hintText: 'ban@email.com',
              prefixIcon: Icons.mail_outline_rounded,
              keyboardType: TextInputType.emailAddress,
              textInputAction: TextInputAction.next,
              autofillHints: const [AutofillHints.email],
              errorText: state.fieldErrors['email'],
            ),
            Gap.gapMd,
            AuthTextField(
              label: l10n.authPassword,
              controller: _password,
              hintText: l10n.authPasswordHint,
              prefixIcon: Icons.lock_outline_rounded,
              obscureText: state.obscure,
              onToggleObscure: ref
                  .read(registerControllerProvider.notifier)
                  .toggleObscure,
              textInputAction: TextInputAction.done,
              autofillHints: const [AutofillHints.newPassword],
              onSubmitted: (_) => _submit(),
              errorText: state.fieldErrors['password'],
            ),
            Gap.gapSm,
            _TermsCheckbox(
              value: _agree,
              onChanged: (v) => setState(() => _agree = v),
            ),
            if (state.formError != null) ...[
              Gap.gapXs,
              AuthFormError(state.formError!),
            ],
            Gap.gapMd,
            PrimaryButton(
              label: l10n.authCreateAccount,
              loading: state.submitting,
              onPressed: state.submitting ? null : _submit,
            ),
            Gap.gapLg,
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  l10n.registerHaveAccount,
                  style: theme.textTheme.bodyMedium,
                ),
                GestureDetector(
                  onTap: () => context.pushReplacement(Routes.login),
                  child: Text(
                    l10n.authSignIn,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _TermsCheckbox extends StatelessWidget {
  const _TermsCheckbox({required this.value, required this.onChanged});

  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    return InkWell(
      onTap: () => onChanged(!value),
      borderRadius: Radii.brSm,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: Gap.xxs),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Checkbox(
              value: value,
              onChanged: (v) => onChanged(v ?? false),
              visualDensity: VisualDensity.compact,
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
            Gap.gapXs,
            Expanded(
              child: Padding(
                padding: const EdgeInsets.only(top: 10),
                child: Text.rich(
                  TextSpan(
                    text: l10n.termsPrefix,
                    children: [
                      TextSpan(
                        text: l10n.termsOfUse,
                        style: TextStyle(color: theme.colorScheme.primary),
                      ),
                      TextSpan(text: l10n.termsAnd),
                      TextSpan(
                        text: l10n.termsPrivacy,
                        style: TextStyle(color: theme.colorScheme.primary),
                      ),
                      const TextSpan(text: '.'),
                    ],
                  ),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                    height: 1.4,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
