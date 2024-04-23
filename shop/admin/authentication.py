from flask_httpauth import HTTPTokenAuth, HTTPBasicAuth
from .errors import *
from ..models import User
from flask_login import current_user

from flask import current_app,jsonify
from werkzeug.security import check_password_hash


auth = HTTPTokenAuth()

basic_auth = HTTPBasicAuth()


@auth.verify_token
def verify_token(token):
    
    verify_token = User.Verify_token(token, current_app.config.get("SECRET_KEY"))

    if not verify_token:

        return None
    
    return User.query.filter_by(id=verify_token['sub'])


# @auth.error_handler
# def auth_error():
#     return unauthorized('Invalid credentials')


@basic_auth.verify_password
def verify_password(email,password):
    user = User.query.filter_by(email = email).first()

    if not user or  not check_password_hash(user.password, password):

        return None
    
    return user
@basic_auth.error_handler
def basic_auth_error(status):

    return jsonify({'message': 'Invalid credentials'}), status


@auth.error_handler
def token_auth_error(status):

    return jsonify({'message': 'Unauthorized'}), status
