import pandas as pd
from sqlalchemy import text
from src.database.conn_db import Database


class SQLService:
    def __init__(self, database: Database):
        self.database = database

    def _validate_query(self, sql: str):
        if not sql.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed.")

    def execute(self, sql: str) -> pd.DataFrame | str:
        try:
            self._validate_query(sql)

            with self.database.get_session() as session:
                result = session.execute(text(sql))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                return df
        except Exception as e:
            raise RuntimeError(str(e))
