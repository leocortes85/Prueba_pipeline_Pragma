from sqlalchemy import text
from src.config import engine
from src.db import create_tables, reset_db
from src.stats import update_stats_db

def test_update_stats_db():
    create_tables()
    reset_db()
    with engine.begin() as conn:
        res = update_stats_db(conn, 3, 60.0, 10.0, 30.0)
        assert res["count"] == 3
        assert res["min"] == 10.0
        assert res["max"] == 30.0
        assert res["mean"] == 20.0
