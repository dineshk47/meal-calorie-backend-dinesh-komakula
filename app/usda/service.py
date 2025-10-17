from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
import httpx
from rapidfuzz import fuzz
from ..utils.cache import usda_cache
import logging

load_dotenv()
logger = logging.getLogger(__name__)
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

USDA_API_KEY = os.getenv("USDA_API_KEY")
def search_usda_sync(query: str, pageSize: int = 10) -> Optional[Dict[str, Any]]:
    """Synchronous call to USDA FoodData Central search endpoint."""
    params = {"query": query, "pageSize": pageSize, "api_key": USDA_API_KEY}
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(USDA_SEARCH_URL, params=params)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        logger.exception("USDA search failed: %s", e)
        return None

def fuzzy_select_best(query: str, foods: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    best = None
    best_score = -1
    for f in foods:
        candidates = []
        for field in ("description", "lowercaseDescription", "dataType", "foodCategory", "brandOwner"):
            v = f.get(field) or ""
            if v:
                candidates.append(v)
        # compute token_set_ratio against each candidate and take max
        scores = [fuzz.token_set_ratio(query, c) for c in candidates] if candidates else [0]
        score = max(scores)
        if score > best_score:
            best_score = score
            best = f
    if best_score < 40:
        # low confidence
        return None
    best["_score"] = best_score
    best["_match_query"] = query
    best["_best_score"] = best_score
    return best

def extract_calories_from_food(food: Dict[str, Any]) -> Optional[float]:
    nutrients = food.get("foodNutrients") or []
    for n in nutrients:
        name = (n.get("nutrientName") or "").lower()
        if "energy" in name or "calorie" in name or "kcal" in name:
            try:
                return float(n.get("value") or 0.0)
            except Exception:
                continue
    # fallback: sometimes 'labelNutrients' exist
    label = food.get("labelNutrients") or {}
    energy = label.get("calories") or label.get("energy")
    if energy:
        try:
            return float(energy.get("value"))
        except Exception:
            pass
    return None

def get_best_calorie_for_dish(dish_name: str) -> Optional[Dict[str, Any]]:
    key = dish_name.strip().lower()
    if key in usda_cache:
        return usda_cache[key]

    data = search_usda_sync(dish_name, pageSize=25)
    if not data:
        usda_cache[key] = None
        return None
    foods = data.get("foods") or []
    best = fuzzy_select_best(dish_name, foods)
    if not best:
        usda_cache[key] = None
        return None
    calories = extract_calories_from_food(best)
    result = {
        "fdcId": best.get("fdcId"),
        "description": best.get("description"),
        "dataType": best.get("dataType"),
        "brandOwner": best.get("brandOwner"),
        "calories_per_unit": calories, 
        "raw": best
    }
    usda_cache[key] = result
    return result
