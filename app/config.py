import os
# app/config.py
DB_USER = "postgres"            # Your PostgreSQL username
DB_PASSWORD = "Kristi2005"      # Your PostgreSQL password
DB_ADDRESS = "localhost"        # Address, assuming local connection
DB_PORT = "5435"                # Port you mapped in Docker
DB_NAME = "postgres"            # Database name

# # JWT
# SECRET_KEY = os.getenv('SECRET_KEY')
# ALGORITHM = os.getenv('ALGORITHM')
# ACCESS_TOKEN_EXPIRE_MINUTES= int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))