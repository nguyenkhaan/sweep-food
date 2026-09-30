# SweepFood Crawler & Nutritional Extractor

This directory contains ingestion scripts and tools to extract ingredient and food nutritional data from the **National Institute of Nutrition (Viện Dinh Dưỡng Quốc Gia - NIN)** and external PDF nutrition sheets.

---

## 1. Viện Dinh Dưỡng Food Composition Crawler

### Architecture & Discovery
On the website `https://viendinhduong.vn/vi/cong-cu-va-tien-ich/gia-tri-dinh-duong-thuc-pham`, the user interface displays food items and dynamically generates tabular PDF reports using client-side libraries (`jsPDF`).

Under the hood, the frontend consumes an internal REST API endpoint:
```http
GET https://viendinhduong.vn/api/fe/foodNatunal/getPageFoodData?page=1&pageSize=1000
```

This endpoint returns the **complete, pristine, structured JSON** for all **853 food items** in Vietnam, including:
* Food code (`code`) and canonical names (`name_vi`, `name_en`).
* Category grouping (`category`, `categoryEn`).
* Standardized energy per 100g (`energy` in Kcal).
* 30+ macronutrients and micronutrients:
  * Protein, Fat, Carbohydrates, Dietary Fiber, Sugars, Water, Ash.
  * Minerals: Calcium (Ca), Iron (Fe), Sodium (Na), Potassium (K), Zinc (Zn), Magnesium (Mg), Phosphorus (P), Copper (Cu), Manganese (Mn), Selenium (Se).
  * Vitamins: Vitamin A (Retinol, Vit A-RAE), Vitamin C, B1, B2, B3, B5, B6, Folate.
  * Saturated / Monounsaturated / Polyunsaturated Fatty Acids and Essential Amino Acids.

### Execution
Run the crawler script:
```bash
python crawler/crawl_viendinhduong.py
```

### Outputs
* **Raw JSON**: `data/raw/viendinhduong/food_nutrition_raw.json` (Full verbatim payload for auditability).
* **Master Ingredients Nutrition CSV**: `data/processed/viendinhduong/master_ingredients_nutrition.csv` (Flattened table formatted for direct seeding into the `master_ingredients` database table).
* **Ingredient Categories CSV**: `data/processed/viendinhduong/ingredient_categories.csv` (Extracted categories for `ingredient_categories`).

---

## 2. PDF Nutritional Table Extractor (`pdf_extractor.py`)

If you have offline PDF nutrition sheets, laboratory test results, or PDF food composition tables, use `pdf_extractor.py`.

### Execution
```bash
# Print extracted nutrients to stdout
python crawler/pdf_extractor.py path/to/document.pdf

# Export to CSV
python crawler/pdf_extractor.py path/to/document.pdf -o output_nutrients.csv

# Export to JSON
python crawler/pdf_extractor.py path/to/document.pdf -o output_nutrients.json
```
