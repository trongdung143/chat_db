# import pandas as pd
# from sqlalchemy import text
# from src.database.conn_db import Database


# class SQLService:
#     def __init__(self, database: Database):
#         self.database = database

#     def _validate_query(self, sql: str):
#         if not sql.strip().lower().startswith("select"):
#             raise ValueError("Only SELECT queries are allowed.")

#     async def execute(self, sql: str) -> pd.DataFrame | str:
#         try:
#             self._validate_query(sql)

#             async with self.database.get_session() as session:
#                 result = await session.execute(text(sql))

#                 rows = result.fetchall()
#                 df = pd.DataFrame(rows, columns=result.keys())

#                 return df

#         except Exception as e:
#             raise RuntimeError(str(e))


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

            session = self.database.get_session()
            try:
                result = session.execute(text(sql))

                rows = result.fetchall()
                df = pd.DataFrame(rows, columns=result.keys())

                return df
            finally:
                session.close()

        except Exception as e:
            raise RuntimeError(str(e))
