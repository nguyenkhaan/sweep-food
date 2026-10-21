import 'dart:async';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart' show Override;
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sweepfood/app/router/routes.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/media/media_providers.dart';
import 'package:sweepfood/core/permissions/permission_service.dart';
import 'package:sweepfood/core/utils/result.dart';
import 'package:sweepfood/features/ingest/data/repositories/scan_repository_impl.dart';
import 'package:sweepfood/features/ingest/domain/entities/scan_job.dart';
import 'package:sweepfood/features/ingest/presentation/screens/camera_capture_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

import '../../helpers/ingest_fixtures.dart';
import '../../helpers/media_fakes.dart';
import '../../helpers/mocks.dart';

Widget _screen(List<Override> overrides) => ProviderScope(
  overrides: [
    imageCaptureServiceProvider.overrideWithValue(
      FakeImageCaptureService(path: null),
    ),
    ...overrides,
  ],
  child: MaterialApp(
    locale: const Locale('vi'),
    supportedLocales: AppL10n.supportedLocales,
    localizationsDelegates: AppL10n.localizationsDelegates,
    theme: AppTheme.light,
    home: const CameraCaptureScreen(),
  ),
);

Future<void> _tick(WidgetTester tester) async {
  await tester.pump();
  await tester.pump(const Duration(milliseconds: 50));
  await tester.pump(const Duration(milliseconds: 50));
}

/// The camera-startup fallback deliberately contains an indeterminate spinner
/// while the platform camera API is unavailable in widget tests. Route changes
/// therefore need a bounded wait rather than `pumpAndSettle`.
Future<void> _settleRoute(WidgetTester tester) async {
  await tester.pump();
  await tester.runAsync(
    () => Future<void>.delayed(const Duration(milliseconds: 1)),
  );
  await tester.pump();
  await tester.pump(const Duration(milliseconds: 350));
}

void main() {
  testWidgets('mounts with the scan chrome and no crash', (tester) async {
    await tester.pumpWidget(
      _screen([
        permissionServiceProvider.overrideWithValue(
          const GrantedPermissionService(),
        ),
      ]),
    );
    await _tick(tester);

    expect(tester.takeException(), isNull);
    expect(find.text('Quét tem nhãn'), findsOneWidget);
    expect(find.text('Tem nhãn'), findsOneWidget); // mode chip
    expect(find.text('Nhập tay'), findsOneWidget);
    // Permission was granted → the "grant" fallback never shows.
    expect(find.text('Cấp quyền máy ảnh'), findsNothing);
  });

  testWidgets('permission refused → shows the "Cấp quyền máy ảnh" CTA', (
    tester,
  ) async {
    await tester.pumpWidget(
      _screen([
        permissionServiceProvider.overrideWithValue(
          const _DeniedPermissionService(),
        ),
      ]),
    );
    await _tick(tester);

    // Drive the G-04 priming sheet: "Cho phép" → request denied → helper false.
    expect(find.text('Cho phép'), findsOneWidget);
    await tester.tap(find.text('Cho phép'));
    await _tick(tester);
    await tester.pump(const Duration(milliseconds: 300));

    expect(tester.takeException(), isNull);
    expect(find.text('Cấp quyền máy ảnh'), findsOneWidget);
    expect(find.text('Dùng ảnh có sẵn'), findsOneWidget);
  });

  group('while a scan is in flight', () {
    // No CameraController in tests (availableCameras has no platform impl),
    // so drive the shared busy flow through the gallery button instead.
    const picked = '/tmp/fake_capture.jpg';
    late MockScanRepository repo;
    late Completer<Result<ScanJob>> response;
    late GoRouter router;

    setUp(() {
      repo = MockScanRepository();
      response = Completer<Result<ScanJob>>();
      when(() => repo.scanLabel(any())).thenAnswer((_) => response.future);
      router = GoRouter(
        routes: [
          GoRoute(path: '/', builder: (_, __) => const CameraCaptureScreen()),
          GoRoute(
            path: '${Routes.pantry}/${Routes.scanLabelReview}',
            builder: (_, __) => const Scaffold(body: Text('label-review')),
          ),
          GoRoute(
            path: '${Routes.pantry}/${Routes.scanFailed}',
            builder: (_, __) => const Scaffold(body: Text('scan-failed')),
          ),
        ],
      );
      addTearDown(router.dispose);
    });

    Future<void> pumpRouted(WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            permissionServiceProvider.overrideWithValue(
              const GrantedPermissionService(),
            ),
            imageCaptureServiceProvider.overrideWithValue(
              FakeImageCaptureService(path: picked),
            ),
            scanRepositoryProvider.overrideWithValue(repo),
          ],
          child: MaterialApp.router(
            locale: const Locale('vi'),
            supportedLocales: AppL10n.supportedLocales,
            localizationsDelegates: AppL10n.localizationsDelegates,
            theme: AppTheme.light,
            routerConfig: router,
          ),
        ),
      );
      await _tick(tester);
    }

    final galleryButton = find.widgetWithIcon(
      IconButton,
      Icons.photo_library_outlined,
    );
    final torchButton = find.widgetWithIcon(
      IconButton,
      Icons.flash_off_rounded,
    );
    final manualTap = find.ancestor(
      of: find.text('Nhập tay'),
      matching: find.byType(GestureDetector),
    );
    final frozenImage = find.byWidgetPredicate(
      (w) =>
          w is Image &&
          w.image is FileImage &&
          (w.image as FileImage).file.path == picked,
    );

    bool chipsEnabled(WidgetTester tester) => tester
        .widgetList<ChoiceChip>(find.byType(ChoiceChip))
        .every((c) => c.onSelected != null);
    bool chipsDisabled(WidgetTester tester) => tester
        .widgetList<ChoiceChip>(find.byType(ChoiceChip))
        .every((c) => c.onSelected == null);
    bool galleryEnabled(WidgetTester tester) =>
        tester.widget<IconButton>(galleryButton).onPressed != null;
    bool manualEnabled(WidgetTester tester) =>
        tester.widget<GestureDetector>(manualTap.first).onTap != null;

    testWidgets('locks mode / torch / gallery / manual', (tester) async {
      await pumpRouted(tester);
      expect(chipsEnabled(tester), isTrue);
      expect(galleryEnabled(tester), isTrue);
      expect(manualEnabled(tester), isTrue);

      await tester.tap(galleryButton);
      await _tick(tester);

      expect(chipsDisabled(tester), isTrue);
      expect(tester.widget<IconButton>(torchButton).onPressed, isNull);
      expect(galleryEnabled(tester), isFalse);
      expect(manualEnabled(tester), isFalse);

      response.complete(Right(labelScanJob()));
      await _settleRoute(tester);
    });

    testWidgets('shows the frozen photo + reading overlay, no live preview', (
      tester,
    ) async {
      await pumpRouted(tester);
      expect(frozenImage, findsNothing);

      await tester.tap(galleryButton);
      await _tick(tester);

      expect(find.text('Đang đọc thông tin…'), findsOneWidget);
      expect(frozenImage, findsOneWidget);
      expect(find.byType(CameraPreview), findsNothing);
      // "Đã chụp ảnh" is only for camera shots, not gallery picks.
      expect(find.text('Đã chụp ảnh'), findsNothing);
      verify(() => repo.scanLabel(picked)).called(1);

      response.complete(Right(labelScanJob()));
      await _settleRoute(tester);
    });

    testWidgets('resets busy state once the scan finishes', (tester) async {
      await pumpRouted(tester);
      await tester.tap(galleryButton);
      await _tick(tester);
      expect(find.text('Đang đọc thông tin…'), findsOneWidget);

      response.complete(Right(labelScanJob()));
      await _settleRoute(tester);
      expect(find.text('label-review'), findsOneWidget);

      router.pop();
      await _settleRoute(tester);

      expect(tester.takeException(), isNull);
      expect(find.text('Đang đọc thông tin…'), findsNothing);
      expect(frozenImage, findsNothing);
      expect(chipsEnabled(tester), isTrue);
      expect(galleryEnabled(tester), isTrue);
      expect(manualEnabled(tester), isTrue);
    });
  });
}

/// Never grants; the priming sheet appears and the request comes back false.
class _DeniedPermissionService extends PermissionService {
  const _DeniedPermissionService();

  @override
  Future<bool> hasCameraPermission() async => false;
  @override
  Future<bool> requestCameraPermission() async => false;
  @override
  Future<bool> isCameraPermanentlyDenied() async => false;
}
