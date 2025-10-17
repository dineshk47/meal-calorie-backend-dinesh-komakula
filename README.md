# Meal Calorie Count Generator - Backend

A **FastAPI backend** for calculating total calories of a dish using the USDA FoodData Central API.  
Includes user authentication, fuzzy matching of dish names, and optional ingredient breakdown.

---

## Features

- User registration and login with JWT authentication
- Calculate calories per serving and total calories
- Ingredient breakdown (if available)
- Fuzzy matching of dish names
- PostgreSQL database
- Optional caching for repeated queries

---

## Tech Stack

- **Python 3.11+**
- **FastAPI** (for building API)
- **SQLAlchemy** (ORM for PostgreSQL)
- **PostgreSQL** (user and authentication data)
- **httpx** (for USDA API calls)
- **rapidfuzz** (for fuzzy matching)
- **pytest** (for testing)

---

## Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/meal-calorie-backend.git
   cd meal-calorie-backend

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Create .env file based on .env.example:
   ```bash
   cp .env.example .env

4. Start server:
   ```bash
   uvicorn main:app --reload

5. Run tests:
   ```bash
   pytest

API Endpoints
1. Authentication
   | Method | Path             | Request Body                                                                                                | Description                                                         |
   | ------ | ---------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
   | POST   | `/auth/register` | `json { "first_name": "John", "last_name": "Doe", "email": "john@example.com", "password": "strongpass" } ` | Registers a new user. Returns user ID and success message.          |
   | POST   | `/auth/login`    | `json { "email": "john@example.com", "password": "strongpass" } `                                           | Logs in a user. Returns JWT access token and token type (`bearer`). |

Sample Login Response:
```json
{
  "status_code": "GS20001",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
  }
}
```
2. Calories
      | Method | Path                      | Request Body                                              | Description                                                                                                                         |
      | ------ | ------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
      | POST   | `/calrories/get-calories` | `json { "dish_name": "chicken biryani", "servings": 2 } ` | Calculates calories for the dish. Uses USDA API with fuzzy matching. Returns calories per serving, total calories, and ingredients. |

Sample Response:
   ```json
   {
     "dish_name": "chicken biryani",
     "servings": 2,
     "calories_per_serving": 280,
     "total_calories": 560,
     "source": "USDA FoodData Central",
     "ingredients": [
       {
         "name": "Chicken, Rice, Spices",
         "calories_per_serving": 280
       }
     ]
   }
```
Error Responses:
  422: Dish name too short
  404: Dish not found or calories unavailable

3. Users (Protected Routes – JWT required)
      | Method | Path               | Description                                                                                                                 |
      | ------ | ------------------ | --------------------------------------------------------------------------------------------------------------------------- |
      | GET    | `/users/`          | Returns a paginated list of all users. Query parameters: `limit` (default 10), `offset` (default 0), `q` (optional search). |
      | GET    | `/users/{user_id}` | Returns details of a specific user by ID.                                                                                   |
      | PATCH  | `/users/{user_id}` | Updates user details. Request body can contain any of `first_name`, `last_name`, `email`, `password`.                       |
      | DELETE | `/users/{user_id}` | Deletes a user by ID.                                                                                                       |
Sample GET /users/ Response:
```json
{
  "status_code": "GS20006",
  "data": {
    "result": [
      {
        "id": 1,
        "email": "john@example.com"
      }
    ],
    "detail": "Users list"
  }
}
```
Sample GET /users/{user_id}/ Response:
```json
{
  "status_code": "GS20006",
  "data": {
    "result": [
      {
        "id": 1,
        "first_name": "john",
        "last_name": "smith",
        "email": "john@example.com"
      }
    ],
    "detail": "User data"
  }
}
```
**Error Codes**

All API responses use structured error codes and messages for consistency. Below is a list of all possible codes and their associated endpoints:
   | Code    | Description                              | Endpoint                    |
   | ------- | ---------------------------------------- | --------------------------- |
   | GE40001 | Email already registered                 | `/auth/register`            |
   | GE40002 | Registration failed                      | `/auth/register`            |
   | GE40003 | Token missing                            | `/auth/*`                   |
   | GE40101 | Invalid credentials                      | `/auth/login`               |
   | GE40102 | Invalid or expired token                 | Any authenticated endpoint  |
   | GE40103 | User not found                           | Any user endpoint           |
   | GE42201 | Dish name too short                      | `/calrories/get-calories`   |
   | GE40401 | Dish not found or calories not available | `/calrories/get-calories`   |
   | GE40402 | User not found                           | `/users/{user_id}` (GET)    |
   | GE40403 | User not found                           | `/users/{user_id}` (PATCH)  |
   | GE40404 | User not found                           | `/users/{user_id}` (DELETE) |
   | GS20101 | Registered successfully                  | `/auth/register`            |
   | GS20001 | Token generated                          | `/auth/login`               |
   | GS20002 | Token generated                          | `/calrories/get-calories`   |
   | GS20003 | User data                                | `/users/{user_id}` (GET)    |
   | GS20004 | User updated                             | `/users/{user_id}` (PATCH)  |
   | GS20005 | User deleted                             | `/users/{user_id}` (DELETE) |
   | GS20006 | Users list                               | `/users/` (GET)             |

Decisions / Trade-offs
  FastAPI chosen for speed, async support, and built-in validation.
  SQLAlchemy ORM used for structured database interaction.
  Fuzzy matching via rapidfuzz to handle partial dish name matches.
  JWT tokens used for authentication.
  Passwords securely hashed using industry-standard algorithms.
  Rate limiting implemented.

.env Variables
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=meal_calorie_db
DB_USER=postgres
DB_PASS=postgres

# USDA API
USDA_API_KEY=your_usda_api_key_here

# JWT Secret
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

Testing
  Run all tests:
   ```bash
       pytest -v
   ```
  
Test cases include:
  Common dishes: macaroni and cheese, grilled salmon, paneer butter asala
  Non-existent dishes
  Zero or negative servings
  Multiple similar matches

Hosted Link
Local server: http://localhost:8000/docs
