import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from app.data.models import Professional, User
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('API_KEY'),
    api_secret=os.getenv('API_SECRET'),
    secure=True
)

def upload_image_to_cloudinary(image_file, public_id=None, folder="uploads"):
    return cloudinary.uploader.upload(image_file, public_id=public_id, folder=folder)

def generate_optimized_url(public_id):
    url, _ = cloudinary_url(public_id, fetch_format="auto", quality="auto")
    return url

def generate_auto_crop_url(public_id, width=500, height=500):
    url, _ = cloudinary_url(public_id, width=width, height=height, crop="auto", gravity="auto")
    return url

def delete_picture(current_user: User, db: Session):
    user = db.query(Professional).filter(Professional.user_id == current_user.id).first()
    user_pic = user.picture
    if user_pic:
        cloudinary.uploader.destroy(user_pic)

        user.picture = None
        db.commit()
        db.refresh(user)

        return {"message": "Picture deleted successfully"}
    else:
        return {"message": "No picture to be deleted."}

