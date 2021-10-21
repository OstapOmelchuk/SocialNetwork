import os

from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager
from database import db
from test_project_api.views.post_view import mod as post_view_mod
from test_project_api.views.user_view import mod as user_view_mod, User
from test_project_api.views.likes_view import mod as likes_view_mod

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY")

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


app.register_blueprint(user_view_mod, url_prefix="/user")
app.register_blueprint(post_view_mod, url_prefix="/user")
app.register_blueprint(likes_view_mod, url_prefix="/likes")


if __name__ == "__main__":
    app.run(debug=True)
