import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/features/ingest/presentation/screens/voice_review_screen.dart';

void main() {
  testWidgets('VoiceReviewScreen renders transcript and parsed items list', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1000, 2400));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.light,
          home: const VoiceReviewScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Kiểm tra kết quả'), findsOneWidget);
    expect(find.textContaining('2 lạng thịt bò'), findsOneWidget);
    expect(find.text('Nghe lại'), findsOneWidget);
    expect(find.text('Ghi lại'), findsOneWidget);
    expect(find.text('Thịt bò'), findsOneWidget);
    expect(find.text('Cải bó xôi'), findsOneWidget);
    expect(find.text('Trứng gà'), findsOneWidget);
    expect(find.text('Thêm dòng'), findsOneWidget);
    expect(find.text('Thêm 3 nguyên liệu'), findsOneWidget);
  });
}
