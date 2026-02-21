from pydantic import BaseModel

class Product(BaseModel):
    id: int
    item: str
    description: str
    price: int
    quantity: int