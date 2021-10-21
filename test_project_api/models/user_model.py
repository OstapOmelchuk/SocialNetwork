from psycopg2 import DataError, ProgrammingError
from database import db
from test_project_api.models.post_model import Post
from flask_login import UserMixin
from test_project_api.models.likes_model import likes
from datetime import datetime, timedelta
from test_project_api.utils.get_db_connection import get_connection_to_db, get_cursor_data
from sqlalchemy import func, and_


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(1000))
    password = db.Column(db.String(100))
    last_request = db.Column(db.DateTime(timezone=False), server_default=func.now())
    last_login_time = db.Column(db.DateTime(timezone=False), server_default=func.now())

    def __init__(self, id, username, email, password, last_request=datetime.now(), last_login_time=datetime.now()):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.last_request = last_request
        self.last_login_time = last_login_time

    @classmethod
    def create(cls, username: str, email: str, password: str):
        query = f"""INSERT INTO {cls.__tablename__} (username, email, password)
                    VALUES ('%(username)s', '%(email)s', '%(password)s')
                    RETURNING * ;"""
        try:
            id, username, email, password, last_request, last_login_time = get_cursor_data(
                query, {'username': username, 'email': email, 'password': password}
            )
            return User(id=id, username=username, email=email, password=password)
        except(DataError, ProgrammingError):
            return None

    def update(self, username: str = None, email: str = None, password: str = None):
        data_to_update = []
        if username is not None:
            data_to_update.append("username = '%(username)s'")
        if email is not None:
            data_to_update.append("email = '%(email)s'")
        if password is not None:
            data_to_update.append("password = '%(password)s'")
        query = f"""UPDATE {User.__tablename__} SET {', '.join(data_to_update)}
                    WHERE id = %(id)s 
                    RETURNING * ;"""
        try:
            id, username, email, password, last_request, last_login_time = get_cursor_data(
                query, {'username': username, 'email': email, 'password': password, 'id': self.id}
            )
            self.username = username
            self.email = email
            self.password = password
            return True
        except(DataError, ProgrammingError):
            return False

    def update_last_request_time(self):
        query = f"""UPDATE {User.__tablename__} SET last_request = '%(last_request)s'
                    WHERE id = %(id)s 
                    RETURNING last_request;"""
        try:
            last_request = get_cursor_data(
                query, {'last_request': datetime.now(), 'id': self.id}
            )
            self.last_request = last_request
            return True
        except(DataError, ProgrammingError):
            return False

    def update_last_login_time(self):
        query = f"""UPDATE {User.__tablename__} SET last_login_time = '%(last_login_time)s'
                    WHERE id = %(id)s 
                    RETURNING last_login_time ;"""
        try:
            last_login_time = get_cursor_data(
                query, {'last_login_time': datetime.now(), 'id': self.id}
            )
            self.last_login_time = last_login_time
            return True
        except(DataError, ProgrammingError):
            return False

    @classmethod
    def get_by_id(cls, id: int):
        query = f"SELECT * FROM {cls.__tablename__} WHERE id = '%(id)s'"
        try:
            id, username, email, password, last_request, last_login_time = get_cursor_data(
                query, {'id': id}
            )
            return User(id=id, username=username, email=email, password=password, last_request=last_request, last_login_time=last_login_time)
        except(DataError, ProgrammingError, TypeError):
            return None

    @classmethod
    def get_by_email(cls, email: str):
        query = f"SELECT * FROM {cls.__tablename__} WHERE email = '%(email)s'"
        try:
            id, username, email, password, last_request, last_login_time = get_cursor_data(
                query, {'email': email}
            )
            return User(id=id, username=username, email=email, password=password, last_request=last_request, last_login_time=last_login_time)
        except(DataError, ProgrammingError, TypeError):
            return None

    @classmethod
    def get_by_username(cls, username: str):
        query = f"SELECT * FROM {cls.__tablename__} WHERE username = '%(username)s'"
        try:
            id, username, email, password, last_request, last_login_time = get_cursor_data(
                query, {'username': username}
            )
            return User(id=id, username=username, email=email, password=password, last_request=last_request, last_login_time=last_login_time)
        except(DataError, ProgrammingError, TypeError):
            return None

    @classmethod
    def get_all(cls):
        query = f"SELECT * FROM {cls.__tablename__}"
        try:
            conn = get_connection_to_db()
            cur = conn.cursor()
            cur.execute(query)
            users = cur.fetchall()
            all_users = [User(id=id,
                              username=username,
                              email=email,
                              password=password,
                              last_request=last_request,
                              last_login_time=last_login_time)
                         for id, username, email, password, last_request, last_login_time in users]
            return all_users
        except(DataError, ProgrammingError, TypeError):
            return None

    @classmethod
    def delete_by_id(cls, id: int):
        if not User.get_by_id(id):
            return False
        query = f"DELETE FROM {cls.__tablename__} WHERE id = '%(id)s'"
        try:
            conn = get_connection_to_db()
            cur = conn.cursor()
            cur.execute(query % {'id': id})
            conn.commit()
            return True
        except(DataError, ProgrammingError):
            return False

    def like_post(self, post_id):
        try:
            post = Post.get_by_id(post_id)
            post_liked = db.session.query(func.count(likes.columns.user_id)).where(
                and_(
                    likes.columns.user_id == self.id,
                    likes.columns.post_id == post_id)
            ).first()[0]
            if post and post_liked == 0:
                post.like_post()
                like_time = datetime.now()

                statement = likes.insert().values(user_id=self.id, post_id=post.id, event_time=like_time)
                db.session.execute(statement)
                db.session.commit()
                return True
            return False
        except(DataError, ProgrammingError):
            return False

    def unlike_post(self, post_id):
        try:
            post = Post.get_by_id(post_id)
            post_liked = db.session.query(func.count(likes.columns.user_id)).where(
                and_(
                    likes.columns.user_id == self.id,
                    likes.columns.post_id == post_id)
            ).first()[0]
            if post and post_liked > 0:
                post.unlike_post()

                statement = likes.delete().where(likes.columns.user_id == self.id, likes.columns.post_id == post.id)
                db.session.execute(statement)
                db.session.commit()
                return True
            return False
        except(DataError, ProgrammingError):
            return False

    def to_dict(self):
        """
        Returns a dictionary with a stock data values.
        """
        return {'id': self.id, "username": self.username, "email": self.email}
