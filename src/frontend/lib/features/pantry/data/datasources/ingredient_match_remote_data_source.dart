import 'package:sweepfood/core/network/api_client.dart';
import 'package:sweepfood/core/network/api_paths.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';

/// Result of running typed text through the backend smart parser.
class IngredientMatch {
  const IngredientMatch({
    required this.name,
    this.masterIngredientId,
    this.quantity,
    this.unit,
  });

  /// Normalized ingredient name.
  final String name;

  /// Catalog id; `null` when the text did not match a catalog ingredient.
  final String? masterIngredientId;

  /// Only present when the text itself stated a quantity.
  final double? quantity;
  final MeasurementUnit? unit;
}

/// `POST /extractions/text` — typed ingredient text → smart parser.
class IngredientMatchRemoteDataSource {
  IngredientMatchRemoteDataSource(this._api);

  final ApiClient _api;

  /// Returns `null` when the parser found no ingredient in [text].
  Future<IngredientMatch?> match(String text) async {
    final json = await _api.post(ApiPaths.extractionText, body: {'text': text});
    final fields =
        (json as Map<String, dynamic>)['fields'] as Map<String, dynamic>? ?? {};
    final name = fields['ingredient_name']?.toString();
    if (name == null || name.trim().isEmpty) return null;
    final unit = fields['unit']?.toString();
    return IngredientMatch(
      name: name,
      masterIngredientId: fields['master_ingredient_id']?.toString(),
      quantity: (fields['quantity'] as num?)?.toDouble(),
      unit: unit == null ? null : MeasurementUnit.fromWire(unit),
    );
  }
}
