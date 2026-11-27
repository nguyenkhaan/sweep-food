import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_icons.dart';

/// The "Thêm nguyên liệu" action. Extended (label) on Kho, plain on the
/// centre nav slot. Opens `AddEntryChooser`.
class AppFab extends StatelessWidget {
  const AppFab({required this.onPressed, this.label, super.key});

  final VoidCallback onPressed;
  final String? label;

  @override
  Widget build(BuildContext context) {
    if (label == null) {
      return FloatingActionButton(
        onPressed: onPressed,
        child: const Icon(AppIcons.add),
      );
    }
    return FloatingActionButton.extended(
      onPressed: onPressed,
      icon: const Icon(AppIcons.add),
      label: Text(label!),
    );
  }
}
