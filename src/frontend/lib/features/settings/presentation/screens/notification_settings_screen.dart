import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/app/theme/app_spacing.dart';
import 'package:frontend/core/utils/extensions/build_context_x.dart';
import 'package:frontend/features/settings/presentation/controllers/notification_settings_controller.dart';
import 'package:frontend/features/settings/presentation/widgets/settings_group.dart';

/// P-04 Cài đặt thông báo — per-type toggles + timing.
class NotificationSettingsScreen extends ConsumerWidget {
  const NotificationSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final prefs = ref.watch(notificationSettingsControllerProvider);
    final ctrl = ref.read(notificationSettingsControllerProvider.notifier);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.notifTitle)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Gap.lg, Gap.md, Gap.lg, Gap.xxl),
        children: [
          Padding(
            padding: const EdgeInsets.only(left: Gap.xxs, bottom: Gap.xs),
            child: Text(
              l10n.notifSettingsTypesHeader,
              style: context.text.labelSmall,
            ),
          ),
          Container(
            decoration: BoxDecoration(
              color: context.colors.surfaceContainerLowest,
              borderRadius: Radii.brLg,
              border: Border.all(color: context.sweep.hairline),
            ),
            child: Column(
              children: [
                _ToggleRow(
                  label: l10n.notifTypeNearExpiry,
                  subtitle: l10n.notifTypeNearExpirySub,
                  value: prefs.nearExpiry,
                  onChanged: ctrl.toggleNearExpiry,
                ),
                _divider(context),
                _ToggleRow(
                  label: l10n.notifTypeDailySuggestions,
                  value: prefs.dailySuggestions,
                  onChanged: ctrl.toggleDailySuggestions,
                ),
                _divider(context),
                _ToggleRow(
                  label: l10n.notifTypeWeeklyReport,
                  value: prefs.weeklyReport,
                  onChanged: ctrl.toggleWeeklyReport,
                ),
                _divider(context),
                _ToggleRow(
                  label: l10n.notifTypePostCook,
                  value: prefs.postCookReminder,
                  onChanged: ctrl.togglePostCookReminder,
                ),
                _divider(context),
                _ToggleRow(
                  label: l10n.notifTypePromos,
                  value: prefs.promosAndTips,
                  onChanged: ctrl.togglePromosAndTips,
                ),
              ],
            ),
          ),
          Gap.gapMd,
          SettingsGroup(
            label: l10n.notifSettingsTiming,
            rows: [
              SettingsRow(
                icon: Icons.schedule_rounded,
                label: l10n.notifRemindAt,
                trailing: prefs.nearExpiryTimeLabel,
                onTap: () async {
                  final picked = await showTimePicker(
                    context: context,
                    initialTime: TimeOfDay(
                      hour: prefs.nearExpiryHour,
                      minute: 0,
                    ),
                  );
                  if (picked != null) await ctrl.setNearExpiryHour(picked.hour);
                },
              ),
              SettingsRow(
                icon: Icons.do_not_disturb_on_outlined,
                label: l10n.notifDnd,
                trailing: prefs.dndWindowLabel,
                onTap: () => _editDnd(
                  context,
                  ref,
                  prefs.dndStartHour,
                  prefs.dndEndHour,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _divider(BuildContext context) =>
      Divider(height: 1, color: context.sweep.hairline, indent: Gap.md);

  Future<void> _editDnd(
    BuildContext context,
    WidgetRef ref,
    int start,
    int end,
  ) async {
    final s = await showTimePicker(
      context: context,
      initialTime: TimeOfDay(hour: start, minute: 0),
      helpText: context.l10n.notifDndStart,
    );
    if (s == null || !context.mounted) return;
    final e = await showTimePicker(
      context: context,
      initialTime: TimeOfDay(hour: end, minute: 0),
      helpText: context.l10n.notifDndEnd,
    );
    if (e == null) return;
    await ref
        .read(notificationSettingsControllerProvider.notifier)
        .setDndWindow(start: s.hour, end: e.hour);
  }
}

class _ToggleRow extends StatelessWidget {
  const _ToggleRow({
    required this.label,
    required this.value,
    required this.onChanged,
    this.subtitle,
  });

  final String label;
  final String? subtitle;
  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    return SwitchListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: Gap.md),
      value: value,
      onChanged: onChanged,
      title: Text(
        label,
        style: context.text.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
      ),
      subtitle: subtitle == null
          ? null
          : Text(
              subtitle!,
              style: context.text.bodySmall?.copyWith(
                color: context.sweep.textSecondary,
              ),
            ),
    );
  }
}
