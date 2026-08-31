import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/app/theme/theme_mode_controller.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_bottom_sheet.dart';
import 'package:frontend/features/settings/presentation/controllers/preferences_controller.dart';
import 'package:frontend/features/settings/presentation/widgets/settings_group.dart';
import 'package:frontend/shared/domain/dietary_preference.dart';
import 'package:frontend/shared/domain/measurement_unit.dart';

/// P-03 Tùy chọn — dietary preference, default unit, language, theme.
class PreferencesScreen extends ConsumerWidget {
  const PreferencesScreen({super.key});

  static const _unitChoices = [
    MeasurementUnit.gram,
    MeasurementUnit.kilogram,
    MeasurementUnit.milliliter,
    MeasurementUnit.piece,
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final prefs = ref.watch(preferencesControllerProvider);
    final themeMode = ref.watch(themeModeControllerProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Tùy chọn')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
        children: [
          SettingsGroup(
            label: 'Bữa ăn',
            rows: [
              SettingsRow(
                icon: Icons.tune_rounded,
                label: 'Ưu tiên dinh dưỡng',
                trailing: prefs.dietaryPreference.label,
                onTap: () => _pickDietary(context, ref),
              ),
              SettingsRow(
                icon: Icons.straighten_rounded,
                label: 'Đơn vị đo mặc định',
                trailing: prefs.defaultUnit.label,
                onTap: () => _pickUnit(context, ref),
              ),
              const SettingsRow(
                icon: Icons.payments_outlined,
                label: 'Tiền tệ hiển thị',
                trailing: 'VND (đ)',
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            label: 'Giao diện',
            rows: [
              const SettingsRow(
                icon: Icons.language_rounded,
                label: 'Ngôn ngữ',
                trailing: 'Tiếng Việt',
              ),
              SettingsRow(
                icon: Icons.brightness_6_outlined,
                label: 'Chủ đề',
                trailing: switch (themeMode) {
                  ThemeMode.light => 'Sáng',
                  ThemeMode.dark => 'Tối',
                  ThemeMode.system => 'Theo hệ thống',
                },
                onTap: () => _pickTheme(context, ref),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _pickDietary(BuildContext context, WidgetRef ref) async {
    final selected = await showAppBottomSheet<DietaryPreference>(
      context,
      builder: (_) => _OptionSheet<DietaryPreference>(
        title: 'Ưu tiên dinh dưỡng',
        options: [
          for (final p in DietaryPreference.values)
            (value: p, label: p.label, subtitle: p.description),
        ],
        current: ref.read(preferencesControllerProvider).dietaryPreference,
      ),
    );
    if (selected != null) {
      await ref
          .read(preferencesControllerProvider.notifier)
          .setDietaryPreference(selected);
    }
  }

  Future<void> _pickUnit(BuildContext context, WidgetRef ref) async {
    final selected = await showAppBottomSheet<MeasurementUnit>(
      context,
      builder: (_) => _OptionSheet<MeasurementUnit>(
        title: 'Đơn vị đo mặc định',
        options: [
          for (final u in _unitChoices) (value: u, label: u.label, subtitle: null),
        ],
        current: ref.read(preferencesControllerProvider).defaultUnit,
      ),
    );
    if (selected != null) {
      await ref
          .read(preferencesControllerProvider.notifier)
          .setDefaultUnit(selected);
    }
  }

  Future<void> _pickTheme(BuildContext context, WidgetRef ref) async {
    final selected = await showAppBottomSheet<ThemeMode>(
      context,
      builder: (_) => _OptionSheet<ThemeMode>(
        title: 'Chủ đề',
        options: const [
          (value: ThemeMode.light, label: 'Sáng', subtitle: null),
          (value: ThemeMode.dark, label: 'Tối', subtitle: null),
          (value: ThemeMode.system, label: 'Theo hệ thống', subtitle: null),
        ],
        current: ref.read(themeModeControllerProvider),
      ),
    );
    if (selected != null) {
      await ref.read(themeModeControllerProvider.notifier).set(selected);
    }
  }
}

class _OptionSheet<T> extends StatelessWidget {
  const _OptionSheet({
    required this.title,
    required this.options,
    required this.current,
  });

  final String title;
  final List<({T value, String label, String? subtitle})> options;
  final T current;

  @override
  Widget build(BuildContext context) {
    return SheetBody(
      title: title,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          for (final o in options)
            ListTile(
              contentPadding: EdgeInsets.zero,
              onTap: () => Navigator.of(context).pop(o.value),
              title: Text(o.label),
              subtitle: o.subtitle == null ? null : Text(o.subtitle!),
              trailing: o.value == current
                  ? Icon(Icons.check_rounded, color: context.colors.primary)
                  : null,
            ),
        ],
      ),
    );
  }
}
