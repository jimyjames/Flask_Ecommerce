from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import db, login_manager
import jwt
from datetime import timedelta, datetime, timezone
from flask import current_app


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(10), nullable=False, unique=True)
    email = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    profile = db.Column(
        db.String(80), unique=False, nullable=False, default="profile.jpg"
    )
    confirmed = db.Column(db.Boolean, default=False)
    phone = db.Column(db.Integer)
    county = db.Column(db.String(20))
    town = db.Column(db.String(15))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(7))
    created_at = db.Column(db.Date, default=(datetime.utcnow()))
    companyname = db.Column(db.String(30))
    address = db.Column(db.String)

    orders = db.relationship("Order", backref="user_order", lazy="dynamic")

    def __repr__(self):
        return f'User("{self.id}","{self.name}","{self.username}","{self.email}")'

    def generate_confirmation_token(self, expiration=3600):
        confirmation_token = jwt.encode(
            {
                "confirm": self.id,
                "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expiration),
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return confirmation_token

    def generate_auth_token(self, timeline=9000):
        payload = {
            "exp": datetime.utcnow() + timedelta(seconds=timeline),
            "iat": datetime.utcnow(),
            "sub": self.id,
        }
        return jwt.encode(payload, current_app.config["SECRET_KEY"])

    def verify_token(token, secret_key):
        try:
            return jwt.decode(token, secret_key, algorithms="HS256")
        except:
            return None

    def confirm(self, token):
        print("here we go ")
        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            # Token has expired
            return (False, "Your token has expired")
        except jwt.InvalidTokenError:
            print("Your Token is invalid ")
            # Token is invalid
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    # merchant_id=db.Column(db.Integer)
    name = db.Column(db.String(30), nullable=False)
    category = db.Column(db.String, nullable=False)
    description = db.Column(db.String(), nullable=False)
    price = db.Column(db.Float, nullable=False)
    detail = db.relationship(
        "ProductDescription",
        backref="details",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    discounted_price = db.Column(db.Float)
    stock_level = db.Column(db.Integer)
    creation_date = db.Column(db.Date, default=(datetime.utcnow()))
    summary = db.Column(db.String)
    rating = db.Column(db.Integer, default=0)

    purchases = db.relationship("Order", backref="purchases", lazy="dynamic")


class ProductDescription(db.Model):
    __tablename__ = "product_description"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    title = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String, nullable=False)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    quantity = db.Column(db.Integer)
    order_date = db.Column(db.Date, default=datetime.now().date())
    total_price = db.Column(db.Float)

    def __repr__(self):
        return f'Order("{self.id}","{self.customer}","{self.product_id}","{self.quantity}","{self.order_date}","{self.total_price}")'
class ProductImages(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    image = db.Column(db.String, nullable=False)
    default = db.Column(db.Boolean, default=False)
