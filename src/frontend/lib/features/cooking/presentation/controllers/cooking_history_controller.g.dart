// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'cooking_history_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// D-08 — the completed-cooking-session list (`GET /cooking/history`).

@ProviderFor(CookingHistoryController)
final cookingHistoryControllerProvider = CookingHistoryControllerProvider._();

/// D-08 — the completed-cooking-session list (`GET /cooking/history`).
final class CookingHistoryControllerProvider
    extends
        $AsyncNotifierProvider<
          CookingHistoryController,
          List<CookingHistoryEntry>
        > {
  /// D-08 — the completed-cooking-session list (`GET /cooking/history`).
  CookingHistoryControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'cookingHistoryControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$cookingHistoryControllerHash();

  @$internal
  @override
  CookingHistoryController create() => CookingHistoryController();
}

String _$cookingHistoryControllerHash() =>
    r'1f41398bc61fd855e96833b88412084444c0ad08';

/// D-08 — the completed-cooking-session list (`GET /cooking/history`).

abstract class _$CookingHistoryController
    extends $AsyncNotifier<List<CookingHistoryEntry>> {
  FutureOr<List<CookingHistoryEntry>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<List<CookingHistoryEntry>>,
              List<CookingHistoryEntry>
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<CookingHistoryEntry>>,
                List<CookingHistoryEntry>
              >,
              AsyncValue<List<CookingHistoryEntry>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// One completed session in full (`GET /cooking/history/{id}`).

@ProviderFor(cookingHistoryDetail)
final cookingHistoryDetailProvider = CookingHistoryDetailFamily._();

/// One completed session in full (`GET /cooking/history/{id}`).

final class CookingHistoryDetailProvider
    extends
        $FunctionalProvider<
          AsyncValue<CookingHistoryDetail>,
          CookingHistoryDetail,
          FutureOr<CookingHistoryDetail>
        >
    with
        $FutureModifier<CookingHistoryDetail>,
        $FutureProvider<CookingHistoryDetail> {
  /// One completed session in full (`GET /cooking/history/{id}`).
  CookingHistoryDetailProvider._({
    required CookingHistoryDetailFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'cookingHistoryDetailProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$cookingHistoryDetailHash();

  @override
  String toString() {
    return r'cookingHistoryDetailProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<CookingHistoryDetail> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<CookingHistoryDetail> create(Ref ref) {
    final argument = this.argument as String;
    return cookingHistoryDetail(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is CookingHistoryDetailProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$cookingHistoryDetailHash() =>
    r'63f152516acfbcb1bdfd886078758af57c753ea3';

/// One completed session in full (`GET /cooking/history/{id}`).

final class CookingHistoryDetailFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<CookingHistoryDetail>, String> {
  CookingHistoryDetailFamily._()
    : super(
        retry: null,
        name: r'cookingHistoryDetailProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// One completed session in full (`GET /cooking/history/{id}`).

  CookingHistoryDetailProvider call(String sessionId) =>
      CookingHistoryDetailProvider._(argument: sessionId, from: this);

  @override
  String toString() => r'cookingHistoryDetailProvider';
}
