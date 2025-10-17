from app.usda.service import fuzzy_select_best, extract_calories_from_food, get_best_calorie_for_dish

def test_fuzzy_select_best():
    foods = [
        {"description": "Apple", "foodCategory": "Fruit"},
        {"description": "Rice", "foodCategory": "Grain"}
    ]
    best = fuzzy_select_best("rice", foods)
    assert best["description"] == "Rice"
    assert best["_best_score"] > 40

def test_extract_calories_from_food_energy():
    food = {"foodNutrients": [{"nutrientName": "Energy", "value": 200}]}
    assert extract_calories_from_food(food) == 200.0

def test_extract_calories_from_label_nutrients():
    food = {"labelNutrients": {"calories": {"value": 150}}}
    assert extract_calories_from_food(food) == 150.0

def test_get_best_calorie_for_dish_cache(monkeypatch):
    from app.usda.service import usda_cache
    usda_cache.clear()
    monkeypatch.setattr("app.usda.service.search_usda_sync", lambda q, pageSize=25: {"foods": [
        {"description": "Rice", "foodNutrients": [{"nutrientName": "Energy", "value": 130}]}
    ]})
    result = get_best_calorie_for_dish("rice")
    assert result["calories_per_unit"] == 130.0
