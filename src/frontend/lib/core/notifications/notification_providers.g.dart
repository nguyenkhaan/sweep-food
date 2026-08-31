// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notification_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(flutterLocalNotificationsPlugin)
final flutterLocalNotificationsPluginProvider =
    FlutterLocalNotificationsPluginProvider._();

final class FlutterLocalNotificationsPluginProvider
    extends
        $FunctionalProvider<
          FlutterLocalNotificationsPlugin,
          FlutterLocalNotificationsPlugin,
          FlutterLocalNotificationsPlugin
        >
    with $Provider<FlutterLocalNotificationsPlugin> {
  FlutterLocalNotificationsPluginProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'flutterLocalNotificationsPluginProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$flutterLocalNotificationsPluginHash();

  @$internal
  @override
  $ProviderElement<FlutterLocalNotificationsPlugin> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  FlutterLocalNotificationsPlugin create(Ref ref) {
    return flutterLocalNotificationsPlugin(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(FlutterLocalNotificationsPlugin value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<FlutterLocalNotificationsPlugin>(
        value,
      ),
    );
  }
}

String _$flutterLocalNotificationsPluginHash() =>
    r'2db49bbfb81bcbc2aafa571e10dd243629d78385';

/// Local (on-device) notifications — the MVP reminder channel.

@ProviderFor(localNotifications)
final localNotificationsProvider = LocalNotificationsProvider._();

/// Local (on-device) notifications — the MVP reminder channel.

final class LocalNotificationsProvider
    extends
        $FunctionalProvider<
          LocalNotifications,
          LocalNotifications,
          LocalNotifications
        >
    with $Provider<LocalNotifications> {
  /// Local (on-device) notifications — the MVP reminder channel.
  LocalNotificationsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'localNotificationsProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$localNotificationsHash();

  @$internal
  @override
  $ProviderElement<LocalNotifications> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  LocalNotifications create(Ref ref) {
    return localNotifications(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(LocalNotifications value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<LocalNotifications>(value),
    );
  }
}

String _$localNotificationsHash() =>
    r'8dba3e59c378aeb07fe2444e5a7fef9ff5e5ad54';

/// FCM — no-op until M6 (see [FcmService]).

@ProviderFor(fcmService)
final fcmServiceProvider = FcmServiceProvider._();

/// FCM — no-op until M6 (see [FcmService]).

final class FcmServiceProvider
    extends $FunctionalProvider<FcmService, FcmService, FcmService>
    with $Provider<FcmService> {
  /// FCM — no-op until M6 (see [FcmService]).
  FcmServiceProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'fcmServiceProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$fcmServiceHash();

  @$internal
  @override
  $ProviderElement<FcmService> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  FcmService create(Ref ref) {
    return fcmService(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(FcmService value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<FcmService>(value),
    );
  }
}

String _$fcmServiceHash() => r'52a55b21750e81c6b4af8b365a7fbdcb73ad97ab';
