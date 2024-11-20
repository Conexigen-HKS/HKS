from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.models import Base
from config import DB_USER, DB_PASSWORD, DB_ADDRESS, DB_PORT, DB_NAME


DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()