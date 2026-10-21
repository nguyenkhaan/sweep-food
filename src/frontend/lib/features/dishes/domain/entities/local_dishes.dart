import 'package:sweepfood/features/dishes/domain/entities/cooking_step.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish.dart';
import 'package:sweepfood/features/dishes/domain/entities/dish_ingredient.dart';
import 'package:sweepfood/features/suggestions/domain/entities/dish_suggestion.dart';
import 'package:sweepfood/features/suggestions/domain/entities/score_breakdown.dart';
import 'package:sweepfood/shared/domain/measurement_unit.dart';
import 'package:sweepfood/shared/domain/nutrition_info.dart';

final _uuidRegex = RegExp(
  r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$',
);

/// Returns true if [id] is a valid 36-character UUID string.
bool isUuid(String id) => _uuidRegex.hasMatch(id);

/// Predefined local dishes used as offline/sample recipes when navigating
/// from mock data or local matching.
final Map<String, Dish> _kLocalDishes = {
  'd1': const Dish(
    id: 'd1',
    name: 'Salad bơ ức gà',
    servings: 2,
    prepTimeMin: 15,
    cookTimeMin: 10,
    cuisine: 'Món trộn',
    difficulty: 'Dễ',
    nutritionPerServing: NutritionInfo(
      energyKcal: 320,
      proteinG: 28,
      carbG: 30,
      lipidG: 14,
    ),
    ingredients: [
      DishIngredient(
        name: 'Ức gà',
        quantity: 200,
        unit: MeasurementUnit.gram,
      ),
      DishIngredient(
        name: 'Cà chua bi',
        quantity: 100,
        unit: MeasurementUnit.gram,
      ),
      DishIngredient(
        name: 'Bơ',
        quantity: 1,
        unit: MeasurementUnit.fruit,
      ),
      DishIngredient(
        name: 'Xà lách',
        quantity: 150,
        unit: MeasurementUnit.gram,
      ),
      DishIngredient(
        name: 'Dầu ô liu',
        quantity: 15,
        unit: MeasurementUnit.milliliter,
        isSeasoning: true,
      ),
    ],
    steps: [
      CookingStep(
        order: 1,
        text: 'Luộc hoặc áp chảo ức gà chín tới, để nguội rồi xé sợi.',
      ),
      CookingStep(
        order: 2,
        text: 'Bơ cắt lát, cà chua bi bổ đôi, xà lách rửa sạch để ráo.',
      ),
      CookingStep(
        order: 3,
        text: 'Pha nước trộn: dầu ô liu, nước cốt chanh, mật ong, muối, tiêu.',
      ),
      CookingStep(
        order: 4,
        text: 'Cho tất cả vào tô, rưới nước trộn, đảo nhẹ và dùng ngay.',
      ),
    ],
  ),
  'd2': const Dish(
    id: 'd2',
    name: 'Canh chua cá lóc',
    servings: 3,
    prepTimeMin: 15,
    cookTimeMin: 20,
    cuisine: 'Món canh',
    difficulty: 'Trung bình',
    nutritionPerServing: NutritionInfo(
      energyKcal: 280,
      proteinG: 26,
      carbG: 18,
      lipidG: 11,
    ),
    ingredients: [
      DishIngredient(
        name: 'Cá lóc',
        quantity: 300,
        unit: MeasurementUnit.gram,
      ),
      DishIngredient(
        name: 'Cà chua bi',
        quantity: 100,
        unit: MeasurementUnit.gram,
      ),
      DishIngredient(
        name: 'Cải bó xôi',
        quantity: 1,
        unit: MeasurementUnit.bunch,
      ),
      DishIngredient(
        name: 'Đậu bắp',
        quantity: 50,
        unit: MeasurementUnit.gram,
      ),
      DishIngredient(
        name: 'Giá đỗ',
        quantity: 100,
        unit: MeasurementUnit.gram,
      ),
      DishIngredient(
        name: 'Nước mắm',
        quantity: 10,
        unit: MeasurementUnit.milliliter,
        isSeasoning: true,
      ),
    ],
    steps: [
      CookingStep(
        order: 1,
        text: 'Cá lóc làm sạch, cắt khúc vừa ăn, ướp chút muối, tiêu.',
      ),
      CookingStep(
        order: 2,
        text: 'Đun sôi nước, cho cá vào nấu chín tới, vớt bọt cho nước trong.',
      ),
      CookingStep(
        order: 3,
        text: 'Cho cà chua, đậu bắp, giá đỗ và cải vào nấu sôi lại khoảng 3-5 phút.',
      ),
      CookingStep(
        order: 4,
        text: 'Nêm gia vị chua ngọt vừa ăn, tắt bếp và rắc rau thơm lên trên.',
      ),
    ],
  ),
  'd3': const Dish(
    id: 'd3',
    name: 'Trứng chiên hành lá',
    servings: 2,
    prepTimeMin: 5,
    cookTimeMin: 5,
    cuisine: 'Món mặn',
    difficulty: 'Dễ',
    nutritionPerServing: NutritionInfo(
      energyKcal: 210,
      proteinG: 15,
      carbG: 3,
      lipidG: 15,
    ),
    ingredients: [
      DishIngredient(
        name: 'Trứng gà',
        quantity: 3,
        unit: MeasurementUnit.fruit,
      ),
      DishIngredient(
        name: 'Hành lá',
        quantity: 20,
        unit: MeasurementUnit.gram,
      ),
      DishIngredient(
        name: 'Nước mắm',
        quantity: 10,
        unit: MeasurementUnit.milliliter,
        isSeasoning: true,
      ),
    ],
    steps: [
      CookingStep(
        order: 1,
        text: 'Đập trứng vào bát, thêm hành lá cắt nhỏ, nước mắm và chút tiêu.',
      ),
      CookingStep(
        order: 2,
        text: 'Dùng đũa đánh đều cho trứng tan và sủi bọt nhẹ.',
      ),
      CookingStep(
        order: 3,
        text: 'Đun nóng chảo với chút dầu ăn, đổ trứng vào tráng đều chảo.',
      ),
      CookingStep(
        order: 4,
        text: 'Chiên vàng một mặt rồi lật mặt còn lại, chín vàng thì tắt bếp.',
      ),
    ],
  ),
  'd4': const Dish(
    id: 'd4',
    name: 'Thịt ba chỉ rang cháy cạnh',
    servings: 3,
    prepTimeMin: 10,
    cookTimeMin: 15,
    cuisine: 'Món mặn',
    difficulty: 'Trung bình',
    nutritionPerServing: NutritionInfo(
      energyKcal: 420,
      proteinG: 22,
      carbG: 6,
      lipidG: 35,
    ),
    ingredients: [
      DishIngredient(
        name: 'Thịt ba chỉ',
        quantity: 300,
        unit: MeasurementUnit.gram,
      ),
      DishIngredient(
        name: 'Hành tím',
        quantity: 3,
        unit: MeasurementUnit.fruit,
      ),
      DishIngredient(
        name: 'Nước mắm',
        quantity: 20,
        unit: MeasurementUnit.milliliter,
        isSeasoning: true,
      ),
      DishIngredient(
        name: 'Đường',
        quantity: 10,
        unit: MeasurementUnit.gram,
        isSeasoning: true,
      ),
    ],
    steps: [
      CookingStep(
        order: 1,
        text: 'Thịt ba chỉ rửa sạch, thái miếng mỏng vừa ăn.',
      ),
      CookingStep(
        order: 2,
        text: 'Cho thịt vào chảo đảo đều trên lửa vừa cho đến khi xém cạnh và ra bớt mỡ.',
      ),
      CookingStep(
        order: 3,
        text: 'Phi thơm hành tím băm nhỏ cùng thịt trong chảo.',
      ),
      CookingStep(
        order: 4,
        text: 'Cho nước mắm, đường vào đảo đều đến khi thịt lên màu cánh gián đẹp mắt thì tắt bếp.',
      ),
    ],
  ),
  'd5': const Dish(
    id: 'd5',
    name: 'Đậu hũ sốt cà chua',
    servings: 2,
    prepTimeMin: 5,
    cookTimeMin: 10,
    cuisine: 'Món xào',
    difficulty: 'Dễ',
    nutritionPerServing: NutritionInfo(
      energyKcal: 190,
      proteinG: 14,
      carbG: 12,
      lipidG: 10,
    ),
    ingredients: [
      DishIngredient(
        name: 'Đậu hũ non',
        quantity: 2,
        unit: MeasurementUnit.box,
      ),
      DishIngredient(
        name: 'Cà chua bi',
        quantity: 200,
        unit: MeasurementUnit.gram,
      ),
      DishIngredient(
        name: 'Hành lá',
        quantity: 20,
        unit: MeasurementUnit.gram,
      ),
    ],
    steps: [
      CookingStep(
        order: 1,
        text: 'Đậu hũ cắt miếng vuông vừa ăn, có thể chiên sơ hoặc để non tùy thích.',
      ),
      CookingStep(
        order: 2,
        text: 'Cà chua băm nhỏ, xào mềm với chút dầu ăn để tạo sốt sánh mịn.',
      ),
      CookingStep(
        order: 3,
        text: 'Cho đậu hũ vào đun cùng sốt cà chua trên lửa nhỏ khoảng 5 phút cho ngấm gia vị.',
      ),
      CookingStep(
        order: 4,
        text: 'Nêm nếm vừa ăn, rắc hành lá cắt nhỏ lên trên rồi tắt bếp.',
      ),
    ],
  ),
  'd6': const Dish(
    id: 'd6',
    name: 'Canh cải thịt băm',
    servings: 2,
    prepTimeMin: 10,
    cookTimeMin: 10,
    cuisine: 'Món canh',
    difficulty: 'Dễ',
    nutritionPerServing: NutritionInfo(
      energyKcal: 160,
      proteinG: 18,
      carbG: 6,
      lipidG: 7,
    ),
    ingredients: [
      DishIngredient(
        name: 'Cải bó xôi',
        quantity: 1,
        unit: MeasurementUnit.bunch,
      ),
      DishIngredient(
        name: 'Thịt nạc xay',
        quantity: 150,
        unit: MeasurementUnit.gram,
      ),
      DishIngredient(
        name: 'Hành tím',
        quantity: 2,
        unit: MeasurementUnit.fruit,
      ),
    ],
    steps: [
      CookingStep(
        order: 1,
        text: 'Rau cải rửa sạch, cắt khúc vừa ăn. Thịt xay ướp chút gia vị và hành tím băm.',
      ),
      CookingStep(
        order: 2,
        text: 'Phi thơm hành tím, cho thịt băm vào xào săn thơm.',
      ),
      CookingStep(
        order: 3,
        text: 'Đổ nước vừa đủ vào đun sôi, vớt bọt nếu có.',
      ),
      CookingStep(
        order: 4,
        text: 'Cho rau cải vào nấu chín tới, nêm gia vị vừa ăn rồi tắt bếp.',
      ),
    ],
  ),
};

/// Lookup a local/sample dish by [id].
/// If the id is not in the predefined map, a sensible fallback dish is generated.
Dish getLocalDish(String id, {String? customName}) {
  final found = _kLocalDishes[id];
  if (found != null) return found;

  return Dish(
    id: id,
    name: customName ?? 'Món ngon mỗi ngày',
    servings: 2,
    prepTimeMin: 15,
    cookTimeMin: 15,
    cuisine: 'Món gia đình',
    difficulty: 'Dễ',
    nutritionPerServing: const NutritionInfo(
      energyKcal: 250,
      proteinG: 20,
      carbG: 15,
      lipidG: 10,
    ),
    ingredients: const [
      DishIngredient(
        name: 'Gia vị tổng hợp',
        quantity: 1,
        unit: MeasurementUnit.pack,
        isSeasoning: true,
      ),
    ],
    steps: const [
      CookingStep(
        order: 1,
        text: 'Sơ chế sạch các nguyên liệu trước khi nấu.',
      ),
      CookingStep(
        order: 2,
        text: 'Nấu chín các nguyên liệu theo khẩu vị gia đình.',
      ),
    ],
  );
}

/// Convert a local dish into a [DishSuggestion] so suggestions screens
/// can display it without missing fields.
DishSuggestion getLocalDishSuggestion(String id, {String? customName}) {
  final dish = getLocalDish(id, customName: customName);
  return DishSuggestion(
    dish: dish,
    breakdown: const ScoreBreakdown(
      e: 0.8,
      a: 0.9,
      p: 0.8,
      u: 0.9,
    ),
    rank: 1,
  );
}
