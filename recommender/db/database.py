import psycopg2
from psycopg2.extras import RealDictCursor
import os

# def get_db_connection():
#     return psycopg2.connect(
#         dbname="lolmatch",
#         user="postgres",
#         password="admin",
#         port="5432",
#         host="localhost"
#     )


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        host=os.getenv("DB_HOST"),
    )


def fetch_one(query, params=None):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchone()


def fetch_all(query, params=None):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()


def execute_query(query, conn=None, params=None, commit=False):
    if not conn:
        conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(query, params)
        if commit:
            conn.commit()
