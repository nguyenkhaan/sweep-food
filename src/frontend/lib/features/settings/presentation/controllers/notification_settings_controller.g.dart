// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notification_settings_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// P-04 Cài đặt thông báo. Persisted as JSON in SharedPreferences; on every
/// change it re-schedules the local near-expiry reminders.

@ProviderFor(NotificationSettingsController)
final notificationSettingsControllerProvider =
    NotificationSettingsControllerProvider._();

/// P-04 Cài đặt thông báo. Persisted as JSON in SharedPreferences; on every
/// change it re-schedules the local near-expiry reminders.
final class NotificationSettingsControllerProvider extends $NotifierProvider<
    NotificationSettingsController, NotificationPreferences> {
  /// P-04 Cài đặt thông báo. Persisted as JSON in SharedPreferences; on every
  /// change it re-schedules the local near-expiry reminders.
  NotificationSettingsControllerProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'notificationSettingsControllerProvider',
          isAutoDispose: false,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$notificationSettingsControllerHash();

  @$internal
  @override
  NotificationSettingsController create() => NotificationSettingsController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(NotificationPreferences value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<NotificationPreferences>(value),
    );
  }
}

String _$notificationSettingsControllerHash() =>
    r'2f926e49d9c5b47a3a44b7ae4c9e15e1ceb3fe8c';

/// P-04 Cài đặt thông báo. Persisted as JSON in SharedPreferences; on every
/// change it re-schedules the local near-expiry reminders.

abstract class _$NotificationSettingsController
    extends $Notifier<NotificationPreferences> {
  NotificationPreferences build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<NotificationPreferences, NotificationPreferences>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<NotificationPreferences, NotificationPreferences>,
        NotificationPreferences,
        Object?,
        Object?>;
    element.handleCreate(ref, build);
  }
}
