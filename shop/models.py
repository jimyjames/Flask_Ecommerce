from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import db
import jwt
import datetime
from flask import current_app




class User(UserMixin, db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(10), nullable=False, unique=True)
    email = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    profile = db.Column(db.String(80), unique=False, nullable=False, default='profile.jpg')
    confirmed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'User("{self.id}","{self.name}","{self.username}","{self.email}")'
    def generate_confirmation_token(self, expiration=3600):
        confirmation_token = jwt.encode({
            "confirm": self.id,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=expiration)
        },
        current_app.config['SECRET_KEY'],
        algorithm="HS256"
        )
        return confirmation_token

    def confirm(self, token):
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            # Token has expired
            return False
        except jwt.InvalidTokenError:
            # Token is invalid
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
from . import login_manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
