// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'entitlements_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// The current user's [Entitlements].
///
/// While [kPremiumEnabled] is `false` this is always [Entitlements.allUnlocked].
/// When gating goes live, back this with the `/subscription` response.

@ProviderFor(entitlements)
final entitlementsProvider = EntitlementsProvider._();

/// The current user's [Entitlements].
///
/// While [kPremiumEnabled] is `false` this is always [Entitlements.allUnlocked].
/// When gating goes live, back this with the `/subscription` response.

final class EntitlementsProvider
    extends $FunctionalProvider<Entitlements, Entitlements, Entitlements>
    with $Provider<Entitlements> {
  /// The current user's [Entitlements].
  ///
  /// While [kPremiumEnabled] is `false` this is always [Entitlements.allUnlocked].
  /// When gating goes live, back this with the `/subscription` response.
  EntitlementsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'entitlementsProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$entitlementsHash();

  @$internal
  @override
  $ProviderElement<Entitlements> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  Entitlements create(Ref ref) {
    return entitlements(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(Entitlements value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<Entitlements>(value),
    );
  }
}

String _$entitlementsHash() => r'd6113d65709159d69d92948258d47942d0439188';

/// Whether [feature] is available right now.

@ProviderFor(featureAllowed)
final featureAllowedProvider = FeatureAllowedFamily._();

/// Whether [feature] is available right now.

final class FeatureAllowedProvider extends $FunctionalProvider<bool, bool, bool>
    with $Provider<bool> {
  /// Whether [feature] is available right now.
  FeatureAllowedProvider._({
    required FeatureAllowedFamily super.from,
    required Feature super.argument,
  }) : super(
         retry: null,
         name: r'featureAllowedProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$featureAllowedHash();

  @override
  String toString() {
    return r'featureAllowedProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $ProviderElement<bool> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  bool create(Ref ref) {
    final argument = this.argument as Feature;
    return featureAllowed(ref, argument);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(bool value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<bool>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is FeatureAllowedProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$featureAllowedHash() => r'de0642da8bec9b2701f7883c8ce3ab3f232e8c4d';

/// Whether [feature] is available right now.

final class FeatureAllowedFamily extends $Family
    with $FunctionalFamilyOverride<bool, Feature> {
  FeatureAllowedFamily._()
    : super(
        retry: null,
        name: r'featureAllowedProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Whether [feature] is available right now.

  FeatureAllowedProvider call(Feature feature) =>
      FeatureAllowedProvider._(argument: feature, from: this);

  @override
  String toString() => r'featureAllowedProvider';
}
