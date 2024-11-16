from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.models import Base
from app.config import DB_USER, DB_PASSWORD, DB_ADDRESS, DB_PORT, DB_NAME


database_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}:{DB_PORT}/{DB_NAME}"
engine = create_engine(database_url, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()