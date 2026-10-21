import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sweepfood/app/theme/app_theme.dart';
import 'package:sweepfood/features/pantry/data/models/freshness_dto.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_answer_set.dart';
import 'package:sweepfood/features/pantry/presentation/widgets/freshness_questions_form.dart';

const _longLabel =
    'Thịt có màu hồng nhạt, hơi xỉn ở rìa miếng và có vài chỗ sẫm màu '
    'hơn bình thường khi để lâu trong ngăn mát';

const _questions = [
  FreshnessQuestionDto(
    axis: 'color',
    questionVi: 'Màu sắc phần nạc và mỡ?',
    defaultValue: 'red',
    options: [
      FreshnessQuestionOptionDto(value: 'red', labelVi: 'Đỏ tươi'),
      FreshnessQuestionOptionDto(value: 'pale', labelVi: _longLabel),
    ],
  ),
  FreshnessQuestionDto(
    axis: 'smell',
    questionVi: 'Ngửi gần miếng thịt?',
    defaultValue: 'fresh',
    options: [
      FreshnessQuestionOptionDto(value: 'fresh', labelVi: 'Thơm tươi'),
    ],
  ),
];

/// Hosts the form with its answers held in state, like the real sheets do.
Future<ValueNotifier<FreshnessAnswerSet>> _pump(
  WidgetTester tester, {
  Map<String, String> axisErrors = const {},
  double width = 320,
}) async {
  final answers = ValueNotifier(
    const FreshnessAnswerSet(selected: {'color': 'red', 'smell': 'fresh'}),
  );
  await tester.pumpWidget(
    MaterialApp(
      theme: AppTheme.light,
      home: Scaffold(
        body: Center(
          child: SizedBox(
            width: width,
            child: ValueListenableBuilder<FreshnessAnswerSet>(
              valueListenable: answers,
              builder: (_, value, _) => SingleChildScrollView(
                child: FreshnessQuestionsForm(
                  questions: _questions,
                  answers: value,
                  axisErrors: axisErrors,
                  onChanged: (next) => answers.value = next,
                ),
              ),
            ),
          ),
        ),
      ),
    ),
  );
  return answers;
}

void main() {
  testWidgets('each question is a numbered card with radio options and "Khác"', (
    tester,
  ) async {
    await _pump(tester);

    expect(find.text('Màu sắc phần nạc và mỡ?'), findsOneWidget);
    expect(find.text('Ngửi gần miếng thịt?'), findsOneWidget);
    expect(find.text('1'), findsOneWidget);
    expect(find.text('2'), findsOneWidget);
    // Two predefined options + "Khác" for the first question, one + "Khác" for
    // the second: radios, not chips.
    expect(find.byType(RadioListTile<String>), findsNWidgets(5));
    expect(find.byType(ChoiceChip), findsNothing);
    expect(find.text('Khác'), findsNWidgets(2));
  });

  testWidgets('a long option wraps onto several lines instead of overflowing', (
    tester,
  ) async {
    await _pump(tester, width: 260);

    expect(tester.takeException(), isNull);
    final label = tester.getSize(find.text(_longLabel));
    final single = tester.getSize(find.text('Đỏ tươi'));
    expect(label.height, greaterThan(single.height * 2));
    expect(label.width, lessThanOrEqualTo(260));
  });

  testWidgets('choosing an option updates the answer and keeps "Khác" closed', (
    tester,
  ) async {
    final answers = await _pump(tester);

    await tester.tap(find.text(_longLabel));
    await tester.pump();

    expect(answers.value.selected['color'], 'pale');
    expect(answers.value.usesOther('color'), isFalse);
    expect(find.byType(TextField), findsNothing);
  });

  testWidgets('"Khác" opens a text box whose text is the axis answer', (
    tester,
  ) async {
    final answers = await _pump(tester);

    await tester.tap(find.text('Khác').first);
    await tester.pump();

    expect(find.byType(TextField), findsOneWidget);
    expect(answers.value.usesOther('color'), isTrue);
    expect(answers.value.selected.containsKey('color'), isFalse);
    expect(answers.value.selected['smell'], 'fresh'); // other axis untouched

    await tester.enterText(find.byType(TextField), '  Màu hồng, hơi nhạt  ');
    await tester.pump();

    expect(answers.value.other['color'], '  Màu hồng, hơi nhạt  ');
    expect(answers.value.otherToSend, {'color': 'Màu hồng, hơi nhạt'});
  });

  testWidgets('what was typed survives switching to an option and back', (
    tester,
  ) async {
    final answers = await _pump(tester);
    await tester.tap(find.text('Khác').first);
    await tester.pump();
    await tester.enterText(find.byType(TextField), 'hồng nhạt');
    await tester.pump();

    await tester.tap(find.text('Đỏ tươi'));
    await tester.pump();
    expect(answers.value.usesOther('color'), isFalse);

    await tester.tap(find.text('Khác').first);
    await tester.pump();
    expect(answers.value.other['color'], 'hồng nhạt');
    expect(find.text('hồng nhạt'), findsOneWidget);
  });

  testWidgets('an axis error is shown directly under that axis\' box', (
    tester,
  ) async {
    await _pump(
      tester,
      axisErrors: const {'color': 'vui lòng trả lời liên quan tới câu hỏi'},
    );
    await tester.tap(find.text('Khác').first);
    await tester.pump();

    final error = find.text('vui lòng trả lời liên quan tới câu hỏi');
    expect(error, findsOneWidget);
    expect(
      tester.getTopLeft(error).dy,
      greaterThan(tester.getBottomLeft(find.byType(EditableText)).dy),
    );
  });
}
