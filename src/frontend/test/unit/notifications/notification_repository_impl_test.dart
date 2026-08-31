import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/notifications/data/datasources/notification_remote_data_source.dart';
import 'package:sweepfood/features/notifications/data/repositories/notification_repository_impl.dart';
import 'package:sweepfood/features/notifications/domain/entities/app_notification.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient api;
  late NotificationRepositoryImpl repo;

  setUp(() {
    api = _MockApiClient();
    repo = NotificationRepositoryImpl(NotificationRemoteDataSource(api));
  });

  test('list() maps DTOs, resolves the type enum, and sorts newest first',
      () async {
    when(() => api.get(ApiPaths.notifications)).thenAnswer(
      (_) async => {
        'items': [
          {
            'id': 'old',
            'type': 'system',
            'title': 'A',
            'body': 'a',
            'created_at': '2026-08-20T07:00:00.000',
            'read': true,
          },
          {
            'id': 'new',
            'type': 'near_expiry',
            'title': 'B',
            'body': 'b',
            'created_at': '2026-08-30T08:00:00.000',
            'read': false,
            'pantry_item_id': 'p2',
          },
        ],
      },
    );

    final res = await repo.list();
    final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

    expect(list.map((n) => n.id), ['new', 'old']);
    expect(list.first.type, AppNotificationType.nearExpiry);
    expect(list.first.pantryItemId, 'p2');
    expect(list.first.timeLabel, '8:00');
  });

  test('list() returns a Failure (Left) when the client throws', () async {
    when(() => api.get(ApiPaths.notifications)).thenThrow(Exception('boom'));
    expect((await repo.list()).isLeft(), isTrue);
  });

  test('markAllRead() fans out one POST per id', () async {
    when(() => api.post(any())).thenAnswer((_) async => null);
    final res = await repo.markAllRead(['a', 'b', 'c']);
    expect(res.isRight(), isTrue);
    verify(() => api.post(ApiPaths.notificationRead('a'))).called(1);
    verify(() => api.post(ApiPaths.notificationRead('b'))).called(1);
    verify(() => api.post(ApiPaths.notificationRead('c'))).called(1);
  });
}
