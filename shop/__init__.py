from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myshop.db'
app.config['SECRET_KEY'] = 'ecommerce1234'

from shop.models import db
db.init_app(app)

from shop.admin import routes as main

from shop.models import User  # Assuming User is your model

# Import your routes here
from shop.admin import routes

# Create all database tables
with app.app_context():
    db.create_all()
