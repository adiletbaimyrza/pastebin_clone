from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_serialize import FlaskSerialize
import uuid
from datetime import datetime

from cutils import add_utc_minutes, is_expired

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
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    expire_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Paste {self.id}>'


# create a database before app runs
with app.app_context():
    db.create_all()


@app.post('/post')
def post():
    # create a Paste model instance from json
    new_paste = Paste(
        id=str(uuid.uuid4()),
        content=request.json['content'],
        created_at=datetime.utcnow(),
        expire_at=add_utc_minutes(datetime.utcnow(), minutes_to_add=request.json['minutes_to_live']))

    # add to the database
    db.session.add(new_paste)
    db.session.commit()

    # return json of the created paste
    return Paste.fs_get_delete_put_post(new_paste.id), 201


@app.get('/get/<uuid:id>')
def get_paste(id):
    # query the Paste model by id using get()
    paste = Paste.query.get(str(id))

    # check if the paste exists in the database
    if paste:
        # if exists check for expiration
        if is_expired(paste.expire_at):
            # return 410 Gone status code if the Paste is expired
            return 'Paste is expired', 410
        else:
            # return serialized paste object as JSON with 200 OK status code
            return Paste.fs_get_delete_put_post(paste.id), 200
    else:
        # return 404 Not Found status code if paste not found
        return 'Paste not found', 404


if __name__ == '__main__':
    app.run()
