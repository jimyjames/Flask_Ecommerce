from functools import wraps
from flask import request,jsonify,current_app
import jwt


def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=request.args.get('token')
        if not token:
            return jsonify({'message':'Token is missing!'}),403
        try:
            data=jwt.decode(token, current_app.config['SECRET_KEY'],algorithms=['HS256'])
        except:
            return jsonify({'message':'Token is invalid'}),403
        return f(*args, **kwargs)
    return(decorated)
