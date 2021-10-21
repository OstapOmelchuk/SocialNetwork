from psycopg2 import DataError, ProgrammingError
from database import db
from datetime import datetime
from sqlalchemy.sql import func
from test_project_api.utils.get_db_connection import get_connection_to_db, get_cursor_data


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(10000))
    likes = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    creation_time = db.Column(db.DateTime(timezone=False), server_default=func.now())
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", cascade="all,delete", backref="posts")

    def __init__(self, id, text, owner_id, likes=0, creation_time=datetime.now()):
        self.id = id
        self.text = text
        self.likes = likes
        self.creation_time = creation_time
        self.owner_id = owner_id

    @classmethod
    def create(cls, text, owner_id):
        query = f"""INSERT INTO {cls.__tablename__} (text, owner_id)
                    VALUES ('%(text)s', %(owner_id)s)
                    RETURNING id, text, likes, creation_time, owner_id;"""
        try:
            id, text, likes, creation_time, owner_id = get_cursor_data(
                query, {'text': text, "owner_id": owner_id}
            )
            return Post(id=id, text=text, owner_id=owner_id)

        except(DataError, ProgrammingError):
            return None

    def update(self, text: str = None):
        if text is not None:
            query = f"""UPDATE {Post.__tablename__} SET text = '%(text)s', creation_time = '%(creation_time)s'
                    WHERE id = %(id)s
                    RETURNING id, text, likes, creation_time, owner_id;"""
            try:
                time_now = datetime.now()
                id, text, likes, creation_time, owner_id = get_cursor_data(
                    query, {'text': text, 'id': self.id, 'creation_time': time_now}
                )
                self.text = text
                self.creation_time = time_now
                return True
            except(DataError, ProgrammingError):
                return False

    @classmethod
    def get_by_id(cls, id: int):
        query = f"SELECT * FROM {cls.__tablename__} WHERE id = %(id)s"
        try:
            id, text, likes, creation_time, owner_id = get_cursor_data(
                query, {'id': id}
            )
            return Post(id=id, text=text, likes=likes, creation_time=creation_time, owner_id=owner_id)
        except(DataError, ProgrammingError, TypeError):
            return None

    @classmethod
    def get_all(cls):
        query = f"SELECT * FROM {cls.__tablename__}"
        try:
            conn = get_connection_to_db()
            cur = conn.cursor()
            cur.execute(query)
            posts = cur.fetchall()
            all_users = [
                Post(id=id,
                     text=text,
                     likes=likes,
                     creation_time=creation_time, owner_id=owner_id) for
                id, text, likes, creation_time, owner_id in posts
            ]
            return all_users
        except(DataError, ProgrammingError, TypeError):
            return None

    @classmethod
    def delete_by_id(cls, id: int):
        if not cls.get_by_id(id):
            return False
        query = f"DELETE FROM {cls.__tablename__} WHERE id = %(id)s"
        try:
            conn = get_connection_to_db()
            cur = conn.cursor()
            cur.execute(query % {'id': id})
            conn.commit()
            return True
        except(DataError, ProgrammingError):
            return False

    def like_post(self):
        query = f"""UPDATE {Post.__tablename__} SET likes = %(likes)s
                    WHERE id = %(id)s
                    RETURNING id, text, likes, creation_time, owner_id;"""
        try:
            id, text, likes, creation_time, owner_id = get_cursor_data(
                query, {'likes': self.likes+1, 'id': self.id}
            )
            self.likes = likes
            return True
        except(DataError, ProgrammingError):
            return False

    def unlike_post(self):
        query = f"""UPDATE {Post.__tablename__} SET likes = %(likes)s
                    WHERE id = %(id)s
                    RETURNING id, text, likes, creation_time, owner_id;"""
        try:
            id, text, likes, creation_time, owner_id = get_cursor_data(
                query, {'likes': self.likes-1, 'id': self.id}
            )
            self.likes = likes
            return True
        except(DataError, ProgrammingError):
            return False

    def to_dict(self):
        """
        Returns a dictionary with a stock data values.
        """
        return {
            'id': self.id,
            "text": self.text,
            "likes": self.likes,
            "creation_time": self.creation_time,
            "owner_id": self.owner_id
        }


