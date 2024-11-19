import jwt
import datetime
from fastapi import HTTPException


SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
def create_jwt_token(user_id: int, username: str, user_role: int):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    token_data = {
        "sub": username,
        "user_id": user_id,
        "user_role": user_role,
        "exp": expiration
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "user_id": payload["user_id"],
            "username": payload["sub"],
            "user_role": payload["user_role"]
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")


def authenticate(authorization: str):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization token missing or invalid")
    token = authorization.split(" ")[1]
    return decode_jwt_token(token)
