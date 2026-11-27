import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:sweepfood/app/theme/app_icons.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/auth/presentation/widgets/welcome_hang_tag_stack.dart';

void main() {
  const front = HangTagCardData(
    tagLabel: 'NHẮC SỚM',
    metric: '3 giây',
    icon: AppIcons.scan,
    title: 'Quét tem cân và hóa đơn',
    subtitle: 'Tự nhận diện tên món và hạn sử dụng',
  );

  const back = HangTagCardData(
    tagLabel: 'TỦ BẾP CỦA BẠN',
    metric: 'Còn 2 ngày',
    metricIcon: AppIcons.clock,
    icon: AppIcons.pantry,
    title: 'Cà chua bi · Sữa tươi',
    subtitle: 'Đẩy nguyên liệu sắp hết hạn lên đầu',
  );

  Widget buildSubject({double height = 340}) {
    return MaterialApp(
      theme: AppTheme.light,
      home: Scaffold(
        body: Center(
          child: SizedBox(
            width: 384,
            height: height,
            child: const WelcomeHangTagStack(frontData: front, backData: back),
          ),
        ),
      ),
    );
  }

  testWidgets('renders both hang-tag cards and swaps on back card tap', (
    tester,
  ) async {
    await tester.pumpWidget(buildSubject());
    await tester.pumpAndSettle();

    expect(find.text('NHẮC SỚM'), findsOneWidget);
    expect(find.text('TỦ BẾP CỦA BẠN'), findsOneWidget);

    // Before swap: back tag sits above front tag.
    final initialBackY = tester.getTopLeft(find.text('TỦ BẾP CỦA BẠN')).dy;
    final initialFrontY = tester.getTopLeft(find.text('NHẮC SỚM')).dy;
    expect(initialBackY, lessThan(initialFrontY));

    // Tap the peeking back tag to swap it to the front slot.
    await tester.tap(find.text('TỦ BẾP CỦA BẠN'));
    await tester.pumpAndSettle();

    final swappedEmeraldY = tester.getTopLeft(find.text('TỦ BẾP CỦA BẠN')).dy;
    final swappedLightY = tester.getTopLeft(find.text('NHẮC SỚM')).dy;
    expect(swappedEmeraldY, greaterThan(swappedLightY));
  });

  testWidgets('handles vertical pull and front tap swing without overflow', (
    tester,
  ) async {
    await tester.pumpWidget(buildSubject(height: 260));
    await tester.pumpAndSettle();

    // Tap front tag to trigger pendulum swing.
    await tester.tap(find.text('Quét tem cân và hóa đơn'));
    await tester.pump(const Duration(milliseconds: 120));
    await tester.pumpAndSettle();

    // Pull front tag vertically downward and release.
    await tester.drag(find.text('Quét tem cân và hóa đơn'), const Offset(0, 30));
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
  });
}
