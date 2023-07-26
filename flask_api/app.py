import os
import uuid
import redis
from datetime import datetime
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from flask_serialize import FlaskSerialize
from cutils import add_utc_minutes, is_expired, generate_short_url_hash, create_paste, read_txt
# from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings

redisClient = redis.Redis(host='localhost', port=6379, decode_responses=True)

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


class Paste(db.Model, fs_mixin):
    id = db.Column(db.String(36), primary_key=True)
    blob_url = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    expire_at = db.Column(db.DateTime, nullable=False)

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
        expire_at=add_utc_minutes(datetime.utcnow(), minutes_to_add=request.json['minutes_to_live']))

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


@app.get('/get/<string:hash>')
def get_paste(hash):
    # Query the Hash model by hash using get()
    id = ''
    if redisClient.get(hash):
        print('cached')
        return jsonify(dict(content=redisClient.get(hash)))
    else:
        hash_obj = Hash.query.get(hash)
        if hash_obj:
            id = hash_obj.paste_id

        # Query the Paste model by ID using get()
        paste = Paste.query.get(str(id))

        # Check if the paste exists in the database
        if paste:
            # If exists, check for expiration
            if is_expired(paste.expire_at):
                # Return 410 Gone status code if the Paste is expired
                return 'Paste is expired', 410
            else:
                # Fetch the content from Azure Blob Storage using the blob URL
                # blob_client = BlobClient.from_blob_url(paste.blob_url)
                # content = blob_client.download_blob().readall().decode("utf-8")
                # return jsonify({"id": paste.id, "content": content}), 200
                content = read_txt(paste.blob_url)

                redisClient.setex(hash, 5, content)
                print('not cached')
                return jsonify({
                    "content": content
                }), 200
        else:
            # Return 404 Not Found status code if paste not found
            return 'Paste not found', 404


if __name__ == '__main__':
    app.run()
