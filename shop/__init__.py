from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from config import config
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(config['development'])

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view="admin.login"

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    mail.init_app(app)
    db.init_app(app)
    migrate=Migrate(app,db)
   
    login_manager.init_app(app)

    
   
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    


    return app



