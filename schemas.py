import re
from pydantic import BaseModel, EmailStr, conint, field_validator
from typing import Optional, List

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    class Config:
        extra = "forbid" 
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    class Config:
        extra = "forbid" 

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    class Config:
        extra = "forbid" 
    
    
class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes = True

class PostResponse(BaseModel):
    id: int

    class Config:
        from_attributes = True

class OutUsers(BaseModel):
    id: int
    email: EmailStr
    
    class Config:
        from_attributes=True

class OutUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes=True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None 

    class Config:
        from_attributes = True
        extra = "forbid" 
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None 


class GetCaloriesRequest(BaseModel):
    dish_name: str
    servings: conint(gt=0)

class IngredientBreakdown(BaseModel):
    name: str
    calories_per_serving: Optional[float] = None
    amount_descriptor: Optional[str] = None

class CalorieResponse(BaseModel):
    dish_name: str
    servings: int
    calories_per_serving: float
    total_calories: float
    source: str
    ingredients: Optional[List[IngredientBreakdown]] = None
