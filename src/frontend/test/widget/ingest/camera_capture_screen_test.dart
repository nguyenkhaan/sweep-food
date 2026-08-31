import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart' show Override;
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/core/media/media_providers.dart';
import 'package:frontend/core/permissions/permission_service.dart';
import 'package:frontend/features/ingest/presentation/screens/camera_capture_screen.dart';

import '../../helpers/media_fakes.dart';

Widget _screen(List<Override> overrides) => ProviderScope(
      overrides: [
        imageCaptureServiceProvider
            .overrideWithValue(FakeImageCaptureService(path: null)),
        ...overrides,
      ],
      child: MaterialApp(
        theme: AppTheme.light,
        home: const CameraCaptureScreen(),
      ),
    );

Future<void> _tick(WidgetTester tester) async {
  await tester.pump();
  await tester.pump(const Duration(milliseconds: 50));
  await tester.pump(const Duration(milliseconds: 50));
}

void main() {
  testWidgets('mounts with the scan chrome and no crash', (tester) async {
    await tester.pumpWidget(
      _screen([
        permissionServiceProvider
            .overrideWithValue(const GrantedPermissionService()),
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
        permissionServiceProvider
            .overrideWithValue(const _DeniedPermissionService()),
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
