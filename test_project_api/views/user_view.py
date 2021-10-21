import os
import datetime
import json
import jwt

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from test_project_api.models.revoke_token_model import RevokedToken
from test_project_api.models.user_model import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user
from check_for_jwt_token import token_required
from dotenv import load_dotenv


load_dotenv()

mod = Blueprint('user', __name__, static_folder="static", template_folder="templates")


class UserView(MethodView):
    def get(self, id=None):
        if id is None:
            users = [user.to_dict() for user in User.get_all()]
            return make_response(jsonify(users), 200)
        user = User.get_by_id(id=id)
        user.update_last_request_time()
        if user:
            return make_response(jsonify(user.to_dict()), 200)
        message = f"Can not find user, wrong id: {id}"
        return make_response(message, 400)

    @token_required
    def put(self, put_request, id):
        user = User.get_by_id(id=id)
        if not user:
            message = "Wrong id"
            return make_response(message, 400)
        body = json.loads(request.data)
        new_username, new_email, new_password = (body.get("username"), body.get("email"), body.get("password"))
        values_to_update = {}
        if isinstance(new_username, str):
            values_to_update['username'] = new_username
        if isinstance(new_email, str):
            values_to_update['email'] = new_email
        if isinstance(new_password, str):
            values_to_update['password'] = new_password
        if values_to_update:
            user.update(**values_to_update)
            if user:
                user.update_last_request_time()
                return make_response(jsonify(user.to_dict()), 200)
        message = "An error occurred during updating"
        return make_response(message, 400)


class UserSignUpView(UserView):
    def post(self):
        data = request.get_json()
        username = data['username']
        email = data['email']
        password = data['password']
        if User.get_by_email(email):
            return make_response("this email is already being used.", 400)
        if User.get_by_username(username):
            return make_response("this username is already being used.", 400)
        user = User.create(username, email, str(generate_password_hash(password, method='sha256')))
        if user:
            user.update_last_request_time()
            return make_response("New user registered.", 200)
        return make_response(400)


class UserLoginView(MethodView):
    def post(self):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return make_response('could not verify', 401, {'Authentication': 'login required"'})

        user = User.get_by_username(username=auth.username)
        user.update_last_request_time()
        if check_password_hash(user.password, auth.password):
            token = jwt.encode(
                {'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)},
                os.getenv("SECRET_KEY"), "HS256")
            user.update_last_login_time()
            return jsonify({'token': token})

        return make_response('could not verify', 401, {'Authentication': '"login required"'})


class UserLogOutView(MethodView):
    @token_required
    def post(self, post_request):
        logout_user()
        RevokedToken.create(request.headers['x-access-token'])
        return make_response("You are now logged out.", 200)


class UserActivityView(MethodView):
    def get(self, id):
        user = User.get_by_id(id=id)
        if not user:
            message = f"Can not find user, wrong id: {id}"
            return make_response(message, 400)
        user_activity = {
            "last login time": user.last_login_time,
            "last request to the service time": user.last_request
        }
        return make_response(jsonify(user_activity), 200)


user_view = UserView.as_view('user')
mod.add_url_rule('/', view_func=user_view, methods=['GET'])
mod.add_url_rule('/<id>', view_func=user_view, methods=['GET', 'DELETE', 'PUT'])

user_signup_view = UserSignUpView.as_view('user_signup')
mod.add_url_rule('/signup', view_func=user_signup_view, methods=['POST'])

user_login_view = UserLoginView.as_view('user_login')
mod.add_url_rule('/login', view_func=user_login_view, methods=['POST'])

user_logout_view = UserLogOutView.as_view('logout')
mod.add_url_rule('/logout', view_func=user_logout_view, methods=['POST'])

user_activity_view = UserActivityView.as_view('user_activity')
mod.add_url_rule('/<id>/user_activity', view_func=user_activity_view, methods=['GET'])
