from database import db
from test_project_api.utils.get_db_connection import get_cursor_data, get_connection_to_db
from psycopg2 import DataError, ProgrammingError


class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jwt = db.Column(db.String(120))
    
    def __init__(self, id, jwt):
        self.id = id
        self.jwt = jwt

    @classmethod
    def create(cls, jwt: str):
        count = db.session.query(RevokedToken).where(RevokedToken.jwt == jwt).count()
        if count == 0:
            query = f"""INSERT INTO {cls.__tablename__} (jwt)
                        VALUES ('%(jwt)s')
                        RETURNING * ;"""
            try:
                id, jwt = get_cursor_data(
                    query, {'jwt': jwt}
                )
                return RevokedToken(id=id, jwt=jwt)
            except(DataError, ProgrammingError, TypeError):
                return None
        else:
            return False

    @classmethod
    def get_all(cls):
        query = f"""SELECT * FROM {cls.__tablename__}"""
        try:
            conn = get_connection_to_db()
            cur = conn.cursor()
            cur.execute(query)
            blacklist_jwt = cur.fetchall()
            all_blacklist_jwt = [RevokedToken(id=id, jwt=jwt) for id, jwt in blacklist_jwt]
            return all_blacklist_jwt
        except(DataError, ProgrammingError, TypeError):
            return None

    def to_dict(self):
        """
        Returns a dictionary with a stock data values.
        """
        return {'id': self.id, "jwt": self.jwt}
