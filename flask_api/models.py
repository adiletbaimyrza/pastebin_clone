from flask_sqlalchemy import SQLAlchemy
from flask_serialize import FlaskSerialize

db = SQLAlchemy()
fs_mixin = FlaskSerialize(db)

class User(db.Model, fs_mixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(87), nullable=False)

    comments = db.relationship('Comment', backref='user')
    pastes = db.relationship('Paste', backref='user')


class Paste(db.Model, fs_mixin):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(8), unique=True, nullable=False)
    blob_url = db.Column(db.String(256), unique=True, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False)
    expire_at = db.Column(db.DateTime, nullable=False)
    views_count = db.Column(db.Integer, nullable=False, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    comments = db.relationship('Comment', backref='paste')


class Hash(db.Model, fs_mixin):
    id = db.Column(db.Integer, primary_key=True)
    url_hash = db.Column(db.String(8), unique=True)


class Comment(db.Model, fs_mixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    paste_id = db.Column(db.Integer, db.ForeignKey('paste.id'), nullable=False)
