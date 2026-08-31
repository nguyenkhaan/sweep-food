import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';

/// Full-body error state with a retry button (spec 3.3).
class ErrorView extends StatelessWidget {
  const ErrorView({required String this.message, this.onRetry, super.key})
    : failure = null;

  const ErrorView.fromFailure(Failure this.failure, {this.onRetry, super.key})
    : message = null;

  /// Explicit message; when null the localized [failure] text is shown.
  final String? message;
  final Failure? failure;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    final message = this.message ?? failure!.localizedMessage(context.l10n);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(Gap.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: context.sweep.expired.bg,
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.error_outline_rounded,
                size: 30,
                color: context.sweep.expired.fg,
              ),
            ),
            Gap.gapSm,
            Text(
              message,
              style: context.text.titleSmall,
              textAlign: TextAlign.center,
            ),
            if (onRetry != null) ...[
              Gap.gapMd,
              OutlinedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh_rounded, size: 18),
                label: Text(context.l10n.commonRetry),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
