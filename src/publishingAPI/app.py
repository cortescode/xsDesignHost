from flask import Flask, request
from flask_cors import CORS
from firebase_admin import credentials, initialize_app, auth
from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv

from werkzeug.utils import secure_filename

from websiteCreation import create_or_update_website

from validation import validate_credentials


# Initialize Firebase Admin SDK with service account credentials
cred = credentials.Certificate('../../service-account.json')
initialize_app(cred)

app = Flask(__name__)
CORS(app)


websites_path = "/var/www/"
zip_filename = 'zip-website'
max_file_size = 10 * 1024 * 1024


load_dotenv()

@app.post('/publish-website')
def publish_website():

    # Extracts user and website relevant data
    website_data = request.form
    id_token = website_data.get("user_token")
    website_id = website_data.get("website_id")

    # Validate if user is the owner of the website and can perform this action
    valid_user_access: bool = validate_credentials(id_token, website_id)

    # Check everything is correct before publishing the website
    if not valid_user_access:
        return 'Unauthorized access', 401
    

    local_path = websites_path + website_id
    zip_file = request.files.get(zip_filename)


    # Check if all required data is provided
    if not zip_file:
        return 'Incomplete data provided', 400


    # Validate zip file size and content type
    if zip_file.content_length > max_file_size:
        return 'File size exceeds limit', 400


    return create_or_update_website(local_path, zip_file)

    


if __name__ == "__main__":
    app.run()