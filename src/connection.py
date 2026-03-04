from sqlalchemy import create_engine
import urllib
from setup import DB_DRIVER, DB_SERVER, DB_DATABASE, DB_UID, DB_PWD

params = urllib.parse.quote_plus(
    "DRIVER=" + DB_DRIVER + ";"
    "SERVER=" + DB_SERVER + ";"
    "DATABASE=" + DB_DATABASE + ";"
    "UID=" + DB_UID + ";"
    "PWD=" + DB_PWD + ";"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
