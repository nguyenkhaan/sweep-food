// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'suggestion_list_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(SuggestionFilterController)
final suggestionFilterControllerProvider =
    SuggestionFilterControllerProvider._();

final class SuggestionFilterControllerProvider
    extends $NotifierProvider<SuggestionFilterController, SuggestionFilter> {
  SuggestionFilterControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'suggestionFilterControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$suggestionFilterControllerHash();

  @$internal
  @override
  SuggestionFilterController create() => SuggestionFilterController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(SuggestionFilter value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<SuggestionFilter>(value),
    );
  }
}

String _$suggestionFilterControllerHash() =>
    r'700f5e2a980ef93972cd94515527d281ab8d3d19';

abstract class _$SuggestionFilterController
    extends $Notifier<SuggestionFilter> {
  SuggestionFilter build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<SuggestionFilter, SuggestionFilter>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<SuggestionFilter, SuggestionFilter>,
              SuggestionFilter,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// S-01 list. Re-fetches whenever the filter changes; the server does the
/// `0.4E + 0.3A + 0.2P + 0.1U` scoring.

@ProviderFor(SuggestionListController)
final suggestionListControllerProvider = SuggestionListControllerProvider._();

/// S-01 list. Re-fetches whenever the filter changes; the server does the
/// `0.4E + 0.3A + 0.2P + 0.1U` scoring.
final class SuggestionListControllerProvider
    extends
        $AsyncNotifierProvider<SuggestionListController, List<DishSuggestion>> {
  /// S-01 list. Re-fetches whenever the filter changes; the server does the
  /// `0.4E + 0.3A + 0.2P + 0.1U` scoring.
  SuggestionListControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'suggestionListControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$suggestionListControllerHash();

  @$internal
  @override
  SuggestionListController create() => SuggestionListController();
}

String _$suggestionListControllerHash() =>
    r'465145a831ab0c24fcdd7cde9677852324fe57f7';

/// S-01 list. Re-fetches whenever the filter changes; the server does the
/// `0.4E + 0.3A + 0.2P + 0.1U` scoring.

abstract class _$SuggestionListController
    extends $AsyncNotifier<List<DishSuggestion>> {
  FutureOr<List<DishSuggestion>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<AsyncValue<List<DishSuggestion>>, List<DishSuggestion>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<DishSuggestion>>,
                List<DishSuggestion>
              >,
              AsyncValue<List<DishSuggestion>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
