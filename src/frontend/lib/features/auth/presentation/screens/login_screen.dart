import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/router/routes.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/primary_button.dart';
import 'package:frontend/features/auth/presentation/controllers/login_controller.dart';
import 'package:frontend/features/auth/presentation/widgets/auth_form_error.dart';
import 'package:frontend/features/auth/presentation/widgets/auth_text_field.dart';
import 'package:go_router/go_router.dart';

/// A-02 Đăng nhập. On success the session flips and `appRedirect` moves the
/// router on — no explicit navigation here.
class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    FocusScope.of(context).unfocus();
    await ref
        .read(loginControllerProvider.notifier)
        .submit(
          email: _email.text,
          password: _password.text,
          l10n: context.l10n,
        );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = context.l10n;
    final state = ref.watch(loginControllerProvider);

    return Scaffold(
      appBar: AppBar(leading: const BackButton()),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.xs, Gap.xl, Gap.xl),
          children: [
            Text(
              l10n.authSignIn,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            Gap.gapXxs,
            Text(
              l10n.loginSubtitle,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            Gap.gapXl,
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
              hintText: '••••••••',
              prefixIcon: Icons.lock_outline_rounded,
              obscureText: state.obscure,
              onToggleObscure: ref
                  .read(loginControllerProvider.notifier)
                  .toggleObscure,
              textInputAction: TextInputAction.done,
              autofillHints: const [AutofillHints.password],
              onSubmitted: (_) => _submit(),
              errorText: state.fieldErrors['password'],
            ),
            Gap.gapXs,
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () => context.push(Routes.forgotPassword),
                child: Text(l10n.authForgotQ),
              ),
            ),
            if (state.formError != null) ...[
              Gap.gapXs,
              AuthFormError(state.formError!),
            ],
            Gap.gapMd,
            PrimaryButton(
              label: l10n.authSignIn,
              loading: state.submitting,
              onPressed: state.submitting ? null : _submit,
            ),
            Gap.gapLg,
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(l10n.loginNoAccount, style: theme.textTheme.bodyMedium),
                GestureDetector(
                  onTap: () => context.push(Routes.register),
                  child: Text(
                    l10n.authSignUp,
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
