import os

from dotenv import load_dotenv
from mailjet_rest import Client

from app.config import MJ_APIKEY_PRIVATE, MJ_APIKEY_PUBLIC

load_dotenv()

api_key = os.getenv('MJ_APIKEY_PUBLIC')
api_secret = os.getenv('MJ_APIKEY_PRIVATE')
mailjet = Client(auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_PRIVATE), version='v3.1')

def send_email(to_email: str, to_name: str, subject: str, text_content: str, html_content: str):
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "kristinkaa891@gmail.com",  # Replace with your sender email
                    "Name": "Conexigen team"
                },
                "To": [
                    {
                        "Email": to_email,
                        "Name": to_name
                    }
                ],
                "Subject": subject,
                "TextPart": text_content,
                "HTMLPart": html_content
            }
        ]
    }
    result = mailjet.send.create(data=data)
    return result.status_code, result.json()

# def notify_user_registration(user_email: str, user_name: str):
#     variables = {
#         "subject": "Welcome to Our Service",
#         "text_part": f"Hello {user_name}, welcome to our platform!",
#         "html_part": f"<h3>Hello {user_name},</h3><p>Welcome to our platform!</p>"
#     }
#     status, response = send_templated_email(user_email, user_name, variables)
#     if status == 200:
#         print("Email sent successfully.")
#     else:
#         print(f"Failed to send email: {response}")