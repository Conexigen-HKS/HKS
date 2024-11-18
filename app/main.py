import os
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.data.database import Base
from app.routers.employer import users_router

app = FastAPI()

# Database connection
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Kristi2005")
DB_ADDRESS = os.getenv("DB_ADDRESS", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize Database
@app.on_event("startup")
def startup():
    try:
        with engine.connect() as connection:
            print("Connection to the database was successful.")
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("Error connecting to the database:", e)

# Include router
app.include_router(users_router)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
