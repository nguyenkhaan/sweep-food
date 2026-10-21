import 'package:flutter/material.dart';
import 'package:sweepfood/app/theme/app_spacing.dart';
import 'package:sweepfood/core/utils/extensions/build_context_x.dart';
import 'package:sweepfood/features/pantry/data/models/freshness_dto.dart';
import 'package:sweepfood/features/pantry/domain/entities/freshness_answer_set.dart';

/// Radio value of the free-text option; never collides with a backend option.
const _otherValue = '__other__';

/// Longest "Khác" description the backend accepts.
const freshnessOtherMaxLength = 500;

/// The FreshCheck sensory questions as a Google-Form-style survey: one card per
/// question with a prominent numbered title, radio options that wrap onto
/// further lines when the text is long, and a final "Khác" option that opens a
/// text box for the user's own description. [axisErrors] are shown directly
/// under the box of the axis they belong to.
class FreshnessQuestionsForm extends StatefulWidget {
  const FreshnessQuestionsForm({
    required this.questions,
    required this.answers,
    required this.onChanged,
    this.axisErrors = const {},
    this.enabled = true,
    super.key,
  });

  final List<FreshnessQuestionDto> questions;
  final FreshnessAnswerSet answers;
  final ValueChanged<FreshnessAnswerSet> onChanged;

  /// axis -> message shown under that axis' "Khác" box.
  final Map<String, String> axisErrors;
  final bool enabled;

  @override
  State<FreshnessQuestionsForm> createState() => _FreshnessQuestionsFormState();
}

class _FreshnessQuestionsFormState extends State<FreshnessQuestionsForm> {
  final Map<String, TextEditingController> _texts = {};

  TextEditingController _textFor(String axis) => _texts.putIfAbsent(
    axis,
    () => TextEditingController(text: widget.answers.other[axis] ?? ''),
  );

  @override
  void dispose() {
    for (final c in _texts.values) {
      c.dispose();
    }
    super.dispose();
  }

  void _onRadio(String axis, String? value) {
    if (value == null) return;
    final answers = widget.answers;
    widget.onChanged(
      value == _otherValue
          // Keep what was typed earlier if the user toggles back to "Khác".
          ? answers.chooseOther(axis).describe(axis, _textFor(axis).text)
          : answers.choose(axis, value),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (var i = 0; i < widget.questions.length; i++) ...[
          _QuestionCard(
            index: i + 1,
            question: widget.questions[i],
            groupValue: widget.answers.usesOther(widget.questions[i].axis)
                ? _otherValue
                : widget.answers.selected[widget.questions[i].axis],
            textController: _textFor(widget.questions[i].axis),
            errorText: widget.axisErrors[widget.questions[i].axis],
            enabled: widget.enabled,
            onRadio: (v) => _onRadio(widget.questions[i].axis, v),
            onText: (t) => widget.onChanged(
              widget.answers.describe(widget.questions[i].axis, t),
            ),
          ),
          if (i < widget.questions.length - 1) Gap.gapSm,
        ],
      ],
    );
  }
}

class _QuestionCard extends StatelessWidget {
  const _QuestionCard({
    required this.index,
    required this.question,
    required this.groupValue,
    required this.textController,
    required this.errorText,
    required this.enabled,
    required this.onRadio,
    required this.onText,
  });

  final int index;
  final FreshnessQuestionDto question;
  final String? groupValue;
  final TextEditingController textController;
  final String? errorText;
  final bool enabled;
  final ValueChanged<String?> onRadio;
  final ValueChanged<String> onText;

  @override
  Widget build(BuildContext context) {
    final scheme = context.colors;
    final hasError = errorText != null;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(Gap.md, Gap.md, Gap.md, Gap.xs),
      decoration: BoxDecoration(
        color: scheme.surface,
        borderRadius: Radii.brMd,
        border: Border.all(
          color: hasError ? scheme.error : context.sweep.hairline,
          width: hasError ? 1.5 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 28,
                height: 28,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: scheme.primaryContainer,
                  shape: BoxShape.circle,
                ),
                child: Text(
                  '$index',
                  style: context.text.labelLarge?.copyWith(
                    color: scheme.onPrimaryContainer,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              const SizedBox(width: Gap.sm),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.only(top: 3),
                  child: Text(
                    question.questionVi,
                    style: context.text.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      height: 1.3,
                    ),
                  ),
                ),
              ),
            ],
          ),
          Gap.gapXs,
          // ListTile paints its ink on the nearest Material; the card's coloured
          // DecoratedBox would hide it, so give the tiles their own.
          Material(
            type: MaterialType.transparency,
            child: RadioGroup<String>(
              groupValue: groupValue,
              onChanged: onRadio,
              child: Column(
                children: [
                  for (final option in question.options)
                    RadioListTile<String>(
                      value: option.value,
                      enabled: enabled,
                      contentPadding: EdgeInsets.zero,
                      controlAffinity: ListTileControlAffinity.leading,
                      visualDensity: VisualDensity.compact,
                      title: Text(
                        option.labelVi,
                        style: context.text.bodyMedium,
                      ),
                    ),
                  RadioListTile<String>(
                    value: _otherValue,
                    enabled: enabled,
                    contentPadding: EdgeInsets.zero,
                    controlAffinity: ListTileControlAffinity.leading,
                    visualDensity: VisualDensity.compact,
                    title: Text('Khác', style: context.text.bodyMedium),
                  ),
                ],
              ),
            ),
          ),
          if (groupValue == _otherValue)
            Padding(
              padding: const EdgeInsets.only(bottom: Gap.sm),
              child: TextField(
                controller: textController,
                enabled: enabled,
                minLines: 2,
                maxLines: 4,
                maxLength: freshnessOtherMaxLength,
                textCapitalization: TextCapitalization.sentences,
                keyboardType: TextInputType.multiline,
                onChanged: onText,
                decoration: InputDecoration(
                  hintText: 'Mô tả những gì bạn quan sát được…',
                  errorText: errorText,
                  errorMaxLines: 3,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
