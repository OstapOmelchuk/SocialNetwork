from test_project_api.models import user_model, post_model, likes_model
from app import app
from database import db

with app.app_context():
    db.create_all()
