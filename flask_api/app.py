from cutils import add_utc_minutes, is_expired
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_serialize import FlaskSerialize
import uuid
from datetime import datetime
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
from dotenv import load_dotenv

load_dotenv()

# create an extension
db = SQLAlchemy()
# create an app
app = Flask(__name__)

# app configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pastes.db'
app.config['SQLALCHEMY_TRACK_MIGRATIONS'] = False
app.config['DEBUG'] = False

# initialize the app with the extension
db.init_app(app)

# create a flask-serialize mixin instance
fs_mixin = FlaskSerialize(db)

# Paste model


class Paste(db.Model, fs_mixin):
    id = db.Column(db.String(36), primary_key=True)
    # Store the Azure Blob URL instead of the content
    blob_url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    expire_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Paste {self.id}>'


# create a database before app runs
with app.app_context():
    db.create_all()

# retrieve the connection string from the environment variable
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
# container name in which pastes will be stored in the storage account
container_name = "pastes"

# create a blob service client to interact with the storage account
blob_service_client = BlobServiceClient.from_connection_string(
    conn_str=connect_str)
try:
    # get container client to interact with the container in which pastes will be stored
    container_client = blob_service_client.get_container_client(
        container=container_name)
    # get properties of the container to force an exception to be thrown if the container does not exist
    container_client.get_container_properties()
except Exception as e:
    # create a container in the storage account if it does not exist
    container_client = blob_service_client.create_container(container_name)


@app.post('/post')
def post():
    # create a Paste model instance from json
    new_paste = Paste(
        id=str(uuid.uuid4()),
        blob_url="",  # Initialize the blob_url, it will be set after blob upload
        created_at=datetime.utcnow(),
        expire_at=add_utc_minutes(datetime.utcnow(), minutes_to_add=request.json['minutes_to_live']))

    # add to the database
    db.session.add(new_paste)
    db.session.commit()

    # Upload content to Azure Blob Storage
    blob_name = f"{new_paste.id}.txt"
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name)
    blob_client.upload_blob(request.json['content'], content_settings=ContentSettings(
        content_type='text/plain'))

    # Set the blob URL in the Paste model
    new_paste.blob_url = blob_client.url
    db.session.commit()

    # return JSON of the created paste
    return Paste.fs_get_delete_put_post(new_paste.id), 201


@app.get('/get/<uuid:id>')
def get_paste(id):
    # query the Paste model by id using get()
    paste = Paste.query.get(str(id))

    # check if the paste exists in the database
    if paste:
        # if exists, check for expiration
        if is_expired(paste.expire_at):
            # return 410 Gone status code if the Paste is expired
            return 'Paste is expired', 410
        else:
            # Fetch the content from Azure Blob Storage using the blob URL
            blob_client = BlobClient.from_blob_url(paste.blob_url)
            content = blob_client.download_blob().readall().decode("utf-8")
            return jsonify({"id": paste.id, "content": content}), 200
    else:
        # return 404 Not Found status code if paste not found
        return 'Paste not found', 404


if __name__ == '__main__':
    app.run()
