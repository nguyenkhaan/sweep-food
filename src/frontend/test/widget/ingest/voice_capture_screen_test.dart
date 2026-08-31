import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/core/media/media_providers.dart';
import 'package:sweepfood/core/permissions/permission_service.dart';
import 'package:sweepfood/features/ingest/presentation/screens/voice_capture_screen.dart';
import 'package:sweepfood/l10n/app_localizations.dart';

import '../../helpers/media_fakes.dart';

void main() {
  testWidgets('VoiceCaptureScreen primes the mic then shows the listening UI', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          permissionServiceProvider.overrideWithValue(
            const GrantedPermissionService(),
          ),
          audioRecorderServiceProvider.overrideWithValue(
            FakeAudioRecorderService(),
          ),
        ],
        child: MaterialApp(
          locale: const Locale('vi'),
          supportedLocales: AppL10n.supportedLocales,
          localizationsDelegates: AppL10n.localizationsDelegates,
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
