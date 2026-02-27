from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import PyProduct, Token, TokenData, UserCreate, UserResponse
from databaseconfig import sessionLocal, engine
import db_models 
from db_models import User, Product
from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from securityconfig import SECRET_KEY, ALGORITHM, TOKEN_EXPIRES


#Auth details
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI()

db_models.Base.metadata.create_all(bind=engine)



def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_methods = ["*"],
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_headers=["*"],
)

# Auth Functions
def verify_pwd(plain_pwd:str, hashed_pwd:str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)

def get_pwd_hash(password:str) -> str:
    return pwd_context.hash(password)

def create_access_token(data:dict, expires_delta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta

    to_encode.update({'exp':expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token:str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail=str("Couldn't verify email"))
        return TokenData(email=email)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))



# Auth Dependencies
def get_current_user(token:str = Depends(oauth2_scheme), db:Session=Depends(get_db)):
    try:
        token_data = verify_token(token)
        current_user = db.query(User).filter(User.email==token_data.email).first()
        if current_user is None:
            raise HTTPException(status_code=401, detail="User does not exist")
        return current_user
    except HTTPException:
        raise                            # ← let HTTPExceptions pass through cleanly
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=404, detail="Inactive User")
    return current_user



# Auth Endpoints
@app.post('/register')
def userRegistration(new_user: UserCreate, db:Session=Depends(get_db)):
    try:
        if db.query(User).filter(User.email == new_user.email).first():
            raise HTTPException(status_code=400, detail="Email already exists")
        hashed_password = get_pwd_hash(new_user.password)
        db_new_user = User(
            name = new_user.name,
            email = new_user.email,
            role = new_user.role,
            hashed_pwd = hashed_password 
        )
        db.add(db_new_user) 
        db.commit()
        return {"user registered"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/token", response_model=Token)
def login_for_access_token(form_data:OAuth2PasswordRequestForm=Depends(), db:Session=Depends(get_db)):
    try:
        current_user = db.query(User).filter(User.email==form_data.username).first()

        if not current_user or not verify_pwd(form_data.password, current_user.hashed_pwd):
            raise HTTPException(status_code=404, detail="Incorrect Credentials")
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="User Inactive!")
        
        access_token_expires = timedelta(minutes=TOKEN_EXPIRES)
        access_token = create_access_token(
            data={"sub":current_user.email}, expires_delta=access_token_expires
        )
        return {"access_token":access_token, "token_type":"bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# Route Functions
@app.get('/')
def main():
    return {"message": "Hello from inventory!"}

@app.get('/profile', response_model=UserResponse)
def get_profile(current_user:User = Depends(get_current_active_user)):
    return current_user

@app.get('/verify-token')
def verify_token_endpoint(current_user:User = Depends(get_current_active_user)):
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "name":current_user.name,
            "email":current_user.email,
            "role":current_user.role
        }
    }



## Product Routes
@app.get('/products')
def get_all_products(db: Session = Depends(get_db)):
    try:
        all_products = db.query(Product).all()
        return all_products
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.get('/products/{id}')
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    try:
        item = db.query(Product).filter(Product.id == id).first()
        if item:
            return item
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    



@app.post('/products')
def add_product(product: PyProduct, db: Session = Depends(get_db)):
    try:
        db.add(db_models.Product(**product.model_dump()))
        db.commit()
        return {"product added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




@app.put('/products/{id}')
def update_product(id: int, product: PyProduct, db: Session = Depends(get_db)):
    try:
        old_product = db.query(Product).filter(Product.id == id).first()
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
        stale_product = db.query(Product).filter(Product.id == id).first()
        if stale_product:
            db.delete(stale_product)
            db.commit()
            return "Product deleted successfully"
        else:
            return "Product not found"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))





## Users Routes
@app.get("/users/", response_model=List[UserResponse])
def get_users(current_user:User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get all users"""
    try:
        return db.query(User).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user:User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get one user by ID"""
    try :
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, current_user:User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_pwd_hash(user.password)
        db_user = User(
            name = user.name,
            email = user.email,
            role = user.role,
            hashed_pwd = hashed_password
        )
        db.add(db_user)
        db.commit()
        return db_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate, current_user:User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Update a user"""
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.name = user.name
        db_user.email = user.email
        db_user.role = user.role
        
        db.commit()
        return {"message": "User Updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))





@app.delete("/users/{user_id}")
def delete_user(user_id: int, current_user:User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Delete a user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.id == current_user.id:
            raise HTTPException(status_code=404, detail="Don't Delete yourself!")

        db.delete(user)
        db.commit()
        return {"message": "User deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))