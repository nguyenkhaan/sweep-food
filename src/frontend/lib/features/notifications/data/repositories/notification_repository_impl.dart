import 'package:frontend/core/network/api_result.dart';
import 'package:frontend/core/network/network_providers.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/notifications/data/datasources/notification_remote_data_source.dart';
import 'package:frontend/features/notifications/domain/entities/app_notification.dart';
import 'package:frontend/features/notifications/domain/repositories/notification_repository.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'notification_repository_impl.g.dart';

@Riverpod(keepAlive: true)
NotificationRepository notificationRepository(Ref ref) =>
    NotificationRepositoryImpl(
      NotificationRemoteDataSource(ref.watch(apiClientProvider)),
    );

class NotificationRepositoryImpl implements NotificationRepository {
  NotificationRepositoryImpl(this._remote);

  final NotificationRemoteDataSource _remote;

  @override
  Future<Result<List<AppNotification>>> list() => runGuarded(() async {
        final dtos = await _remote.list();
        final items = [for (final d in dtos) d.toEntity()]
          ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
        return items;
      });

  @override
  Future<Result<void>> markRead(String id) =>
      guardVoid(() => _remote.markRead(id));

  @override
  Future<Result<void>> markAllRead(Iterable<String> ids) => guardVoid(() async {
        await Future.wait([for (final id in ids) _remote.markRead(id)]);
      });
}
