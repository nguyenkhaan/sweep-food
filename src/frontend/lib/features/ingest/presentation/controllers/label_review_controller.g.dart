// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'label_review_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Holds the single editable draft on the Label Review screen (I-03), seeded
/// from the OCR [ScanJob].

@ProviderFor(LabelReviewController)
final labelReviewControllerProvider = LabelReviewControllerFamily._();

/// Holds the single editable draft on the Label Review screen (I-03), seeded
/// from the OCR [ScanJob].
final class LabelReviewControllerProvider
    extends $NotifierProvider<LabelReviewController, ParsedItemDraft> {
  /// Holds the single editable draft on the Label Review screen (I-03), seeded
  /// from the OCR [ScanJob].
  LabelReviewControllerProvider._({
    required LabelReviewControllerFamily super.from,
    required ScanJob super.argument,
  }) : super(
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
    r'a8708b1088a43901fe290bc738adb4c242141b7b';

/// Holds the single editable draft on the Label Review screen (I-03), seeded
/// from the OCR [ScanJob].

final class LabelReviewControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          LabelReviewController,
          ParsedItemDraft,
          ParsedItemDraft,
          ParsedItemDraft,
          ScanJob
        > {
  LabelReviewControllerFamily._()
    : super(
        retry: null,
        name: r'labelReviewControllerProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Holds the single editable draft on the Label Review screen (I-03), seeded
  /// from the OCR [ScanJob].

  LabelReviewControllerProvider call(ScanJob job) =>
      LabelReviewControllerProvider._(argument: job, from: this);

  @override
  String toString() => r'labelReviewControllerProvider';
}

/// Holds the single editable draft on the Label Review screen (I-03), seeded
/// from the OCR [ScanJob].

abstract class _$LabelReviewController extends $Notifier<ParsedItemDraft> {
  late final _$args = ref.$arg as ScanJob;
  ScanJob get job => _$args;

  ParsedItemDraft build(ScanJob job);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<ParsedItemDraft, ParsedItemDraft>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<ParsedItemDraft, ParsedItemDraft>,
              ParsedItemDraft,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
