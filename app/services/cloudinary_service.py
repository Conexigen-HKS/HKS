"""
Cloudinary service module
In this file, we define the cloudinary service module.
This module contains helper functions for uploading and deleting images from Cloudinary.
Functions:
- upload_image_to_cloudinary: This function uploads an image to Cloudinary.
- generate_optimized_url: This function generates an optimized image URL.
- generate_auto_crop_url: This function generates an auto-cropped image URL.
- delete_picture: This function deletes a picture from Cloudinary.
- update_user_picture: This function updates a user's picture in the database.
- change_picture: This function changes a user's picture.
"""

import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from fastapi import File, UploadFile

from app.data.models import Companies, Professional, User


load_dotenv()

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True,
)


def upload_image_to_cloudinary(image_file, public_id=None, folder="uploads"):
    """
    Upload an image to Cloudinary
    :param image_file: The image file to upload
    :param public_id: The public ID of the image
    :param folder: The folder to upload the image to
    :return: The upload result
    """
    return cloudinary.uploader.upload(image_file, public_id=public_id, folder=folder)


def generate_optimized_url(public_id):
    """
    Generate an optimized image URL
    :param public_id: The public ID of the image
    :return: The optimized image URL
    """
    url, _ = cloudinary_url(public_id, fetch_format="auto", quality="auto")
    return url


def generate_auto_crop_url(public_id, width=500, height=500):
    """
    Generate an auto-cropped image URL
    :param public_id: The public ID of the image
    :param width: The width of the image
    :param height: The height of the image
    :return: The auto-cropped image URL
    """
    url, _ = cloudinary_url(
        public_id, width=width, height=height, crop="auto", gravity="auto"
    )
    return url


def delete_picture(current_user: User, db: Session):
    """
    Delete a picture from Cloudinary
    :param current_user: The current user
    :param db: The database session
    :return: The deletion message
    """
    if current_user.role == "professional":
        user = (
            db.query(Professional)
            .filter(Professional.user_id == current_user.id)
            .first()
        )
        user_pic = user.picture
        if user_pic:
            cloudinary.uploader.destroy(user_pic)

            user.picture = None
            db.commit()
            db.refresh(user)
            return {"message": "Picture deleted successfully"}

    elif current_user.role == "company":
        company = (
            db.query(Companies).filter(Companies.user_id == current_user.id).first()
        )
        company_pic = company.picture
        if company_pic:
            cloudinary.uploader.destroy(company_pic)

            company.picture = None
            db.commit()
            db.refresh(company)
            return {"message": "Picture deleted successfully"}
    else:
        return {"message": "No picture to be deleted."}


def update_user_picture(user_instance, file, db):
    """
    Update a user's picture in the database
    :param user_instance: The user instance
    :param file: The image file
    :param db: The database session
    :return: The file URL
    """
    if user_instance.picture:
        cloudinary.uploader.destroy(user_instance.picture)
    upload_result = upload_image_to_cloudinary(file.file)
    file_url = upload_result["secure_url"]
    user_instance.picture = file_url
    db.commit()
    return file_url


def change_picture(current_user: User, db: Session, file: UploadFile = File(...)):
    """
    Change a user's picture
    :param current_user: The current
    :param db: The database session
    :param file: The image file
    :return: The picture change result
    """
    if current_user.role == "company":
        company_user = (
            db.query(Companies).filter(Companies.user_id == current_user.id).first()
        )
        file_url = update_user_picture(company_user, file, db)
    elif current_user.role == "professional":
        prof_user = (
            db.query(Professional)
            .filter(Professional.user_id == current_user.id)
            .first()
        )
        file_url = update_user_picture(prof_user, file, db)
    else:
        return {"error": "Invalid user role"}

    return {
        "message": "Picture changed successfully",
        "picture_url": file_url,
    }
