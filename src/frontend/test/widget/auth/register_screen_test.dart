import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/core/network/network_providers.dart';
import 'package:sweepfood/features/auth/presentation/screens/register_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

class _MockApiClient extends Mock implements ApiClient {}

Future<_MockApiClient> _pump(WidgetTester tester) async {
  await tester.binding.setSurfaceSize(const Size(800, 1600));
  addTearDown(() => tester.binding.setSurfaceSize(null));
  final api = _MockApiClient();
  when(
    () => api.post(ApiPaths.register, body: any(named: 'body')),
  ).thenAnswer((_) async => {'otp': '123456', 'expires_in_seconds': 300});

  final router = GoRouter(
    routes: [
      GoRoute(path: '/', builder: (_, _) => const RegisterScreen()),
      GoRoute(
        path: Routes.verifyOtp,
        builder: (_, _) => const Scaffold(body: Text('otp screen')),
      ),
    ],
  );
  await tester.pumpWidget(
    ProviderScope(
      overrides: [apiClientProvider.overrideWithValue(api)],
      child: MaterialApp.router(
        locale: const Locale('vi'),
        supportedLocales: AppL10n.supportedLocales,
        localizationsDelegates: AppL10n.localizationsDelegates,
        theme: AppTheme.light,
        routerConfig: router,
      ),
    ),
  );
  await tester.pumpAndSettle();
  return api;
}

// Fields in screen order: name, phone, email, password.
Future<void> _fill(
  WidgetTester tester, {
  required String email,
}) async {
  final fields = find.byType(TextField);
  await tester.enterText(fields.at(0), 'Nguyễn Văn A');
  await tester.enterText(fields.at(1), '0901234567');
  await tester.enterText(fields.at(2), email);
  await tester.enterText(fields.at(3), 'matkhau123');
  await tester.tap(find.byType(Checkbox));
  await tester.pump();
}

void main() {
  testWidgets('the email typed on the form is registered, trimmed and lower-cased', (
    tester,
  ) async {
    final api = await _pump(tester);
    expect(find.text('Email (không bắt buộc)'), findsOneWidget);

    await _fill(tester, email: '  Nguyen.A@Example.COM ');
    await tester.tap(find.text('Tạo tài khoản').last);
    await tester.pumpAndSettle();

    final body =
        verify(
              () => api.post(ApiPaths.register, body: captureAny(named: 'body')),
            ).captured.single
            as Map<String, dynamic>;
    expect(body['email'], 'nguyen.a@example.com');
    expect(body['phone'], '+84901234567');
    expect(find.text('otp screen'), findsOneWidget);
  });

  testWidgets('an invalid email blocks the request and is flagged on the field', (
    tester,
  ) async {
    final api = await _pump(tester);

    await _fill(tester, email: 'not-an-email');
    await tester.tap(find.text('Tạo tài khoản').last);
    await tester.pumpAndSettle();

    expect(find.text('Email không hợp lệ'), findsOneWidget);
    verifyNever(() => api.post(ApiPaths.register, body: any(named: 'body')));
    expect(find.text('otp screen'), findsNothing);
  });

  testWidgets('leaving the email empty still registers, without an email', (
    tester,
  ) async {
    final api = await _pump(tester);

    await _fill(tester, email: '');
    await tester.tap(find.text('Tạo tài khoản').last);
    await tester.pumpAndSettle();

    final body =
        verify(
              () => api.post(ApiPaths.register, body: captureAny(named: 'body')),
            ).captured.single
            as Map<String, dynamic>;
    expect(body.containsKey('email'), isFalse);
    expect(find.text('otp screen'), findsOneWidget);
  });
}
