from flask_httpauth import HTTPTokenAuth
from .errors import unauthorized
from ..models import User
from flask_login import current_user
from .errors import forbidden
from flask import current_app


auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_password
def verify_token(token):
    
    verify_token = User.Verify_token(token, current_app.config.get("SECRET_KEY"))

    if not verify_token:

        return None
    
    return User.query.filter_by(id=verify_token['sub'])


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@auth.verify_token
def verify_token(token):
    # Your token verification logic here
    return True  # Replace with your actual verification logic
# 