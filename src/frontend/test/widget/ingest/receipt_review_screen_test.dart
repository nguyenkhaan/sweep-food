import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/features/ingest/presentation/screens/receipt_review_screen.dart';

void main() {
  testWidgets('ReceiptReviewScreen renders parsed items list and selection actions', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1000, 2400));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.light,
          home: const ReceiptReviewScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Hóa đơn — 6 mục'), findsOneWidget);
    expect(find.text('Bách Hóa Xanh · 05/09'), findsOneWidget);
    expect(find.text('Cà chua bi'), findsOneWidget);
    expect(find.text('Trứng gà'), findsOneWidget);
    expect(find.text('Thịt ba chỉ'), findsOneWidget);
    expect(find.text('Thêm 6 mục vào kho'), findsOneWidget);

    // Tap "Bỏ chọn tất cả"
    await tester.tap(find.text('Bỏ chọn tất cả'));
    await tester.pumpAndSettle();

    expect(find.text('Chọn ít nhất 1 mục'), findsOneWidget);
  });
}
