import os

import psycopg
from psycopg.rows import TupleRow


def get_db_conn() -> psycopg.Connection[TupleRow]:
    return psycopg.connect(os.environ["DATABASE_URL"])