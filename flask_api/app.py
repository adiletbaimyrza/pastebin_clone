import os
import redis
import uuid
import pickle
import json
from datetime import datetime
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from flask_serialize import FlaskSerialize
from cutils import add_utc_minutes, is_expired, generate_short_url_hash, create_paste, read_txt, set_to_cache, get_from_cache
from base64 import encode
# from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Load environment variables from .env file
load_dotenv()

# Create an extension
db = SQLAlchemy()
# Create an app
app = Flask(__name__)

# App configurations
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pastebin.db'
app.config['SQLALCHEMY_TRACK_MIGRATIONS'] = False
app.config['DEBUG'] = False

# Initialize the app with the extension
db.init_app(app)

# Create a flask-serialize mixin instance
fs_mixin = FlaskSerialize(db)

# Paste model


class Paste(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    hash = db.Column(db.String(8), unique=True)
    blob_url = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    expire_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.String(36), nullable=True, default=None)
    username = db.Column(db.String(20), nullable=True, default=None)
    views_count = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<Paste {self.id}>'


class Hash(db.Model, fs_mixin):
    url_hash = db.Column(db.String(8), primary_key=True)
    paste_id = db.Column(db.String(36), unique=True)

    def __repr__(self):
        return f'Hash {self.url_hash}'


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


@app.post('/post')
def post():
    # Create a Paste model instance from JSON
    new_paste = Paste(
        id=str(uuid.uuid4()),
        blob_url="",  # Initialize the blob_url, it will be set after blob upload
        created_at=datetime.utcnow(),
        expire_at=add_utc_minutes(
            datetime.utcnow(), minutes_to_add=request.json['minutes_to_live'])
    )

    # Add to the database
    db.session.add(new_paste)
    db.session.commit()

    safe_hash = None
    while safe_hash == None:
        not_safe_hash = generate_short_url_hash(new_paste.id)

        if not Hash.query.get(str(not_safe_hash)):
            safe_hash = not_safe_hash

    new_hash = Hash(
        url_hash=safe_hash,
        paste_id=new_paste.id
    )
    db.session.add(new_hash)

    blob_url = create_paste(f'{new_paste.id}.txt', request.json['content'])

    new_paste.blob_url = blob_url
    new_paste.hash = safe_hash
    db.session.commit()

    # Upload content to Azure Blob Storage
    # blob_name = f"{new_paste.id}.txt"
    # blob_client = blob_service_client.get_blob_client(
    # container=container_name, blob=blob_name)
    # blob_client.upload_blob(request.json['content'], content_settings=ContentSettings(
    # content_type='text/plain'))

    # Set the blob URL in the Paste model
    # new_paste.blob_url = blob_client.url
    # db.session.commit()

    # Return JSON of the created paste
    return jsonify({'hash': new_hash.url_hash}), 201


@app.get('/<string:url_hash>')
def get_paste(url_hash):
    cacheData = get_from_cache(redis_client, url_hash)
    if cacheData:
        if not is_expired(cacheData.expire_at):
            print("CacheData from Cache")
            return pickle.loads(cacheData)
        else:
            return 'Paste is expired', 410

    paste_id = get_from_cache(redis_client, url_hash)

    if not paste_id:
        hash_instance = Hash.query.get(url_hash)

        if not hash_instance:
            return 'Paste not found', 404

        paste_id = hash_instance.paste_id
        set_to_cache(redis_client, url_hash, paste_id)

    expire_at = get_from_cache(redis_client, paste_id)

    if expire_at:
        if is_expired(datetime.strptime(expire_at, '%Y-%m-%d %H:%M:%S.%f')):
            return 'Paste is expired', 410

    paste = Paste.query.get(paste_id)

    if is_expired(paste.expire_at):
        return 'Paste is expired', 410
    else:
        set_to_cache(redis_client, paste_id, str(paste.expire_at))

        blob_content = get_from_cache(redis_client, paste.blob_url)

        if not blob_content:
            blob_content = read_txt(paste.blob_url)
            set_to_cache(redis_client, paste.blob_url, blob_content)

        # i want you to store the jsonified data in pasteData, and store it in redis and before it look outs elsewhere i want you
        # to first look out in cache and check if data is in cache
        jsonData = {
            "hash": paste.hash,
            "created_at": paste.created_at,
            "expire_at": paste.expire_at,
            "user_id": 'anonymous' if paste.user_id == None else paste.user_id,
            "username": 'anonymous' if paste.username == None else paste.username,
            "views_count": paste.views_count,
            "content": blob_content}
        serialized_jsonData = pickle.dumps(jsonData)
        redis_client.setex(paste.hash, serialized_jsonData, 3600)
        print("cacheData set to Cache")
        return jsonify(jsonData), 200
        # Query the Paste model by ID using get()
        # Check if the paste exists in the database
        # If exists, check for expiration
        # Return 410 Gone status code if the Paste is expired
        # Fetch the content from Azure Blob Storage using the blob URL
        # blob_client = BlobClient.from_blob_url(paste.blob_url)
        # content = blob_client.download_blob().readall().decode("utf-8")
        # return jsonify({"id": paste.id, "content": content}), 200


if __name__ == '__main__':
    app.run()
