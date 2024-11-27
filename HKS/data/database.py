from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from HKS.data.models import Base

DATABASE_URL = "postgresql+pg8000://postgres:Kristi2005@localhost:5432/postgres13"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()