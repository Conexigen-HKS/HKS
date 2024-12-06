import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the .env file
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Load the .env file
load_dotenv(dotenv_path=ENV_PATH)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_ADDRESS = os.getenv("DB_ADDRESS")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")

# JWT
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
#ACCESS_TOKEN_EXPIRE_MINUTES= int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

#CLOUDINARY
CLOUD_NAME = os.getenv('CLOUD_NAME')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
# CLOUDINARY_URL= os.getenv('CLOUDINARY_URL')
#
# #MAILJET
MJ_APIKEY_PUBLIC= os.getenv('MJ_APIKEY_PUBLIC')
MJ_APIKEY_PRIVATE= os.getenv('MJ_APIKEY_PRIVATE')
MJ_TEMPLATE_ID= os.getenv('MJ_TEMPLATE_ID')
