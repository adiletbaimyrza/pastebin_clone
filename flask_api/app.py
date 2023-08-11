import os
import json
import uuid
from base64 import encode
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

from models import db, Paste, Hash, User, Comment
from cutils import add_utc_minutes, is_expired, generate_short_url_hash, create_blob_paste, read_txt

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pastebin.db'
app.config['SQLALCHEMY_TRACK_MIGRATIONS'] = False
app.config['DEBUG'] = False

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
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
    minutes_to_live = jsonData.get('minutes_to_live')
    content = jsonData.get('content')

    new_paste = Paste(
        hash=get_hash(),
        created_at=datetime.utcnow(),
        expire_at=add_utc_minutes(datetime.utcnow(), minutes_to_live),
        username=user.username if user else "anonymous",
        user_id=user.id if user else None
    )
    
    blob_url = create_blob_paste(f'{new_paste.hash}.txt', content)
    new_paste.blob_url = blob_url

    db.session.add(new_paste)
    db.session.commit()

    return jsonify({'hash': new_paste.hash}), 201


@app.get('/<string:url_hash>')
def get_paste(url_hash):
    paste_instance = Paste.query.filter_by(hash=url_hash).first()

    if not paste_instance:
        print("Requested paste not found.")
        return 'Paste not found', 404

    if is_expired(paste_instance.expire_at):
        print("Requested paste has expired.")
        return 'Paste is expired', 410

    blob_content = read_txt(paste_instance.blob_url)

    comments = Comment.query.filter_by(paste_id=paste_instance.id).all()
    comments_list = []
    for comment in comments:
        comments_list.append({
            "id": comment.id,
            "created_at": comment.created_at,
            "comment": comment.content,
            "user_id": comment.user_id
            # Add other comment attributes here
        })

    response_dict_data = {
        "id": paste_instance.id,
        "hash": paste_instance.hash,
        "created_at": str(paste_instance.created_at),
        "expire_at": str(paste_instance.expire_at),
        "username": paste_instance.username,
        "content": blob_content,
        "comments": comments_list  # Include the list of comments
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
    comment = request.json["comment"]
    paste_id = request.json["paste_id"]
    
    new_comment = Comment(
        content=comment,
        created_at=datetime.utcnow(),
        
        user_id=User.query.filter_by(username=username).first().id,
        paste_id=paste_id
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    return "", 200

if __name__ == '__main__':
    app.run()
