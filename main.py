from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from databaseconfig import session, engine
import db_models 
from sqlalchemy.orm import Session

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
        db.close


@app.get('/products')
def get_all_products(db: Session = Depends(get_db)):
    all_products = db.query(db_models.Product).all()
    return all_products

@app.get('/products/{id}')
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    try:
        item = db.query(db_models.Product).filter(db_models.Product.id == id).first()
        if item:
            return item
        return "No Product found"
    except:
        return "Invalid request"
    
@app.post('/products')
def add_product(product: Product, db: Session = Depends(get_db)):
    try:
        db.add(db_models.Product(**product.model_dump()))
        db.commit()
        return product
    except:
        return "failed to add"

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
    except:
        return "error while updating"

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
    except:
        return "error while deleting"