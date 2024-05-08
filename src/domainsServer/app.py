from flask import Flask, send_from_directory, request
from flask_cors import CORS
import os
import zipfile
from firebase_admin import credentials, initialize_app, auth
from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv

from werkzeug.utils import secure_filename


app = Flask(__name__)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static_website(path):
    # Get the domain from the request's Host header
    domain = request.headers.get("Host").split(":")[0]

    # Were websites are saved
    base_folder = "/var/www/"

    # Look up the directory corresponding to the domain
    website_id = get_website_id(domain)
    
    website_dir = base_folder + website_id


    if website_dir:
        # If no path is provided, serve index.html by default
        if not path:
            path = "home.html"

        print("path: ", path)
        # Serve the requested file from the corresponding directory
        return send_from_directory(website_dir, path)

    # If the domain is not found in the mapping, return a 404 error
    return "404 Not Found", 404


def get_website_id(domain: str):

    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client.get_database(os.getenv("DB_NAME"))
    websites_collection: Collection = db.get_collection("websites")
        
    website = websites_collection.find_one({
        "config.domains": {
            "name":domain
        },
    })

    id = website.get("id")

    return id


if __name__ == "__main__":
    app.run(debug=True)
