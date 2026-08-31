import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/locale_controller.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/app/theme/theme_mode_controller.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/core/widgets/app_bottom_sheet.dart';
import 'package:frontend/features/settings/presentation/controllers/preferences_controller.dart';
import 'package:frontend/features/settings/presentation/widgets/settings_group.dart';
import 'package:frontend/l10n/app_localizations.dart';
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
    final l10n = context.l10n;
    final prefs = ref.watch(preferencesControllerProvider);
    final themeMode = ref.watch(themeModeControllerProvider);
    final locale = ref.watch(localeControllerProvider);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.prefsTitle)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
        children: [
          SettingsGroup(
            label: l10n.prefsGroupMeal,
            rows: [
              SettingsRow(
                icon: Icons.tune_rounded,
                label: l10n.prefsDietary,
                trailing: prefs.dietaryPreference.label(l10n),
                onTap: () => _pickDietary(context, ref),
              ),
              SettingsRow(
                icon: Icons.straighten_rounded,
                label: l10n.prefsUnit,
                trailing: prefs.defaultUnit.label,
                onTap: () => _pickUnit(context, ref),
              ),
              SettingsRow(
                icon: Icons.payments_outlined,
                label: l10n.prefsCurrency,
                trailing: l10n.prefsCurrencyValue,
              ),
            ],
          ),
          Gap.gapMd,
          SettingsGroup(
            label: l10n.prefsGroupAppearance,
            rows: [
              SettingsRow(
                icon: Icons.language_rounded,
                label: l10n.prefsLanguage,
                trailing: _localeLabel(l10n, locale),
                onTap: () => _pickLanguage(context, ref),
              ),
              SettingsRow(
                icon: Icons.brightness_6_outlined,
                label: l10n.prefsTheme,
                trailing: switch (themeMode) {
                  ThemeMode.light => l10n.themeLight,
                  ThemeMode.dark => l10n.themeDark,
                  ThemeMode.system => l10n.themeSystem,
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
    final l10n = context.l10n;
    final selected = await showAppBottomSheet<DietaryPreference>(
      context,
      builder: (_) => _OptionSheet<DietaryPreference>(
        title: l10n.prefsDietary,
        options: [
          for (final p in DietaryPreference.values)
            (value: p, label: p.label(l10n), subtitle: p.description(l10n)),
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
        title: context.l10n.prefsUnit,
        options: [
          for (final u in _unitChoices)
            (value: u, label: u.label, subtitle: null),
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
        title: context.l10n.prefsTheme,
        options: [
          (
            value: ThemeMode.light,
            label: context.l10n.themeLight,
            subtitle: null,
          ),
          (
            value: ThemeMode.dark,
            label: context.l10n.themeDark,
            subtitle: null,
          ),
          (
            value: ThemeMode.system,
            label: context.l10n.themeSystem,
            subtitle: null,
          ),
        ],
        current: ref.read(themeModeControllerProvider),
      ),
    );
    if (selected != null) {
      await ref.read(themeModeControllerProvider.notifier).set(selected);
    }
  }

  static String _localeLabel(AppL10n l10n, Locale locale) =>
      locale.languageCode == 'en' ? l10n.langEn : l10n.langVi;

  Future<void> _pickLanguage(BuildContext context, WidgetRef ref) async {
    final l10n = context.l10n;
    final selected = await showAppBottomSheet<Locale>(
      context,
      builder: (_) => _OptionSheet<Locale>(
        title: l10n.prefsLanguage,
        options: [
          (value: const Locale('vi'), label: l10n.langVi, subtitle: null),
          (value: const Locale('en'), label: l10n.langEn, subtitle: null),
        ],
        current: ref.read(localeControllerProvider),
      ),
    );
    if (selected != null) {
      await ref.read(localeControllerProvider.notifier).set(selected);
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
