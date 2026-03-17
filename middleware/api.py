from fastapi import FastAPI, HTTPException
from middleware.crypto import decrypt, verify, encrypt, sign
from middleware.sql_service import SQLService
from middleware.conn_db import Database
from middleware.utils import dataframe_to_json
import json

app = FastAPI()
db = Database()
sql_service = SQLService(db)


@app.post("/query/v1")
def query_api(body: dict):
    encrypted_data = body.get("data")
    signature = body.get("signature")

    if not verify(encrypted_data, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    sql = decrypt(encrypted_data)

    if not sql.strip().lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT allowed")

    df = sql_service.execute(sql)
    result = dataframe_to_json(df)

    result_json = json.dumps(result)

    encrypted_response = encrypt(result_json)

    response_signature = sign(encrypted_response)

    return {"data": encrypted_response, "signature": response_signature}
