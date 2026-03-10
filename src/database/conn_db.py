# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# import urllib
# from src.setup import DB_DRIVER, DB_SERVER, DB_DATABASE, DB_UID, DB_PWD


# class Database:
#     def __init__(self):
#         params = urllib.parse.quote_plus(
#             "DRIVER=" + DB_DRIVER + ";"
#             "SERVER=" + DB_SERVER + ";"
#             "DATABASE=" + DB_DATABASE + ";"
#             "UID=" + DB_UID + ";"
#             "PWD=" + DB_PWD + ";"
#             "Encrypt=no;"
#             "TrustServerCertificate=yes;"
#         )

#         self.engine = create_async_engine(
#             f"mssql+aioodbc:///?odbc_connect={params}",
#             pool_size=10,
#             max_overflow=20,
#             pool_timeout=30,
#         )

#         self.SessionLocal = async_sessionmaker(
#             bind=self.engine,
#             expire_on_commit=False,
#         )

#     def get_session(self):
#         return self.SessionLocal()


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import urllib
from src.setup import DB_DRIVER, DB_SERVER, DB_DATABASE, DB_UID, DB_PWD


class Database:
    def __init__(self):
        params = urllib.parse.quote_plus(
            "DRIVER=" + DB_DRIVER + ";"
            "SERVER=" + DB_SERVER + ";"
            "DATABASE=" + DB_DATABASE + ";"
            "UID=" + DB_UID + ";"
            "PWD=" + DB_PWD + ";"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
        )

        self.engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={params}",
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    def get_session(self):
        return self.SessionLocal()
