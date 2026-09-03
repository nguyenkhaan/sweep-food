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

  test('list() maps the backend shape, resolves the type, sorts newest first',
      () async {
    when(() => api.get(ApiPaths.notifications)).thenAnswer(
      (_) async => {
        'items': [
          {
            'notification_id': 'old',
            'type': 'LEFTOVER_REMINDER',
            'title': 'A',
            'body': 'a',
            'created_at': '2026-08-20T07:00:00.000Z',
            'status': 'DISMISSED',
          },
          {
            'notification_id': 'new',
            'type': 'EXPIRES_TODAY',
            'title': 'B',
            'body': 'b',
            'created_at': '2026-08-30T08:00:00.000Z',
            'status': 'UNREAD',
            'inventory_batch_id': 'b2',
          },
        ],
        'next_before': null,
      },
    );

    final res = await repo.list();
    final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

    expect(list.map((n) => n.id), ['new', 'old']);
    expect(list.first.type, AppNotificationType.nearExpiry);
    expect(list.first.pantryItemId, 'b2'); // backend inventory_batch_id
    expect(list.first.read, isFalse); // UNREAD
    expect(list.last.read, isTrue); // DISMISSED counts as read
    expect(list.last.type, AppNotificationType.nearExpiry); // LEFTOVER_REMINDER
  });

  test('list() returns a Failure (Left) when the client throws', () async {
    when(() => api.get(ApiPaths.notifications)).thenThrow(Exception('boom'));
    expect((await repo.list()).isLeft(), isTrue);
  });

  test('markRead() PATCHes /notifications/{id} with status READ', () async {
    when(() => api.patch(any(), body: any(named: 'body')))
        .thenAnswer((_) async => null);

    final res = await repo.markRead('n1');

    expect(res.isRight(), isTrue);
    final body = verify(
      () => api.patch(ApiPaths.notification('n1'), body: captureAny(named: 'body')),
    ).captured.single as Map<String, dynamic>;
    expect(body, {'status': 'READ'});
  });

  test('markAllRead() fans out one PATCH per id', () async {
    when(() => api.patch(any(), body: any(named: 'body')))
        .thenAnswer((_) async => null);

    final res = await repo.markAllRead(['a', 'b', 'c']);

    expect(res.isRight(), isTrue);
    verify(() => api.patch(ApiPaths.notification('a'), body: {'status': 'READ'}))
        .called(1);
    verify(() => api.patch(ApiPaths.notification('b'), body: {'status': 'READ'}))
        .called(1);
    verify(() => api.patch(ApiPaths.notification('c'), body: {'status': 'READ'}))
        .called(1);
  });
}
