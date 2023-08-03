import os
import json
import uuid
import redis
from base64 import encode
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, request

from models import db, Paste, Hash
from cutils import add_utc_minutes, is_expired, generate_short_url_hash, create_blob_paste, read_txt


# from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Load environment variables from .env file
load_dotenv()


# Create an app
app = Flask(__name__)

# App configurations
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pastebin.db'
app.config['SQLALCHEMY_TRACK_MIGRATIONS'] = False
app.config['DEBUG'] = False

# Initialize the app with the extension
db.init_app(app)

# Create a database before the app runs
with app.app_context():
    db.create_all()

# Retrieve the connection string from the environment variable
# connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
# Container name in which pastes will be stored in the storage account
# container_name = "pastes"

# Create a blob service client to interact with the storage account
# blob_service_client = BlobServiceClient.from_connection_string(
    # conn_str=connect_str)
# try:
    # Get container client to interact with the container in which pastes will be stored
    # container_client = blob_service_client.get_container_client(
    # container=container_name)
    # Get properties of the container to force an exception to be thrown if the container does not exist
    # container_client.get_container_properties()
# except Exception as e:
    # Create a container in the storage account if it does not exist
    # container_client = blob_service_client.create_container(container_name)


def generate_10k_hashes():
    for _ in range(10000):
        random_hash = generate_short_url_hash(str(uuid.uuid4()))
        unique_hash = None
        while unique_hash is None:
            if not Hash.query.filter_by(url_hash=random_hash):
                unique_hash = random_hash
                new_hash_entry = Hash(url_hash=unique_hash)
                db.session.add(new_hash_entry)
    db.session.commit()
    
def get_hash() -> str:
    if Hash.query.count() < 1000:
        generate_10k_hashes()
    
    hash_record = Hash.query.first()
    db.session.delete(hash_record)
    db.session.commit()
    
    hash = hash_record.url_hash
    
    return hash



@app.post('/post')
def post():
    new_paste = Paste(
        hash=get_hash(),
        created_at=datetime.utcnow(),
        expire_at=add_utc_minutes(
            datetime.utcnow(),
            minutes_to_add=request.json['minutes_to_live']),
        user_id=None
    )
    blob_url = create_blob_paste(f'{new_paste.id}.txt', request.json['content'])
    new_paste.blob_url = blob_url
    
    db.session.commit()

    # Upload content to Azure Blob Storage
    # blob_name = f"{new_paste.id}.txt"
    # blob_client = blob_service_client.get_blob_client(
    # container=container_name, blob=blob_name)
    # blob_client.upload_blob(request.json['content'], content_settings=ContentSettings(
    # content_type='text/plain'))

    return jsonify({'hash': new_paste.hash}), 201


@app.get('/<string:url_hash>')
def get_paste(url_hash):
    cache_json_data = redis_client.get(url_hash)
    if cache_json_data:
        cache_dict_data = json.loads(cache_json_data)

        if not is_expired(datetime.strptime(cache_dict_data['expire_at'], '%Y-%m-%d %H:%M:%S.%f')):
            print("cache_data from Cache")
            return jsonify(cache_dict_data), 200
        else:
            return 'Paste is expired', 410

    paste_instance = Paste.query.filter_by(hash=url_hash).first()

    if not paste_instance:
        return 'Paste not found', 404

    if is_expired(paste_instance.expire_at):
        return 'Paste is expired', 410
    else:
        blob_content = redis_client.get(paste_instance.blob_url)

        if not blob_content:
            blob_content = read_txt(paste_instance.blob_url)
            redis_client.setex(paste_instance.blob_url, 20, blob_content)

        response_dict_data = {
            "hash": paste_instance.hash,
            "created_at": str(paste_instance.created_at),
            "expire_at": str(paste_instance.expire_at),
            "user_id": 'anonymous' if paste_instance.user_id is None else paste_instance.user_id,
            "username": 'anonymous' if paste_instance.username is None else paste_instance.username,
            "views_count": paste_instance.views_count,
            "content": blob_content}

        response_json_data = json.dumps(response_dict_data)
        redis_client.setex(paste_instance.hash, 3600, response_json_data)
        print("response_json_data set to Cache")
        return jsonify(json.loads(response_json_data)), 200
        # Query the Paste model by ID using get()
        # Check if the paste exists in the database
        # If exists, check for expiration
        # Return 410 Gone status code if the Paste is expired
        # Fetch the content from Azure Blob Storage using the blob URL
        # blob_client = BlobClient.from_blob_url(paste.blob_url)
        # content = blob_client.download_blob().readall().decode("utf-8")
        # return jsonify({"id": paste.id, "content": content}), 200


@app.post("/register")
def register():
    print(request.json["username"])
    print(request.json["email"])
    print(request.json["password"])
    
    return jsonify({'response': 'data received'}), 201

@app.post("/login")
def login():
    print(request.json["username"])
    print(request.json["password"])
    
    return jsonify({'response': 'data received'}), 200
if __name__ == '__main__':
    app.run()
