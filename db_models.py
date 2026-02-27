from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "product"
    id=Column(Integer, primary_key=True, index=True)
    item=Column(String, nullable=False)
    description=Column(String, nullable=False)
    price=Column(Float, nullable=False)
    quantity=Column(Integer, nullable=False) 

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    hashed_pwd = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
