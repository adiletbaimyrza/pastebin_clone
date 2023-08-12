from flask_sqlalchemy import SQLAlchemy
from flask_serialize import FlaskSerialize

db = SQLAlchemy()
fs_mixin = FlaskSerialize(db)

class User(db.Model, fs_mixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)    # email max 100 chars
    username = db.Column(db.String(50), unique=True, nullable=False)  # username max 50 chars
    password = db.Column(db.String(87), nullable=False)               # encrypted password max 87 chars
    comments = db.relationship('Comment', backref='user')
    pastes = db.relationship('Paste', backref='user')


class Paste(db.Model, fs_mixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url_hash = db.Column(db.String(8), unique=True, nullable=False)          # url_hash max 8 chars
    blob_url = db.Column(db.String(256), unique=True, nullable=False)        # blob_url max 256 chars
    created_at = db.Column(db.DateTime, nullable=False)
    expire_at = db.Column(db.DateTime, nullable=True)
    delete_upon_seen = db.Column(db.Boolean, nullable=False, default=False)
    never_delete = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    comments = db.relationship('Comment', backref='paste')


class Hash(db.Model, fs_mixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url_hash = db.Column(db.String(8), unique=True, nullable=False)


class Comment(db.Model, fs_mixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(200), nullable=False)                # comment.content max 200 chars 
    created_at = db.Column(db.DateTime, nullable=False)
    expire_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    paste_id = db.Column(db.Integer, db.ForeignKey('paste.id'), nullable=False)
