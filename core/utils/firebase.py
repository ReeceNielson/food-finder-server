import firebase_admin.messaging
import os
import firebase_admin
from dotenv import load_dotenv

load_dotenv()

private_key_id = os.getenv("PRIVATE_KEY_ID")
private_key = os.getenv("PRIVATE_KEY")

print(private_key)

default_app = firebase_admin.initialize_app(
    credential=firebase_admin.credentials.Certificate({
        "type": "service_account",
        "project_id": "food-finder-71e84",
        "private_key_id": private_key_id,
        "private_key": private_key.replace("\\n", "\n") if private_key else None,
        "client_email": "firebase-adminsdk-fbsvc@food-finder-71e84.iam.gserviceaccount.com",
        "client_id": "116749105601005127841",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40food-finder-71e84.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    })
)

if __name__ == "__main__":
    print("Sending message...")
    message = firebase_admin.messaging.Message(
        notification=firebase_admin.messaging.Notification(
            title="Test Notification",
            body="This is a test notification",
        ),
        data={
            'score': '850',
            'time': '2:45',
        },
        token="cls_xEbkfsA1umvEbTuOiZ:APA91bFiMGjkdDqzd_2VaAP9WGWaA7hz0k2gokm22AW3XOlC5bwyX_DVleab5idlJ-i8xxqKgye2WE3fS3KMAxHoFJSDcZEwunp9MdNM3LRNLtUhxgwiJc4",
    )
    response = firebase_admin.messaging.send(message)
    print(response)
    