import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';

class _MockApiClient extends Mock implements ApiClient {}

class _MockSecureStore extends Mock implements SecureStore {}

Map<String, dynamic> _session({
  required String id,
  String? ip = '203.0.113.7',
  String? ua = 'Mozilla/5.0 (Linux; Android 14) Chrome/120',
  String? lastUsed = '2026-09-06T09:00:00.000Z',
}) => {
      'id': id,
      'ip_address': ip,
      'user_agent': ua,
      'expires_at': '2026-10-01T09:00:00.000Z',
      'created_at': '2026-09-01T09:00:00.000Z',
      'last_used_at': lastUsed,
    };

void main() {
  late _MockApiClient api;
  late AuthRepositoryImpl repo;

  setUp(() {
    api = _MockApiClient();
    repo = AuthRepositoryImpl(AuthRemoteDataSource(api), _MockSecureStore());
  });

  group('activeSessions()', () {
    test('maps GET /auth/sessions array rows to entities', () async {
      when(() => api.get(ApiPaths.sessions)).thenAnswer(
        (_) async => [
          _session(id: 's1'),
          _session(
            id: 's2',
            ua: 'SweepFood/1.0 (iPhone; iOS 17)',
            ip: null,
            lastUsed: null,
          ),
        ],
      );

      final res = await repo.activeSessions();
      final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

      expect(list, hasLength(2));
      expect(list.first.id, 's1');
      expect(list.first.ipAddress, '203.0.113.7');
      expect(list.first.deviceLabel, 'Android · Chrome');
      expect(list.first.expiresAt, DateTime.utc(2026, 10, 1, 9));
      expect(list[1].lastUsedAt, isNull);
      expect(list[1].deviceLabel, 'iPhone · Ứng dụng SweepFood');
    });

    test('deviceLabel falls back to the IP then a generic label', () async {
      when(() => api.get(ApiPaths.sessions)).thenAnswer(
        (_) async => [
          _session(id: 's1', ua: '', ip: '10.0.0.9', lastUsed: null),
          _session(id: 's2', ua: null, ip: null, lastUsed: null),
        ],
      );

      final res = await repo.activeSessions();
      final list = res.fold((f) => fail('expected Right, got $f'), (r) => r);

      expect(list.first.deviceLabel, '10.0.0.9');
      expect(list[1].deviceLabel, 'Thiết bị không xác định');
    });

    test('returns a Failure when the client throws', () async {
      when(() => api.get(ApiPaths.sessions)).thenThrow(Exception('offline'));
      final res = await repo.activeSessions();
      expect(res.isLeft(), isTrue);
    });
  });

  group('revokeSession()', () {
    test('DELETEs /auth/sessions/{id}', () async {
      when(() => api.delete(ApiPaths.session('s2'))).thenAnswer((_) async => null);

      final res = await repo.revokeSession('s2');

      expect(res.isRight(), isTrue);
      verify(() => api.delete('/auth/sessions/s2')).called(1);
    });

    test('returns a Failure when the delete throws', () async {
      when(() => api.delete(ApiPaths.session('s2')))
          .thenThrow(Exception('boom'));
      final res = await repo.revokeSession('s2');
      expect(res.isLeft(), isTrue);
    });
  });
}
