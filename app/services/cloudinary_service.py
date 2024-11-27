import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from fastapi import File, UploadFile
from data.models import Companies, Professional, User
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

load_dotenv()

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

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

#da dobavq i za companies.
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
    
def update_user_picture(user_instance, file, db):
    if user_instance.picture:
        cloudinary.uploader.destroy(user_instance.picture)
    upload_result = upload_image_to_cloudinary(file.file)
    file_url = upload_result["secure_url"]
    user_instance.picture = file_url
    db.commit()
    return file_url

def change_picture(current_user: User, db: Session, file: UploadFile = File(...)):
    if current_user.role == 'company':
        company_user = db.query(Companies).filter(Companies.user_id == current_user.id).first()
        file_url = update_user_picture(company_user, file, db)
    elif current_user.role == 'professional':
        prof_user = db.query(Professional).filter(Professional.user_id == current_user.id).first()
        file_url = update_user_picture(prof_user, file, db)
    else:
        return {"error": "Invalid user role"}

    return {
        "message": "Picture changed successfully",
        "picture_url": file_url,
    }



   

