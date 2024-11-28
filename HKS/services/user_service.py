from HKS.data.databaseScript.models import UsersBase
from sqlalchemy.orm import Session

def register(db: Session, username: str, password: str, role: str) -> UsersBase:
    try:
        user = UsersBase(user_username=username, user_hashed_password=password, user_role=role)
        db.add(user)
        db.commit()
        db.refresh(user)  # Ensure the user object is refreshed and remains attached to the session
        return user
    except Exception as e:
        db.rollback()  # Rollback in case of error
        print(f"An error occurred: {e}")
        return None

def login(db: Session, username: str, password: str) -> UsersBase:
    try:
        user = db.query(UsersBase).filter_by(user_username=username, user_hashed_password=password).first()
        if user:
            if user.user_role == 'Company':
                return user
        else:
            print("Login failed! User not found.")
            print(f"Tried to login with username: {username}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None