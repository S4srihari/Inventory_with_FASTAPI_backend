from pydantic import BaseModel

class Product(BaseModel):
    id: int
    item: str
    description: str
    price: int
    quantity: int

class UserCreate(BaseModel):
    name: str
    email: str
    role: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    
    class Config:
        from_attributes = True