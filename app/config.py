import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_ADDRESS = os.getenv("DB_ADDRESS")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")

# JWT
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES= int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

#CLOUDINARY
CLOUD_NAME = os.getenv('CLOUD_NAME') 
API_KEY = os.getenv('API_KEY') 
API_SECRET = os.getenv('API_SECRET')
CLOUDINARY_URL= os.getenv('CLOUDINARY_URL')