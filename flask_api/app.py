import os
import json
import uuid
from base64 import encode
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, get_jwt

from models import db, Paste, Hash, User, Comment
from cutils import add_utc_time, is_expired, generate_short_url_hash, create_blob_paste, read_txt

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pastebin.db'
app.config['SQLALCHEMY_TRACK_MIGRATIONS'] = False
app.config['DEBUG'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=10)

jwt = JWTManager(app)
db.init_app(app)

with app.app_context():
    db.create_all()

def generate_hashes(quantity=1000):
    print(f'Generation of {quantity} hashes started.')
    
    for _ in range(quantity):
        random_hash = generate_short_url_hash(str(uuid.uuid4()))
        unique_hash = None
        while unique_hash is None:
            if not Hash.query.filter_by(url_hash=random_hash).first():
                unique_hash = random_hash
                new_hash_entry = Hash(url_hash=unique_hash)
                db.session.add(new_hash_entry)
            else:
                random_hash = generate_short_url_hash(str(uuid.uuid4()))
    
    db.session.commit()


def get_hash(when_quantity_lt=100) -> str:
    if Hash.query.count() < when_quantity_lt:
        generate_hashes()
    
    hash_record = Hash.query.first()
    db.session.delete(hash_record)
    db.session.commit()
    
    hash = hash_record.url_hash
    
    return hash


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
    
    new_hash = get_hash()
    
    new_paste = Paste(
        url_hash=new_hash,
        blob_url=create_blob_paste(f'{new_hash}.txt', content),
        created_at=datetime.utcnow(),
        expire_at=add_utc_time(
            datetime.utcnow(),
            time_unit=time_unit,
            time_value=time_value
        ),
        user_id=user.id if user else None)
    
    db.session.add(new_paste)
    db.session.commit()
    
    return jsonify({'url_hash': new_paste.url_hash}), 201


@app.get('/<string:url_hash>')
def get_paste(url_hash):
    paste = Paste.query.filter_by(url_hash=url_hash).first()
    
    if not paste:
        return 'Paste not found', 404
    if is_expired(paste.expire_at):
        return 'Paste is expired', 410
    
    blob_content = read_txt(paste.blob_url)
    
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

@app.get("/get_pastes")
@jwt_required()
def get_pastes():
    print(get_jwt()['exp'])
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
