// test/helpers/mocks.dart
// Shared mocktail doubles for the API client and repositories.
import 'package:frontend/core/network/api_client.dart';
import 'package:frontend/features/cooking/domain/repositories/cooking_repository.dart';
import 'package:frontend/features/dishes/domain/repositories/dish_repository.dart';
import 'package:frontend/features/ingest/domain/repositories/scan_repository.dart';
import 'package:frontend/features/pantry/domain/repositories/pantry_repository.dart';
import 'package:frontend/features/suggestions/domain/repositories/suggestion_repository.dart';
import 'package:mocktail/mocktail.dart';

class MockApiClient extends Mock implements ApiClient {}

class MockPantryRepository extends Mock implements PantryRepository {}

class MockSuggestionRepository extends Mock implements SuggestionRepository {}

class MockDishRepository extends Mock implements DishRepository {}

class MockCookingRepository extends Mock implements CookingRepository {}

class MockScanRepository extends Mock implements ScanRepository {}
