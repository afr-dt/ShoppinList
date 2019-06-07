import datetime
from db import db
from app import app
from sqlalchemy.dialects.postgresql import ARRAY

from werkzeug.security import generate_password_hash, check_password_hash
import jwt


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    last_name = db.Column(db.String(40))
    user_name = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    purchases = db.relationship('Purchase', backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def encode_auth_token(self, user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=1800),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(request):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Token expirado 🧐, vuelva a iniciar sesión 😃.'
        except jwt.InvalidTokenError:
            return 'Token invalido 🤯, vuelva a iniciar sesión 😃.'

    def __repr__(self):
        return f"User('{self.username}')"


class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    tags = db.Column(ARRAY(db.String), nullable=False)
    is_done = db.Column(db.Boolean, default=True)
    created = db.Column(db.DateTime, default=db.func.now())
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"Purchase('{self.name}')"
