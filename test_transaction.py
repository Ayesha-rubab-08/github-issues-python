import os

import psycopg
import pytest

from db import save_issues

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.environ.get("PG_PASSWORD"), reason="PG_PASSWORD not set"),
]

FIRST_ID = 9000000
LAST_ID = 9000029


def connect():
    return psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="issues_db",
        user="issues_user",
        password=os.environ["PG_PASSWORD"],
        connect_timeout=5,
    )


def count_test_rows():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM issues WHERE id BETWEEN %s AND %s",
                (FIRST_ID, LAST_ID),
            )
            return cur.fetchone()[0]


def delete_test_rows():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM issues WHERE id BETWEEN %s AND %s",
                (FIRST_ID, LAST_ID),
            )


def test_bad_row_rolls_back_the_whole_batch():
    issues = []
    for i in range(30):
        issues.append({
            "id": FIRST_ID + i,
            "number": i,
            "title": f"test {i}",
            "author": "tester",
            "is_pull_request": False,
        })
    # title is NOT NULL, so Postgres must reject the 16th row
    issues[15]["title"] = None

    delete_test_rows()
    try:
        with pytest.raises(SystemExit) as exc:
            save_issues(issues)
        assert exc.value.code == 1
        assert count_test_rows() == 0
    finally:
        delete_test_rows()
