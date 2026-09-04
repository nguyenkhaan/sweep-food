import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/features/notifications/data/datasources/device_remote_data_source.dart';
import 'package:sweepfood/features/notifications/data/repositories/device_repository_impl.dart';

class _MockApiClient extends Mock implements ApiClient {}

void main() {
  late _MockApiClient api;
  late DeviceRepositoryImpl repo;

  setUp(() {
    api = _MockApiClient();
    repo = DeviceRepositoryImpl(DeviceRemoteDataSource(api));
  });

  group('register()', () {
    test('POSTs token + platform and returns the server device_id', () async {
      when(() => api.post(ApiPaths.devices, body: any(named: 'body'))).thenAnswer(
        (_) async => {
          'device_id': 'dev-123',
          'platform': 'ANDROID',
          'is_enabled': true,
          'last_seen_at': '2026-09-04T10:00:00Z',
        },
      );

      final res = await repo.register('a-fcm-token', platform: 'ANDROID');

      expect(res.fold((f) => fail('$f'), (id) => id), 'dev-123');
      final body = verify(
        () => api.post(ApiPaths.devices, body: captureAny(named: 'body')),
      ).captured.single as Map<String, dynamic>;
      expect(body, {'fcm_token': 'a-fcm-token', 'platform': 'ANDROID'});
    });

    test('returns a Failure when the request throws', () async {
      when(() => api.post(ApiPaths.devices, body: any(named: 'body')))
          .thenThrow(Exception('boom'));

      expect((await repo.register('t', platform: 'ANDROID')).isLeft(), isTrue);
    });
  });

  group('unregister()', () {
    test('DELETEs /users/me/devices/{device_id}', () async {
      when(() => api.delete(ApiPaths.device('dev-123')))
          .thenAnswer((_) async => null);

      final res = await repo.unregister('dev-123');

      expect(res.isRight(), isTrue);
      verify(() => api.delete('/users/me/devices/dev-123')).called(1);
    });
  });
}
