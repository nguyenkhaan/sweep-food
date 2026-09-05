// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'suggestion_repository_impl.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(suggestionRepository)
final suggestionRepositoryProvider = SuggestionRepositoryProvider._();

final class SuggestionRepositoryProvider
    extends
        $FunctionalProvider<
          SuggestionRepository,
          SuggestionRepository,
          SuggestionRepository
        >
    with $Provider<SuggestionRepository> {
  SuggestionRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'suggestionRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$suggestionRepositoryHash();

  @$internal
  @override
  $ProviderElement<SuggestionRepository> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  SuggestionRepository create(Ref ref) {
    return suggestionRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(SuggestionRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<SuggestionRepository>(value),
    );
  }
}

String _$suggestionRepositoryHash() =>
    r'ae1f45dbcf0cd8657185af2bbb3cc70ae4fb0c22';
