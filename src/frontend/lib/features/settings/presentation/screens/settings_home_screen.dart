import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/app/theme/theme_mode_controller.dart';

/// P-01 Cá nhân.
/// TODO(M5): profile header, plan banner, grouped settings, sign out.
/// For now it carries only the theme-mode switch so M0 can be verified.
class SettingsHomeScreen extends ConsumerWidget {
  const SettingsHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final mode = ref.watch(themeModeControllerProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Cá nhân')),
      body: ListView(
        padding: const EdgeInsets.symmetric(vertical: Gap.md),
        children: [
          Padding(
            padding: Insets.screenH,
            child: Text(
              'GIAO DIỆN',
              style: Theme.of(context).textTheme.labelSmall,
            ),
          ),
          Gap.gapXs,
          RadioGroup<ThemeMode>(
            groupValue: mode,
            onChanged: (v) {
              if (v != null) {
                ref.read(themeModeControllerProvider.notifier).set(v);
              }
            },
            child: Column(
              children: [
                for (final m in ThemeMode.values)
                  RadioListTile<ThemeMode>(
                    value: m,
                    title: Text(
                      switch (m) {
                        ThemeMode.system => 'Theo hệ thống',
                        ThemeMode.light => 'Sáng',
                        ThemeMode.dark => 'Tối',
                      },
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
