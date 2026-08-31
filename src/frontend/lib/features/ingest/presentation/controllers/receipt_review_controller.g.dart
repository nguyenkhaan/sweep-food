// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'receipt_review_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(ReceiptReviewController)
final receiptReviewControllerProvider = ReceiptReviewControllerFamily._();

final class ReceiptReviewControllerProvider
    extends $NotifierProvider<ReceiptReviewController, ReceiptReviewState> {
  ReceiptReviewControllerProvider._(
      {required ReceiptReviewControllerFamily super.from,
      required String? super.argument})
      : super(
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
    r'02ff5238489079d7c6b06e138fcdd60f2e2e762a';

final class ReceiptReviewControllerFamily extends $Family
    with
        $ClassFamilyOverride<ReceiptReviewController, ReceiptReviewState,
            ReceiptReviewState, ReceiptReviewState, String?> {
  ReceiptReviewControllerFamily._()
      : super(
          retry: null,
          name: r'receiptReviewControllerProvider',
          dependencies: null,
          $allTransitiveDependencies: null,
          isAutoDispose: true,
        );

  ReceiptReviewControllerProvider call({
    String? imagePath,
  }) =>
      ReceiptReviewControllerProvider._(argument: imagePath, from: this);

  @override
  String toString() => r'receiptReviewControllerProvider';
}

abstract class _$ReceiptReviewController extends $Notifier<ReceiptReviewState> {
  late final _$args = ref.$arg as String?;
  String? get imagePath => _$args;

  ReceiptReviewState build({
    String? imagePath,
  });
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<ReceiptReviewState, ReceiptReviewState>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<ReceiptReviewState, ReceiptReviewState>,
        ReceiptReviewState,
        Object?,
        Object?>;
    element.handleCreate(
        ref,
        () => build(
              imagePath: _$args,
            ));
  }
}
