from flask import Flask, request
from flask_cors import CORS
import os
import zipfile
from firebase_admin import credentials, initialize_app, auth
from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv


# Initialize Firebase Admin SDK with service account credentials
cred = credentials.Certificate('./service-account.json')
initialize_app(cred)

app = Flask(__name__)
CORS(app)


websites_path = "/var/www/"
zip_filename = 'zip-website'


load_dotenv()

@app.post('/publish-website')
def publish_website():

    # Extracts user and website relevant data
    website_data = request.form
    id_token = website_data.get("user_token")
    website_id = website_data.get("website_id")
    local_path = websites_path + website_id
    zip_file = request.files.get(zip_filename)


    # Validate if user is the owner of the website and can perform this action
    valid_user_access: bool = validate_credentials(id_token, website_id)

    # Check everything is correct before publishing the website
    if not website_id:
        return 'The required data is not completed', 400
    if not valid_user_access:
        return 'You are not allowed to do this', 400
    if not zip_file:
        return 'Website files not found', 400
    if zip_file.filename == '':
        return 'Website file zip incorrect', 400
    

    create_or_update_website(local_path, zip_file)


    return 'Website published successfully', 200



def create_or_update_website(local_path, zip_file):
    
    # Create website path if not exists
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    # Save the uploaded file to a temporary location
    file_path = 'temp.zip'
    zip_file.save(file_path)
        
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        # Iterate throughout zip file to check if 
        # the zip contains only .css and .html files

        file_list = zip_ref.namelist()
        
        for file_name in file_list:
            if not file_name.endswith('.css') and not file_name.endswith('.html'):
                return 'The zip file should only contain .css and .html files.', 400

        
        # Extract all the contents to a directory once files checked
        zip_ref.extractall(local_path)
    
    # Remove the temporary zip file
    os.remove(file_path)



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
        
        website = websites_collection.find({
            "user_uid": uid,
            "id": website_id
        })

        if not website:
           return False

        return True
    except Exception as exception:
        return False

    


if __name__ == "__main__":
    app.run()