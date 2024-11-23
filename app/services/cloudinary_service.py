import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
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