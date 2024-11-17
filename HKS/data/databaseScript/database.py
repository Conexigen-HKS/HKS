import os
import uuid

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from HKS.data.databaseScript.models import Base
from HKS.data.databaseScript.models import Companies
# Load environment variables
load_dotenv()

# Get database credentials from environment variables
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
address = os.getenv('DB_ADDRESS')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')

# Create database URL
database_url = f"postgresql+psycopg2://{username}:{password}@{address}:{port}/{database}"
# Create SQLAlchemy engine
engine = create_engine(database_url, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()