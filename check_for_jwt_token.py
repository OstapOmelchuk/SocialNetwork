import os
import jwt

from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv
from test_project_api.models.user_model import User
from test_project_api.models.revoke_token_model import RevokedToken

load_dotenv()


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        all_jwt = [token.to_dict().get("jwt") for token in RevokedToken.get_all()]
        if token not in all_jwt:
            try:
                data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
                current_user = User.get_by_id(id=data['id'])
            except:
                return jsonify({'message': 'token is invalid'})

            return f(current_user, *args, **kwargs)
        return jsonify({'message': 'token is expired'})

    return decorator
