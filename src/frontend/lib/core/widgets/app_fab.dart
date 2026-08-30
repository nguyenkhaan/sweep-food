import 'package:flutter/material.dart';

/// The "Thêm nguyên liệu" action. Extended (label) on Kho, plain on the
/// centre nav slot. Opens `AddEntryChooser` (wired in M4).
class AppFab extends StatelessWidget {
  const AppFab({required this.onPressed, this.label, super.key});

  final VoidCallback onPressed;
  final String? label;

  @override
  Widget build(BuildContext context) {
    if (label == null) {
      return FloatingActionButton(
        onPressed: onPressed,
        child: const Icon(Icons.add_rounded),
      );
    }
    return FloatingActionButton.extended(
      onPressed: onPressed,
      icon: const Icon(Icons.add_rounded),
      label: Text(label!),
    );
  }
}
