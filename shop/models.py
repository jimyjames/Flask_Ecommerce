from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(10), nullable=False, unique=True)
    email = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    profile = db.Column(db.String(80), unique=False, nullable=False, default='profile.jpg')

    def __repr__(self):
        return f'User("{self.id}","{self.name}","{self.username}","{self.email}")'
