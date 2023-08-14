import os
import json
import uuid
import redis
from base64 import encode
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, get_jwt

from models import db, Paste, Hash, User, Comment
from cutils import add_utc_time, is_expired, generate_short_url_hash

from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MIGRATIONS'] = False
app.config['DEBUG'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=10)

jwt = JWTManager(app)
db.init_app(app)

with app.app_context():
    db.create_all()

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container_name = "pastes"
blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str)
try:
    container_client = blob_service_client.get_container_client(container=container_name)
    container_client.get_container_properties()
except Exception as e:
    container_client = blob_service_client.create_container(container_name)


@app.post('/create_paste')
@jwt_required(optional=True)
def create_paste():
    username = get_jwt_identity()
    
    user = None
    
    if username:
        user = User.query.filter_by(username=username).first()
    
    jsonData = request.get_json()
    
    time_unit = jsonData.get('time_unit')
    time_value = jsonData.get('time_value')
    content = jsonData.get('content')
        
    new_paste = Paste(
        url_hash=generate_short_url_hash(str(uuid.uuid4())),
        blob_url='',
        created_at=datetime.utcnow(),
        expire_at=add_utc_time(
            datetime.utcnow(),
            time_unit=time_unit,
            time_value=time_value
        ),
        user_id=user.id if user else None)
    
    blob_name = f"{new_paste.url_hash}.txt"
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name)
    blob_client.upload_blob(content, content_settings=ContentSettings(
        content_type='text/plain'))

    new_paste.blob_url = blob_client.url
    db.session.add(new_paste)
    db.session.commit()
    
    return jsonify({'url_hash': new_paste.url_hash}), 201


@app.get('/<string:url_hash>')
def get_paste(url_hash):
    cache_json_data = redis_client.get(url_hash)
    if cache_json_data:
        cache_dict_data = json.loads(cache_json_data)
        if not is_expired(datetime.strptime(cache_dict_data['expire_at'], '%Y-%m-%d %H:%M:%S.%f')):
            return jsonify(cache_dict_data), 200
        else:
            return 'Paste is expired', 410
        
    paste = Paste.query.filter_by(url_hash=url_hash).first()
    
    if not paste:
        return 'Paste not found', 404
    if is_expired(paste.expire_at):
        return 'Paste is expired', 410
    
    blob_content = redis_client.get(paste.blob_url)
    if not blob_content:
        blob_client = BlobClient.from_blob_url(paste.blob_url)
        blob_content = blob_client.download_blob().readall().decode("utf-8")
        redis_client.setex(paste.blob_url, 360, blob_content)
    
    comments = Comment.query.filter_by(paste_id=paste.id).all()
    comments_list = []
    for comment in comments:
        comments_list.append({
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "username": User.query.filter_by(id=comment.user_id).first().username
        })
    
    user = User.query.filter_by(id=paste.user_id).first()
    username = 'anonymous' if user is None else user.username
    response_dict_data = {
        "id": paste.id,
        "url_hash": paste.url_hash,
        "created_at": str(paste.created_at),
        "expire_at": str(paste.expire_at),
        "username": username,
        "content": blob_content,
        "comments": comments_list
    }
    
    response_json_data = json.dumps(response_dict_data)
    redis_client.setex(paste.url_hash, 20, response_json_data)

    return jsonify(response_dict_data), 200


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

    return jsonify({'response': 'data received'}), 201


@app.post("/token")
def generate_token():
    username = request.json["username"]
    password = request.json["password"]
    
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    else:
        return jsonify({'response': 'incorrect username or password'}), 401
    
@app.post("/create_comment")
@jwt_required()
def create_comment():
    username = get_jwt_identity()
    content = request.json["content"]
    paste_id = request.json["paste_id"]
    expire_at = request.json["expire_at"]
    
    new_comment = Comment(
        content=content,
        created_at=datetime.utcnow(),
        expire_at=datetime.strptime(expire_at, '%Y-%m-%d %H:%M:%S.%f'),
        user_id=User.query.filter_by(username=username).first().id,
        paste_id=paste_id
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    return "", 200

@app.get("/get_my_pastes")
@jwt_required()
def get_my_pastes():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    pastes = Paste.query.filter_by(user_id=user.id).all()
    pastes_list = []

    for paste in pastes:
        content = read_txt(paste.blob_url)[:100]
        
        if not is_expired(paste.expire_at):
            
            pastes_list.append({
                "id": paste.id,
                "content": content,
                "created_at": paste.created_at,
                "expire_at": paste.expire_at,
                "url_hash": paste.url_hash,
            })
    
    return jsonify(dict(pastes=pastes_list)), 200

if __name__ == '__main__':
    app.run()