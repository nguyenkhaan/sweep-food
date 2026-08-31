import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/features/ingest/presentation/screens/voice_capture_screen.dart';

void main() {
  testWidgets('VoiceCaptureScreen renders hint, timer, waveform and stop button', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.light,
          home: const VoiceCaptureScreen(),
        ),
      ),
    );
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('Nói để thêm'), findsOneWidget);
    expect(find.text('Đọc tên nguyên liệu và số lượng'), findsOneWidget);
    expect(find.text('Đang nghe…'), findsOneWidget);
    expect(find.text('Dừng & Kiểm tra'), findsOneWidget);
  });
}
