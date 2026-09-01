import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/core/error/failure.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/storage/secure_storage.dart';
import 'package:sweepfood/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:sweepfood/features/auth/data/repositories/auth_repository_impl.dart';

class _MockApiClient extends Mock implements ApiClient {}

class _MockSecureStore extends Mock implements SecureStore {}

Map<String, dynamic> _profile() => {
      'user_id': 'u1',
      'name': 'Mai',
      'phone': '+84901234567',
      'phone_verified_at': null,
      'email': 'mai@example.com',
      'email_verified_at': null,
      'preferences': <String, dynamic>{},
    };

Map<String, dynamic> _otp() => {'otp': '123456', 'expires_in_seconds': 300};

void main() {
  late _MockApiClient api;
  late _MockSecureStore store;
  late AuthRepositoryImpl repo;

  setUp(() {
    api = _MockApiClient();
    store = _MockSecureStore();
    repo = AuthRepositoryImpl(AuthRemoteDataSource(api), store);
  });

  group('updateProfile()', () {
    test('PATCHes /users/profile and maps the response to a User', () async {
      when(() => api.patch(ApiPaths.profile, body: any(named: 'body')))
          .thenAnswer((_) async => _profile());

      final res = await repo.updateProfile(name: 'Mai');

      final user = res.fold((f) => fail('expected Right, got $f'), (u) => u);
      expect(user.id, 'u1');
      expect(user.name, 'Mai');
      expect(user.email, 'mai@example.com');
      final captured = verify(
        () => api.patch(ApiPaths.profile, body: captureAny(named: 'body')),
      ).captured.single as Map<String, dynamic>;
      expect(captured, {'name': 'Mai'});
    });

    test('returns a Failure when the request throws', () async {
      when(() => api.patch(ApiPaths.profile, body: any(named: 'body')))
          .thenThrow(Exception('boom'));

      final res = await repo.updateProfile(name: 'x');

      expect(res.isLeft(), isTrue);
    });
  });

  group('password change', () {
    test('requestPasswordChange returns the OTP lifetime', () async {
      when(() => api.post(ApiPaths.passwordChange))
          .thenAnswer((_) async => _otp());

      final res = await repo.requestPasswordChange();

      expect(res.fold((f) => fail('$f'), (ttl) => ttl), 300);
    });

    test('confirmPasswordChange sends purpose CHANGE_PASSWORD', () async {
      when(() => api.post(ApiPaths.verifyChangePassword, body: any(named: 'body')))
          .thenAnswer((_) async => {'message': 'ok'});

      final res = await repo.confirmPasswordChange(
        phone: '+84901234567',
        otp: '123456',
        newPassword: 'newsecret12',
      );

      expect(res.isRight(), isTrue);
      final body = verify(
        () => api.post(
          ApiPaths.verifyChangePassword,
          body: captureAny(named: 'body'),
        ),
      ).captured.single as Map<String, dynamic>;
      expect(body['purpose'], 'CHANGE_PASSWORD');
      expect(body['new_password'], 'newsecret12');
      expect(body['phone'], '+84901234567');
    });
  });

  group('email change', () {
    test('requestEmailChange posts the address and returns the lifetime',
        () async {
      when(() => api.post(ApiPaths.meEmailRequest, body: any(named: 'body')))
          .thenAnswer((_) async => _otp());

      final res = await repo.requestEmailChange('new@example.com');

      expect(res.fold((f) => fail('$f'), (ttl) => ttl), 300);
      final body = verify(
        () => api.post(ApiPaths.meEmailRequest, body: captureAny(named: 'body')),
      ).captured.single as Map<String, dynamic>;
      expect(body, {'email': 'new@example.com'});
    });

    test('confirmEmailChange posts the OTP', () async {
      when(() => api.post(ApiPaths.meEmailVerify, body: any(named: 'body')))
          .thenAnswer((_) async => 'Verify Change Email successfully');

      final res = await repo.confirmEmailChange('123456');

      expect(res.isRight(), isTrue);
      final body = verify(
        () => api.post(ApiPaths.meEmailVerify, body: captureAny(named: 'body')),
      ).captured.single as Map<String, dynamic>;
      expect(body, {'otp': '123456'});
    });
  });

  group('phone change', () {
    test('requestPhoneChange posts the number and returns the lifetime',
        () async {
      when(() => api.post(ApiPaths.mePhoneRequest, body: any(named: 'body')))
          .thenAnswer((_) async => _otp());

      final res = await repo.requestPhoneChange('+84909999999');

      expect(res.fold((f) => fail('$f'), (ttl) => ttl), 300);
      final body = verify(
        () => api.post(ApiPaths.mePhoneRequest, body: captureAny(named: 'body')),
      ).captured.single as Map<String, dynamic>;
      expect(body, {'phone': '+84909999999'});
    });

    test('confirmPhoneChange maps a thrown ValidationFailure through', () async {
      when(() => api.post(ApiPaths.mePhoneConfirm, body: any(named: 'body')))
          .thenThrow(const ValidationFailure(message: 'bad otp'));

      final res = await repo.confirmPhoneChange('000000');

      expect(res.isLeft(), isTrue);
      res.fold((f) => expect(f, isA<ValidationFailure>()), (_) => fail('!'));
    });
  });
}
