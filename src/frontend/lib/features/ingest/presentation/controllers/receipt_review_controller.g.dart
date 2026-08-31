// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'receipt_review_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Seeds from the receipt OCR [ScanJob]; every line is selected by default.

@ProviderFor(ReceiptReviewController)
final receiptReviewControllerProvider = ReceiptReviewControllerFamily._();

/// Seeds from the receipt OCR [ScanJob]; every line is selected by default.
final class ReceiptReviewControllerProvider
    extends $NotifierProvider<ReceiptReviewController, ReceiptReviewState> {
  /// Seeds from the receipt OCR [ScanJob]; every line is selected by default.
  ReceiptReviewControllerProvider._({
    required ReceiptReviewControllerFamily super.from,
    required ScanJob super.argument,
  }) : super(
         retry: null,
         name: r'receiptReviewControllerProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$receiptReviewControllerHash();

  @override
  String toString() {
    return r'receiptReviewControllerProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  ReceiptReviewController create() => ReceiptReviewController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ReceiptReviewState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ReceiptReviewState>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is ReceiptReviewControllerProvider &&
        other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$receiptReviewControllerHash() =>
    r'342041d6f34bdb603c91596b2f742247f9a8f4ed';

/// Seeds from the receipt OCR [ScanJob]; every line is selected by default.

final class ReceiptReviewControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          ReceiptReviewController,
          ReceiptReviewState,
          ReceiptReviewState,
          ReceiptReviewState,
          ScanJob
        > {
  ReceiptReviewControllerFamily._()
    : super(
        retry: null,
        name: r'receiptReviewControllerProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Seeds from the receipt OCR [ScanJob]; every line is selected by default.

  ReceiptReviewControllerProvider call(ScanJob job) =>
      ReceiptReviewControllerProvider._(argument: job, from: this);

  @override
  String toString() => r'receiptReviewControllerProvider';
}

/// Seeds from the receipt OCR [ScanJob]; every line is selected by default.

abstract class _$ReceiptReviewController extends $Notifier<ReceiptReviewState> {
  late final _$args = ref.$arg as ScanJob;
  ScanJob get job => _$args;

  ReceiptReviewState build(ScanJob job);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<ReceiptReviewState, ReceiptReviewState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<ReceiptReviewState, ReceiptReviewState>,
              ReceiptReviewState,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
