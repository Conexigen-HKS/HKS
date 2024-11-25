# from mailjet_rest import Client
# from config import MJ_APIKEY_PRIVATE, MJ_APIKEY_PUBLIC

# api_key = MJ_APIKEY_PUBLIC
# api_secret = MJ_APIKEY_PRIVATE

# mailjet = Client(auth=(api_key, api_secret))
# data = {
# 	'FromEmail': '$SENDER_EMAIL',
# 	'FromName': '$SENDER_NAME',
# 	'Subject': 'Your email flight plan!',
# 	'Text-part': 'Dear passenger, welcome to Mailjet! May the delivery force be with you!',
# 	'Html-part': '<h3>Dear passenger, welcome to <a href=\"https://www.mailjet.com/\">Mailjet</a>!<br />May the delivery force be with you!',
# 	'Recipients': [{'Email': '$RECIPIENT_EMAIL'}]
# }
# result = mailjet.send.create(data=data)
# print(result.status_code)
# print(result.json())

# #mailjet = Client(auth=(api_key, api_secret),api_url="https://api.us.mailjet.com/")

# # """
# # Run:
# # """
# # from mailjet_rest import Client
# # import os
# # api_key = os.environ['MJ_APIKEY_PUBLIC']
# # api_secret = os.environ['MJ_APIKEY_PRIVATE']
# # mailjet = Client(auth=(api_key, api_secret), version='v3.1')
# # data = {
# #   'Messages': [
# # 				{
# # 						"From": {
# # 								"Email": "$SENDER_EMAIL",
# # 								"Name": "Me"
# # 						},
# # 						"To": [
# # 								{
# # 										"Email": "$RECIPIENT_EMAIL",
# # 										"Name": "You"
# # 								}
# # 						],
# # 						"Subject": "My first Mailjet Email!",
# # 						"TextPart": "Greetings from Mailjet!",
# # 						"HTMLPart": "<h3>Dear passenger 1, welcome to <a href=\"https://www.mailjet.com/\">Mailjet</a>!</h3><br />May the delivery force be with you!"
# # 				}
# # 		]
# # }
# # result = mailjet.send.create(data=data)
# # print result.status_code
# # print result.json()


# Retrieve sent messages
# """
# Run :
# """
# from mailjet_rest import Client
# import os
# api_key = os.environ['MJ_APIKEY_PUBLIC']
# api_secret = os.environ['MJ_APIKEY_PRIVATE']
# mailjet = Client(auth=(api_key, api_secret))
# id = '$MESSAGE_ID'
# result = mailjet.message.get(id=id)
# print result.status_code
# print result.json()

# api response -
# {
#   "Count": "1",
#   "Data": [
#     {
#       "ArrivedAt": "2018-01-01T00:00:00",
#       "AttachmentCount": "1",
#       "AttemptCount": "1",
#       "CampaignID": "123456789",
#       "ContactAlt": "",
#       "ContactID": "987654",
#       "FilterTime": "111",
#       "ID": "1234567890987654321",
#       "Status": "clicked",
#       "Subject": "",
#       "UUID": "1ab23cd4-e567-8901-2345-6789f0gh1i2j"
#       "........................."
#     }
#   ],
#   "Total": "1"
# }