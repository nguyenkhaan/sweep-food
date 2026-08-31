// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notifications_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// T-01 Trung tâm thông báo. Loads the list; `markRead` / `markAllRead` update
/// optimistically and roll back on failure.

@ProviderFor(NotificationsController)
final notificationsControllerProvider = NotificationsControllerProvider._();

/// T-01 Trung tâm thông báo. Loads the list; `markRead` / `markAllRead` update
/// optimistically and roll back on failure.
final class NotificationsControllerProvider
    extends
        $AsyncNotifierProvider<NotificationsController, List<AppNotification>> {
  /// T-01 Trung tâm thông báo. Loads the list; `markRead` / `markAllRead` update
  /// optimistically and roll back on failure.
  NotificationsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'notificationsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$notificationsControllerHash();

  @$internal
  @override
  NotificationsController create() => NotificationsController();
}

String _$notificationsControllerHash() =>
    r'827cfa54a3145954423d207a77aad460ef0b82fe';

/// T-01 Trung tâm thông báo. Loads the list; `markRead` / `markAllRead` update
/// optimistically and roll back on failure.

abstract class _$NotificationsController
    extends $AsyncNotifier<List<AppNotification>> {
  FutureOr<List<AppNotification>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<AsyncValue<List<AppNotification>>, List<AppNotification>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<AppNotification>>,
                List<AppNotification>
              >,
              AsyncValue<List<AppNotification>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// Unread badge count for the Home bell.

@ProviderFor(unreadNotificationCount)
final unreadNotificationCountProvider = UnreadNotificationCountProvider._();

/// Unread badge count for the Home bell.

final class UnreadNotificationCountProvider
    extends $FunctionalProvider<int, int, int>
    with $Provider<int> {
  /// Unread badge count for the Home bell.
  UnreadNotificationCountProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'unreadNotificationCountProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$unreadNotificationCountHash();

  @$internal
  @override
  $ProviderElement<int> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  int create(Ref ref) {
    return unreadNotificationCount(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(int value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<int>(value),
    );
  }
}

String _$unreadNotificationCountHash() =>
    r'05a262403e730c1ea356b6ce4c8c6798533d4483';

@ProviderFor(groupedNotifications)
final groupedNotificationsProvider = GroupedNotificationsProvider._();

final class GroupedNotificationsProvider
    extends
        $FunctionalProvider<
          List<NotificationDay>,
          List<NotificationDay>,
          List<NotificationDay>
        >
    with $Provider<List<NotificationDay>> {
  GroupedNotificationsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'groupedNotificationsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$groupedNotificationsHash();

  @$internal
  @override
  $ProviderElement<List<NotificationDay>> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  List<NotificationDay> create(Ref ref) {
    return groupedNotifications(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(List<NotificationDay> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<List<NotificationDay>>(value),
    );
  }
}

String _$groupedNotificationsHash() =>
    r'b04186f9c3584dbcbda67d9270dcb845d693781a';
