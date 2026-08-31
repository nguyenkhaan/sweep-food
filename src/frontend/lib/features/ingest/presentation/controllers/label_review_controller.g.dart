// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'label_review_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Controller managing the state of the Label Review screen (I-03).

@ProviderFor(LabelReviewController)
final labelReviewControllerProvider = LabelReviewControllerFamily._();

/// Controller managing the state of the Label Review screen (I-03).
final class LabelReviewControllerProvider
    extends $NotifierProvider<LabelReviewController, ParsedItemDraft> {
  /// Controller managing the state of the Label Review screen (I-03).
  LabelReviewControllerProvider._(
      {required LabelReviewControllerFamily super.from,
      required String? super.argument})
      : super(
          retry: null,
          name: r'labelReviewControllerProvider',
          isAutoDispose: true,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$labelReviewControllerHash();

  @override
  String toString() {
    return r'labelReviewControllerProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  LabelReviewController create() => LabelReviewController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ParsedItemDraft value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ParsedItemDraft>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is LabelReviewControllerProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$labelReviewControllerHash() =>
    r'e8e6a66abaca054d3d364ed9ba689ed292f2d844';

/// Controller managing the state of the Label Review screen (I-03).

final class LabelReviewControllerFamily extends $Family
    with
        $ClassFamilyOverride<LabelReviewController, ParsedItemDraft,
            ParsedItemDraft, ParsedItemDraft, String?> {
  LabelReviewControllerFamily._()
      : super(
          retry: null,
          name: r'labelReviewControllerProvider',
          dependencies: null,
          $allTransitiveDependencies: null,
          isAutoDispose: true,
        );

  /// Controller managing the state of the Label Review screen (I-03).

  LabelReviewControllerProvider call({
    String? imagePath,
  }) =>
      LabelReviewControllerProvider._(argument: imagePath, from: this);

  @override
  String toString() => r'labelReviewControllerProvider';
}

/// Controller managing the state of the Label Review screen (I-03).

abstract class _$LabelReviewController extends $Notifier<ParsedItemDraft> {
  late final _$args = ref.$arg as String?;
  String? get imagePath => _$args;

  ParsedItemDraft build({
    String? imagePath,
  });
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<ParsedItemDraft, ParsedItemDraft>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<ParsedItemDraft, ParsedItemDraft>,
        ParsedItemDraft,
        Object?,
        Object?>;
    element.handleCreate(
        ref,
        () => build(
              imagePath: _$args,
            ));
  }
}
