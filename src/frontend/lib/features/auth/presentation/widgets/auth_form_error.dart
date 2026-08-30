import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';

/// Form-level error banner for the auth forms (wrong credentials, "cần đồng ý
/// điều khoản", server errors). Per-field 422 errors render inline on the field
/// instead.
class AuthFormError extends StatelessWidget {
  const AuthFormError(this.message, {super.key});

  final String message;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(Gap.sm),
      decoration: BoxDecoration(
        color: scheme.errorContainer,
        borderRadius: Radii.brMd,
      ),
      child: Row(
        children: [
          Icon(
            Icons.error_outline_rounded,
            size: 18,
            color: scheme.onErrorContainer,
          ),
          Gap.gapXs,
          Expanded(
            child: Text(
              message,
              style: TextStyle(color: scheme.onErrorContainer, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }
}
