import logging
import os

import psycopg

UPSERT_SQL = """
INSERT INTO issues (id, number, title, author, is_pull_request)
VALUES (%(id)s, %(number)s, %(title)s, %(author)s, %(is_pull_request)s)
ON CONFLICT (id) DO UPDATE SET
  number = EXCLUDED.number,
  title = EXCLUDED.title,
  author = EXCLUDED.author,
  is_pull_request = EXCLUDED.is_pull_request
"""


def save_issues(issues):
    password = os.environ.get("PG_PASSWORD")
    if not password:
        raise SystemExit("PG_PASSWORD is not set")

    try:
        # One transaction: it commits only if every row saves.
        with psycopg.connect(
            host="127.0.0.1",
            port=5432,
            dbname="issues_db",
            user="issues_user",
            password=password,
            connect_timeout=5,
        ) as conn:
            with conn.cursor() as cur:
                cur.executemany(UPSERT_SQL, issues)
    except psycopg.Error as error:
        logging.error("Database write failed - %s", error)
        raise SystemExit(1)

    logging.info("Upserted %s issues into Postgres", len(issues))