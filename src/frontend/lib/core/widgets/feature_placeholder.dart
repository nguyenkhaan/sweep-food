import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';

/// Temporary body for screens not yet implemented in the current milestone.
/// Replace the whole screen when its milestone comes up (see IMPLEMENTATION_PLAN.md).
class FeaturePlaceholder extends StatelessWidget {
  const FeaturePlaceholder({
    required this.title,
    this.milestone,
    super.key,
  });

  final String title;
  final String? milestone;

  @override
  Widget build(BuildContext context) {
    final t = Theme.of(context).textTheme;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(Gap.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.construction_rounded,
              size: 40,
              color: Theme.of(context).colorScheme.outline,
            ),
            Gap.gapSm,
            Text(title, style: t.titleMedium, textAlign: TextAlign.center),
            if (milestone != null) ...[
              Gap.gapXxs,
              Text(
                'Sẽ hiện thực ở $milestone',
                style: t.bodyMedium,
                textAlign: TextAlign.center,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
