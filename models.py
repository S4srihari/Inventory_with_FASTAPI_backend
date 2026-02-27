from typing import Optional
from pydantic import BaseModel

class PyProduct(BaseModel):
    id: Optional[int] = None
    item: str
    description: str
    price: float
    quantity: int

class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None