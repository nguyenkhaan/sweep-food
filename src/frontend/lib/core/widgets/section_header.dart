import 'package:flutter/material.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/core/widgets/app_text_button.dart';

/// Overline label with an optional trailing action ("CẦN DÙNG SỚM · Xem tất cả").
class SectionHeader extends StatelessWidget {
  const SectionHeader({
    required this.title,
    this.actionLabel,
    this.onAction,
    super.key,
  });

  final String title;
  final String? actionLabel;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(title.toUpperCase(), style: context.text.labelSmall),
        ),
        if (actionLabel != null && onAction != null)
          AppTextButton(label: actionLabel!, onPressed: onAction),
      ],
    );
  }
}
