// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'reports_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// R-01 period selector (Tuần này / Tháng này).

@ProviderFor(ReportPeriodController)
final reportPeriodControllerProvider = ReportPeriodControllerProvider._();

/// R-01 period selector (Tuần này / Tháng này).
final class ReportPeriodControllerProvider
    extends $NotifierProvider<ReportPeriodController, ReportPeriod> {
  /// R-01 period selector (Tuần này / Tháng này).
  ReportPeriodControllerProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'reportPeriodControllerProvider',
          isAutoDispose: true,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$reportPeriodControllerHash();

  @$internal
  @override
  ReportPeriodController create() => ReportPeriodController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ReportPeriod value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ReportPeriod>(value),
    );
  }
}

String _$reportPeriodControllerHash() =>
    r'a91285aec3566d14a940716a9f574ce59d36bfbe';

/// R-01 period selector (Tuần này / Tháng này).

abstract class _$ReportPeriodController extends $Notifier<ReportPeriod> {
  ReportPeriod build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<ReportPeriod, ReportPeriod>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<ReportPeriod, ReportPeriod>,
        ReportPeriod,
        Object?,
        Object?>;
    element.handleCreate(ref, build);
  }
}

/// R-01 "Chống lãng phí" metrics for the selected period.

@ProviderFor(ReportsController)
final reportsControllerProvider = ReportsControllerProvider._();

/// R-01 "Chống lãng phí" metrics for the selected period.
final class ReportsControllerProvider
    extends $AsyncNotifierProvider<ReportsController, WasteReductionSummary> {
  /// R-01 "Chống lãng phí" metrics for the selected period.
  ReportsControllerProvider._()
      : super(
          from: null,
          argument: null,
          retry: null,
          name: r'reportsControllerProvider',
          isAutoDispose: true,
          dependencies: null,
          $allTransitiveDependencies: null,
        );

  @override
  String debugGetCreateSourceHash() => _$reportsControllerHash();

  @$internal
  @override
  ReportsController create() => ReportsController();
}

String _$reportsControllerHash() => r'fe3a42db5b2626effd875e97d2fe3747c4a559fd';

/// R-01 "Chống lãng phí" metrics for the selected period.

abstract class _$ReportsController
    extends $AsyncNotifier<WasteReductionSummary> {
  FutureOr<WasteReductionSummary> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref
        as $Ref<AsyncValue<WasteReductionSummary>, WasteReductionSummary>;
    final element = ref.element as $ClassProviderElement<
        AnyNotifier<AsyncValue<WasteReductionSummary>, WasteReductionSummary>,
        AsyncValue<WasteReductionSummary>,
        Object?,
        Object?>;
    element.handleCreate(ref, build);
  }
}
