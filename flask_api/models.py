from flask_sqlalchemy import SQLAlchemy
from flask_serialize import FlaskSerialize


db = SQLAlchemy()

fs_mixin = FlaskSerialize(db)


class Paste(db.Model):
    hash = db.Column(db.String(8), primary_key=True)
    blob_url = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    expire_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.String(36), nullable=True, default=None)
    username = db.Column(db.String(20), nullable=True, default=None)
    views_count = db.Column(db.Integer, nullable=False, default=0)


class Hash(db.Model, fs_mixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url_hash = db.Column(db.String(8), primary_key=True)
    is_assigned = db.Column(db.Boolean)
