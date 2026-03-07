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
        )

        self.engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={params}",
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
        )

        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()
