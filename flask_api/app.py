import os
import json
import uuid
import redis
from base64 import encode
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

from models import db, Paste, Hash, User, Comment
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

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

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


def generate_10_hashes():
    print("Generating 10 hashes...")
    for _ in range(10):
        random_hash = generate_short_url_hash(str(uuid.uuid4()))
        print(f"Generated random hash: {random_hash}")
        unique_hash = None
        while unique_hash is None:
            if not Hash.query.filter_by(url_hash=random_hash).first():
                unique_hash = random_hash
                new_hash_entry = Hash(url_hash=unique_hash)
                db.session.add(new_hash_entry)
                print(f"Added new hash entry: {unique_hash}")
            else:
                random_hash = generate_short_url_hash(str(uuid.uuid4()))
                print(f"Collision detected. Regenerating hash: {random_hash}")

    db.session.commit()
    print("Committed changes to the database.")


def get_hash() -> str:
    print("Checking for existing hashes...")
    if Hash.query.count() < 2:
        print("No hashes found. Generating new ones...")
        generate_10_hashes()

    hash_record = Hash.query.first()
    db.session.delete(hash_record)
    db.session.commit()

    hash = hash_record.url_hash
    print(f"Selected hash for the paste: {hash}")

    return hash


@app.post('/create_paste')
@jwt_required()
def create_paste():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    user_id = None
    
    if user is None:
        username = None
        user_id = None
    else:
        username = user.username
        user_id = user.id
    
    new_paste = Paste(
        hash=get_hash(),
        created_at=datetime.utcnow(),
        expire_at=add_utc_minutes(
            datetime.utcnow(),
            minutes_to_add=request.json['minutes_to_live']),
        user_id=user_id,
        username = username
    )
    
    blob_url = create_blob_paste(f'{new_paste.hash}.txt', request.json['content'])
    new_paste.blob_url = blob_url

    db.session.add(new_paste)
    db.session.commit()

    # blob_name = f"{new_paste.id}.txt"
    # blob_client = blob_service_client.get_blob_client(
    # container=container_name, blob=blob_name)
    # blob_client.upload_blob(request.json['content'], content_settings=ContentSettings(
    # content_type='text/plain'))

    return jsonify({'hash': new_paste.hash}), 201


@app.get('/<string:url_hash>')
def get_paste(url_hash):
    print(f"Received a GET request for hash: {url_hash}")
    cache_json_data = redis_client.get(url_hash)
    if cache_json_data:
        cache_dict_data = json.loads(cache_json_data)

        if not is_expired(datetime.strptime(cache_dict_data['expire_at'], '%Y-%m-%d %H:%M:%S.%f')):
            print("Cache hit. Retrieved data from Cache.")
            return jsonify(cache_dict_data), 200
        else:
            print("Cache expired. The paste is no longer available.")
            return 'Paste is expired', 410

    paste_instance = Paste.query.filter_by(hash=url_hash).first()

    if not paste_instance:
        print("Requested paste not found.")
        return 'Paste not found', 404

    if is_expired(paste_instance.expire_at):
        print("Requested paste has expired.")
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
            "username": paste_instance.username,
            "content": blob_content}

        response_json_data = json.dumps(response_dict_data)
        redis_client.setex(paste_instance.hash, 3600, response_json_data)
        print("Data set to Cache.")
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
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]
    
    if User.query.filter_by(email=email).first():
        return jsonify({'response': 'email already registered'}), 401
    if User.query.filter_by(username=username).first():
        return jsonify({'response': 'username is taken'}), 401
    
    new_user = User(
        email = email,
        username = username, 
        password = password
    )
    
    db.session.add(new_user)
    db.session.commit()
    print("user created!")

    return jsonify({'response': 'data received'}), 201


@app.post("/token")
def generate_token():
    username = request.json["username"]
    password = request.json["password"]
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'response': 'no such username'}), 401
    else:
        if user.password == password:
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token)
        else:
            return jsonify({'response': 'password incorrect'}), 401


    
            
@app.get("/protected")
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


if __name__ == '__main__':
    app.run()
