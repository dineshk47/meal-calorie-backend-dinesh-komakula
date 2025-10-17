from fastapi import APIRouter, Depends, HTTPException, Request
from app.auth.errors import success_response
from app.verify import get_current_user
import schemas
from ..usda.service import get_best_calorie_for_dish

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Depends

# Use the same limiter instance
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.post("/get-calories", response_model=schemas.CalorieResponse)
@limiter.limit("15/minute")
def get_calories(payload: schemas.GetCaloriesRequest, request: Request, user=Depends(get_current_user)):
    name = payload.dish_name.strip()
    if not name or len(name) < 2:
        raise HTTPException(status_code=422, detail={
                    "status": "GE42201",
                    "error": "Dish name too short",
                })
    usda = get_best_calorie_for_dish(name)
    if not usda or usda.get("calories_per_unit") is None:
        raise HTTPException(status_code=404, detail={
                    "status": "GE40401",
                    "error": "Dish not found or calories not available",
                })
        
    calories_per_serving = float(usda["calories_per_unit"])
    total = calories_per_serving * payload.servings
    raw = usda.get("raw", {}) or {}
    ingredients = None
    ing_text = raw.get("ingredients") or raw.get("ingredientDescription") or None
    if ing_text:
        ingredients = [schemas.IngredientBreakdown(name=ing_text[:400], calories_per_serving=calories_per_serving)]
    resp = schemas.CalorieResponse(
        dish_name=payload.dish_name,
        servings=payload.servings,
        calories_per_serving=calories_per_serving,
        total_calories=total,
        source="USDA FoodData Central",
        ingredients=ingredients
    )
    return resp
   