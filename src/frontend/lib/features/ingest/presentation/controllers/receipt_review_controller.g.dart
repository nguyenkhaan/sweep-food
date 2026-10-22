// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'receipt_review_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Seeds from the receipt OCR [ScanJob]. Every supported line is ticked by
/// default; a food the smart parser cannot recognize starts (and is kept)
/// unticked, though the user may still tick it — which blocks adding.

@ProviderFor(ReceiptReviewController)
final receiptReviewControllerProvider = ReceiptReviewControllerFamily._();

/// Seeds from the receipt OCR [ScanJob]. Every supported line is ticked by
/// default; a food the smart parser cannot recognize starts (and is kept)
/// unticked, though the user may still tick it — which blocks adding.
final class ReceiptReviewControllerProvider
    extends $NotifierProvider<ReceiptReviewController, ReceiptReviewState> {
  /// Seeds from the receipt OCR [ScanJob]. Every supported line is ticked by
  /// default; a food the smart parser cannot recognize starts (and is kept)
  /// unticked, though the user may still tick it — which blocks adding.
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
    r'd2d7121d146d97426117a96210fe2c30fd6687e2';

/// Seeds from the receipt OCR [ScanJob]. Every supported line is ticked by
/// default; a food the smart parser cannot recognize starts (and is kept)
/// unticked, though the user may still tick it — which blocks adding.

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

  /// Seeds from the receipt OCR [ScanJob]. Every supported line is ticked by
  /// default; a food the smart parser cannot recognize starts (and is kept)
  /// unticked, though the user may still tick it — which blocks adding.

  ReceiptReviewControllerProvider call(ScanJob job) =>
      ReceiptReviewControllerProvider._(argument: job, from: this);

  @override
  String toString() => r'receiptReviewControllerProvider';
}

/// Seeds from the receipt OCR [ScanJob]. Every supported line is ticked by
/// default; a food the smart parser cannot recognize starts (and is kept)
/// unticked, though the user may still tick it — which blocks adding.

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
