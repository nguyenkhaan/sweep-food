// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'home_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Controller providing aggregated data for the H-01 Home Dashboard.

@ProviderFor(homeDashboard)
final homeDashboardProvider = HomeDashboardProvider._();

/// Controller providing aggregated data for the H-01 Home Dashboard.

final class HomeDashboardProvider
    extends
        $FunctionalProvider<
          AsyncValue<HomeDashboardData>,
          HomeDashboardData,
          FutureOr<HomeDashboardData>
        >
    with
        $FutureModifier<HomeDashboardData>,
        $FutureProvider<HomeDashboardData> {
  /// Controller providing aggregated data for the H-01 Home Dashboard.
  HomeDashboardProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'homeDashboardProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$homeDashboardHash();

  @$internal
  @override
  $FutureProviderElement<HomeDashboardData> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<HomeDashboardData> create(Ref ref) {
    return homeDashboard(ref);
  }
}

String _$homeDashboardHash() => r'f1006482d35a7efc4b75c8d1549b8b1aa7390a4a';
