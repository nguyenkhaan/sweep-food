# SWEEP FOOD APPLICATION BE

## Your Tasks
**Important**: Read this carefully before starting.
Your Tasks: You have to brainstorm ideas and provide a plan to build a Backend service for this application: API routes, middlewares, database, roles, data communications...

## Main Idea
The application supports:
+ Kitchen ingredient management
+ Optimizing daily meals for households.

The application must solve two problems:
+ The pressure of planning meal menus
+ Addressing surplus and spoiled ingredients

## Main Functions
### Data Input
- Support the following input methods:
    + OCR product labels (in supermarkets): to extract food information such as ingredient name, net weight, packaging date, expiration date, and price
    + OCR bills or invoices: users can take photos of their invoices. The system will detect the list of goods in invoices and assign a maintenance lifecycle to each ingredient group.
    + Voice input:
    + Manual input: Users can enter ingredient information manually.

- Food inventory and storage-duration management module
    + The maintenance lifecycle is distributed across 3 different tiers to identify usage priority:
        + Immediate-use mode / Cook-today mode: for ingredients that need to be used soon and receive high priority in the dish recommendation algorithm.
        + Refrigerator mode: applies reference storage periods by food group, such as 3 to 5 days for leafy vegetables, 7 to 10 days for root vegetables, fruits, and mushrooms, 2 to 3 days for fresh meat, fish, and seafood, while cooked food is recommended for use within a short period.
        + Freezer mode: for meat, fish, and seafood stored frozen, with the usable period determined according to the food type and appropriate storage instructions.
        Dry-goods shelf mode manages groups such as seasonings, canned food, instant noodles, and grains based on the expiration date provided by the manufacturer.
- There would be a background service to check the food inventory every day and send notifications through FCM when food is close to expiration.
- For food with an expiration date from the producer, the system will strongly rely on that information.

- Smart dish recommendation module
    + The system calculates a suitable dish score based on 3 main targets: maximizing the amount of near-expiry ingredients used, maximizing the proportion of ingredients currently available in the refrigerator, and minimizing the number of additional ingredients that need to be purchased.
    + Instead of giving a long list, the system will suggest the 3 to 5 dishes most suitable for the current inventory status.
    + Score = 0.4E + 0.3A + 0.2P + 0.1U
        E: degree of use of ingredients that are close to expiration.
        A: proportion of ingredients currently available.
        P: suitability for portion size, nutrition, time, and preferences.
        U: degree to which fewer additional purchases are needed.

- Nutrition and meal-portion estimation module
    + Dish nutrition = Sum(1-n) (Weight of ingredient i / 100 * Nutrition per 100g)

- Ingredient update module after cooking
    + When the user chooses a dish, the system will expect the quantity of ingredients used. After completion, the user can check which dish they made and also choose some quick actions: use the exact amount, use half, use all, or adjust manually.
    + The system updates the remaining quantity in inventory.
    + If a dish has not been completely consumed, the user can save the remainder as cooked food and set a reminder for use.

- Optimized shopping list module
    + This module analyzes the selected weekly meal plan to automatically create a list of seasonings and supplementary ingredients that need to be purchased. The list is compared with the virtual refrigerator status to avoid buying duplicate ingredients already available in the kitchen.