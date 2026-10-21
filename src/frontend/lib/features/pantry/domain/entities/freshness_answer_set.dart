import 'package:flutter/foundation.dart';

/// What the user answered in the FreshCheck form, per rubric axis.
///
/// An axis is answered either with one of the backend's predefined options
/// ([selected]) or with the free-text "Khác" ([other]) — never both. An [other]
/// entry whose text is still empty means "Khác" is chosen but not described yet.
@immutable
class FreshnessAnswerSet {
  const FreshnessAnswerSet({
    this.selected = const {},
    this.other = const {},
  });

  /// axis -> predefined option value.
  final Map<String, String> selected;

  /// axis -> free-text description (key present = "Khác" chosen).
  final Map<String, String> other;

  bool usesOther(String axis) => other.containsKey(axis);

  /// Picks a predefined option, dropping any "Khác" text for that axis.
  FreshnessAnswerSet choose(String axis, String value) => FreshnessAnswerSet(
    selected: {...selected, axis: value},
    other: {...other}..remove(axis),
  );

  /// Picks "Khác" for [axis], keeping text typed earlier.
  FreshnessAnswerSet chooseOther(String axis) => FreshnessAnswerSet(
    selected: {...selected}..remove(axis),
    other: {...other, axis: other[axis] ?? ''},
  );

  /// Updates the "Khác" text of [axis] (which must already be chosen).
  FreshnessAnswerSet describe(String axis, String text) =>
      FreshnessAnswerSet(selected: selected, other: {...other, axis: text});

  /// Axes where "Khác" is chosen but nothing was written.
  List<String> get emptyOtherAxes => [
    for (final e in other.entries)
      if (e.value.trim().isEmpty) e.key,
  ];

  /// Axes whose answer (option or "Khác" text) differs from [before].
  Set<String> changedAxesFrom(FreshnessAnswerSet before) => {
    for (final axis in {
      ...selected.keys,
      ...other.keys,
      ...before.selected.keys,
      ...before.other.keys,
    })
      if (selected[axis] != before.selected[axis] ||
          other[axis] != before.other[axis])
        axis,
  };

  /// Free-text answers in the shape the backend accepts (`other_answers`).
  Map<String, String> get otherToSend => {
    for (final e in other.entries)
      if (e.value.trim().isNotEmpty) e.key: e.value.trim(),
  };
}
