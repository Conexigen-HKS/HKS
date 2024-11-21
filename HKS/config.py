import os

# JWT Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')  # Replace with a secure default or ensure it's set
ALGORITHM = os.getenv('ALGORITHM', 'HS256')  # Default to a commonly used algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))  # Default to 30 minutes
