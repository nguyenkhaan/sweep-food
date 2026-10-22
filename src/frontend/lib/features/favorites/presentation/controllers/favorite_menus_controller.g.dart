// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'favorite_menus_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(FavoriteMenusController)
final favoriteMenusControllerProvider = FavoriteMenusControllerProvider._();

final class FavoriteMenusControllerProvider
    extends
        $AsyncNotifierProvider<FavoriteMenusController, List<FavoriteMenu>> {
  FavoriteMenusControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'favoriteMenusControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$favoriteMenusControllerHash();

  @$internal
  @override
  FavoriteMenusController create() => FavoriteMenusController();
}

String _$favoriteMenusControllerHash() =>
    r'823cddb5c0ff94288d96944572904710ecf3e0aa';

abstract class _$FavoriteMenusController
    extends $AsyncNotifier<List<FavoriteMenu>> {
  FutureOr<List<FavoriteMenu>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<List<FavoriteMenu>>, List<FavoriteMenu>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<FavoriteMenu>>, List<FavoriteMenu>>,
              AsyncValue<List<FavoriteMenu>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

@ProviderFor(FavoriteMenuDetailController)
final favoriteMenuDetailControllerProvider =
    FavoriteMenuDetailControllerFamily._();

final class FavoriteMenuDetailControllerProvider
    extends
        $AsyncNotifierProvider<
          FavoriteMenuDetailController,
          FavoriteMenuDetail
        > {
  FavoriteMenuDetailControllerProvider._({
    required FavoriteMenuDetailControllerFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'favoriteMenuDetailControllerProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$favoriteMenuDetailControllerHash();

  @override
  String toString() {
    return r'favoriteMenuDetailControllerProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  FavoriteMenuDetailController create() => FavoriteMenuDetailController();

  @override
  bool operator ==(Object other) {
    return other is FavoriteMenuDetailControllerProvider &&
        other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$favoriteMenuDetailControllerHash() =>
    r'07f1a4ffaaa95e8403d839d93bfcb17348921c69';

final class FavoriteMenuDetailControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          FavoriteMenuDetailController,
          AsyncValue<FavoriteMenuDetail>,
          FavoriteMenuDetail,
          FutureOr<FavoriteMenuDetail>,
          String
        > {
  FavoriteMenuDetailControllerFamily._()
    : super(
        retry: null,
        name: r'favoriteMenuDetailControllerProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  FavoriteMenuDetailControllerProvider call(String menuId) =>
      FavoriteMenuDetailControllerProvider._(argument: menuId, from: this);

  @override
  String toString() => r'favoriteMenuDetailControllerProvider';
}

abstract class _$FavoriteMenuDetailController
    extends $AsyncNotifier<FavoriteMenuDetail> {
  late final _$args = ref.$arg as String;
  String get menuId => _$args;

  FutureOr<FavoriteMenuDetail> build(String menuId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<FavoriteMenuDetail>, FavoriteMenuDetail>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<FavoriteMenuDetail>, FavoriteMenuDetail>,
              AsyncValue<FavoriteMenuDetail>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
