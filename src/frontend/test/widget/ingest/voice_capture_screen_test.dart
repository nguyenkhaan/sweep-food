import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/core/media/media_providers.dart';
import 'package:frontend/core/permissions/permission_service.dart';
import 'package:frontend/features/ingest/presentation/screens/voice_capture_screen.dart';

import '../../helpers/media_fakes.dart';

void main() {
  testWidgets('VoiceCaptureScreen primes the mic then shows the listening UI', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          permissionServiceProvider
              .overrideWithValue(const GrantedPermissionService()),
          audioRecorderServiceProvider
              .overrideWithValue(FakeAudioRecorderService()),
        ],
        child: MaterialApp(
          theme: AppTheme.light,
          home: const VoiceCaptureScreen(),
        ),
      ),
    );
    await tester.pump(); // run the post-frame _begin()
    await tester.pump(const Duration(milliseconds: 50));

    expect(find.text('Nói để thêm'), findsOneWidget);
    expect(find.text('Đọc tên nguyên liệu và số lượng'), findsOneWidget);
    expect(find.text('Đang nghe…'), findsOneWidget);
    expect(find.text('Dừng & Kiểm tra'), findsOneWidget);
  });
}
