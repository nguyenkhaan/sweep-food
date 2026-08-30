import 'package:flutter/material.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';

/// Opens a themed modal bottom sheet (rounded top, drag handle, safe-area
/// padded). Use for K-04, D-03/D-04/D-06, S-02, G-03, G-04…
Future<T?> showAppBottomSheet<T>(
  BuildContext context, {
  required WidgetBuilder builder,
  bool isScrollControlled = true,
}) {
  return showModalBottomSheet<T>(
    context: context,
    isScrollControlled: isScrollControlled,
    useSafeArea: true,
    builder: (ctx) => Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.viewInsetsOf(ctx).bottom),
      child: builder(ctx),
    ),
  );
}

/// Standard sheet body: optional title + subtitle above [child].
class SheetBody extends StatelessWidget {
  const SheetBody({
    required this.child,
    this.title,
    this.subtitle,
    super.key,
  });

  final Widget child;
  final String? title;
  final String? subtitle;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: Insets.sheet,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (title != null)
            Text(title!, style: context.text.titleMedium),
          if (subtitle != null) ...[
            const SizedBox(height: 2),
            Text(subtitle!, style: context.text.bodyMedium),
          ],
          if (title != null || subtitle != null) Gap.gapMd,
          child,
        ],
      ),
    );
  }
}
