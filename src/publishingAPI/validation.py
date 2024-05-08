from pymongo import MongoClient
from pymongo.collection import Collection
from firebase_admin import auth
import os
from dotenv import load_dotenv


load_dotenv()

def validate_credentials(id_token: str, website_id) -> bool:
    """Check the user exists and is allowed to publish a website"""
    try:
        # Check if user exists in firebase
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # Check database to see if the request user is owner of the website

        client = MongoClient(os.getenv("MONGODB_URI"))
        db = client.get_database(os.getenv("DB_NAME"))
        websites_collection: Collection = db.get_collection("websites")
        
        website = websites_collection.find_one({
            "id": website_id,
            "user_uid": uid
        })


        if not website:
           return False

        return True
    
    except Exception as exception:
        return False
