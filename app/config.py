import os

DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Kristi2005')
DB_ADDRESS = os.getenv('DB_ADDRESS', '192.168.1.7')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'postgres')

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}:{DB_PORT}/{DB_NAME}"

# # JWT
# SECRET_KEY = os.getenv('SECRET_KEY')
# ALGORITHM = os.getenv('ALGORITHM')
# ACCESS_TOKEN_EXPIRE_MINUTES= int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))