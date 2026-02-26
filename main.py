from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Product, UserCreate, UserResponse
from databaseconfig import session, engine
import db_models 
from sqlalchemy.orm import Session
from typing import List

app = FastAPI()

db_models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_methods = ["*"]
)

@app.get('/')
def main():
    return "Hello from inventory!"

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


@app.get('/products')
def get_all_products(db: Session = Depends(get_db)):
    try:
        all_products = db.query(db_models.Product).all()
        return all_products
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/products/{id}')
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    try:
        item = db.query(db_models.Product).filter(db_models.Product.id == id).first()
        if item:
            return item
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post('/products')
def add_product(product: Product, db: Session = Depends(get_db)):
    try:
        db.add(db_models.Product(**product.model_dump()))
        db.commit()
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put('/products/{id}')
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    try:
        old_product = db.query(db_models.Product).filter(db_models.Product.id == id).first()
        if old_product:
            old_product.description = product.description
            old_product.item = product.item
            old_product.price = product.price
            old_product.quantity = product.quantity
            db.commit()
            return "Updated Succesfully"
        else:
            return "Updated failed"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete('/products/{id}')
def delete_product(id: int, db: Session = Depends(get_db)):
    try:
        stale_product = db.query(db_models.Product).filter(db_models.Product.id == id).first()
        if stale_product:
            db.delete(stale_product)
            db.commit()
            return "Product deleted successfully"
        else:
            return "Product not found"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    try:
        return db.query(db_models.User).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get one user by ID"""
    try :
        user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        if db.query(db_models.User).filter(db_models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        db_user = db_models.User(**user.model_dump())
        db.add(db_user)
        db.commit()
        return db_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    """Update a user"""
    try:
        db_user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.name = user.name
        db_user.email = user.email
        db_user.role = user.role
        
        db.commit()
        return db_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    try:
        user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
        return {"message": "User deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))