import 'package:frontend/core/network/api_result.dart';
import 'package:frontend/core/network/network_providers.dart';
import 'package:frontend/core/utils/result.dart';
import 'package:frontend/features/suggestions/data/datasources/suggestion_remote_data_source.dart';
import 'package:frontend/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:frontend/features/suggestions/domain/entities/suggestion_request.dart';
import 'package:frontend/features/suggestions/domain/repositories/suggestion_repository.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'suggestion_repository_impl.g.dart';

@Riverpod(keepAlive: true)
SuggestionRepository suggestionRepository(Ref ref) => SuggestionRepositoryImpl(
      SuggestionRemoteDataSource(ref.watch(apiClientProvider)),
    );

class SuggestionRepositoryImpl implements SuggestionRepository {
  SuggestionRepositoryImpl(this._remote);

  final SuggestionRemoteDataSource _remote;

  @override
  Future<Result<List<DishSuggestion>>> fetch(SuggestionRequest request) =>
      runGuarded(() async {
        final dtos = await _remote.fetch(request);
        return [for (final d in dtos) d.toEntity()];
      });
}
