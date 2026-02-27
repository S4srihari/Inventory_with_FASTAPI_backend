from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_url =  "postgresql://postgres:srihari@localhost:5432/my_database"
engine = create_engine(db_url)
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
