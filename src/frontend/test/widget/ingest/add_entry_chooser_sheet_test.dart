import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/app/theme/app_theme.dart';
import 'package:frontend/features/ingest/presentation/screens/add_entry_chooser_sheet.dart';

void main() {
  testWidgets('AddEntryChooserSheet renders 4 input methods in 2x2 grid', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.light,
          home: const Scaffold(
            body: AddEntryChooserSheet(),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Thêm nguyên liệu'), findsOneWidget);
    expect(find.text('Quét tem nhãn'), findsOneWidget);
    expect(find.text('Quét hóa đơn'), findsOneWidget);
    expect(find.text('Nói'), findsOneWidget);
    expect(find.text('Nhập tay'), findsOneWidget);
  });

  testWidgets('lays out without overflow on a narrow phone + large text', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(320, 640);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.light,
          home: const MediaQuery(
            data: MediaQueryData(textScaler: TextScaler.linear(1.3)),
            child: Scaffold(body: AddEntryChooserSheet()),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.text('Quét tem nhãn'), findsOneWidget);
    expect(find.text('Nhập tay'), findsOneWidget);
  });

  testWidgets('showAddEntryChooser opens bottom sheet', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.light,
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => showAddEntryChooser(context),
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      ),
    );

    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();

    expect(find.byType(AddEntryChooserSheet), findsOneWidget);
    expect(find.text('Thêm nguyên liệu'), findsOneWidget);
  });
}
