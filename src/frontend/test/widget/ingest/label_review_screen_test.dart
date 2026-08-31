import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/features/ingest/presentation/screens/label_review_screen.dart';

void main() {
  testWidgets('LabelReviewScreen renders OCR parsed fields and warning badges', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1000, 2400));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.light,
          home: const LabelReviewScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Kiểm tra thông tin'), findsOneWidget);
    expect(find.text('Cà chua bi'), findsOneWidget);
    expect(find.text('500 g'), findsOneWidget);
    expect(find.text('18.000đ'), findsOneWidget);
    expect(find.text('Cần kiểm tra'), findsOneWidget);
    expect(find.text('Tầng bảo quản'), findsOneWidget);
    expect(find.text('Thêm vào kho'), findsOneWidget);
  });
}
