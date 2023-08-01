from flask_sqlalchemy import SQLAlchemy
from flask_serialize import FlaskSerialize

# Create an extension
db = SQLAlchemy()

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

# Hash model


class Hash(db.Model, fs_mixin):
    url_hash = db.Column(db.String(8), primary_key=True)
    paste_id = db.Column(db.String(36), unique=True)

    def __repr__(self):
        return f'Hash {self.url_hash}'
