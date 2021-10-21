import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection_to_db():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"))
    return conn


def get_cursor_data(query, params=None):
    conn = get_connection_to_db()
    cur = conn.cursor()
    cur.execute(query % params)
    cur_data = cur.fetchone()
    conn.commit()
    return cur_data
