import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/widgets/primary_button.dart';
import 'package:frontend/features/auth/presentation/controllers/forgot_password_controller.dart';
import 'package:frontend/features/auth/presentation/widgets/auth_form_error.dart';
import 'package:frontend/features/auth/presentation/widgets/auth_text_field.dart';
import 'package:go_router/go_router.dart';

/// A-04 Quên mật khẩu `[S]` — form, then a "đã gửi" confirmation card.
class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _email = TextEditingController();

  @override
  void dispose() {
    _email.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    FocusScope.of(context).unfocus();
    await ref.read(forgotPasswordControllerProvider.notifier).submit(_email.text);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final state = ref.watch(forgotPasswordControllerProvider);

    return Scaffold(
      appBar: AppBar(leading: const BackButton()),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(Gap.xl, Gap.xs, Gap.xl, Gap.xl),
          children: [
            Text(
              'Quên mật khẩu',
              style: theme.textTheme.headlineSmall
                  ?.copyWith(fontWeight: FontWeight.w700),
            ),
            Gap.gapXxs,
            Text(
              'Nhập email tài khoản, chúng tôi sẽ gửi liên kết đặt lại mật khẩu.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            Gap.gapXl,
            if (state.isSent)
              _SentCard(email: state.sentToEmail!)
            else ...[
              AuthTextField(
                label: 'Email',
                controller: _email,
                hintText: 'ban@email.com',
                prefixIcon: Icons.mail_outline_rounded,
                keyboardType: TextInputType.emailAddress,
                textInputAction: TextInputAction.done,
                autofillHints: const [AutofillHints.email],
                onSubmitted: (_) => _submit(),
                errorText: state.form.fieldErrors['email'],
              ),
              if (state.form.formError != null) ...[
                Gap.gapXs,
                AuthFormError(state.form.formError!),
              ],
              Gap.gapMd,
              PrimaryButton(
                label: 'Gửi liên kết',
                loading: state.form.submitting,
                onPressed: state.form.submitting ? null : _submit,
              ),
            ],
            Gap.gapMd,
            Center(
              child: TextButton(
                onPressed: () => context.pop(),
                child: const Text('Quay lại đăng nhập'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SentCard extends StatelessWidget {
  const _SentCard({required this.email});

  final String email;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(Gap.md),
      decoration: BoxDecoration(
        color: scheme.primaryContainer,
        borderRadius: Radii.brLg,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.mark_email_read_outlined, color: scheme.onPrimaryContainer),
          Gap.gapSm,
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Đã gửi tới $email',
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    color: scheme.onPrimaryContainer,
                  ),
                ),
                Gap.gapXxs,
                Text(
                  'Kiểm tra hộp thư (kể cả mục spam). Liên kết hiệu lực trong 30 phút.',
                  style: TextStyle(
                    fontSize: 12,
                    height: 1.45,
                    color: scheme.onPrimaryContainer.withValues(alpha: 0.85),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
