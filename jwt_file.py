import jwt
from flask import current_app

token = jwt.encode({"user": 1}, current_app.config['SECRET_KEY'], algorithm="HS256")
print(token)
decode_token = jwt.decode(token, current_app.config['SECRET_KEY'],algorithms=['HS256'])
print(decode_token)
