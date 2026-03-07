import pandas as pd
from decimal import Decimal
import re
import sqlparse


def dataframe_to_json(df: pd.DataFrame, max_rows: int = 10):

    if df.empty:
        return []

    if df.columns.duplicated().any():
        counts = {}
        new_cols = []

        for col in df.columns:
            if col in counts:
                counts[col] += 1
                new_cols.append(f"{col}_{counts[col]}")
            else:
                counts[col] = 0
                new_cols.append(col)

        df.columns = new_cols

    df = df.head(max_rows)

    df = df.where(pd.notna(df), None)

    def convert_value(v):
        if isinstance(v, pd.Timestamp):
            return v.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(v, Decimal):
            return float(v)
        return v

    df = df.apply(lambda col: col.map(convert_value))

    return df.to_dict(orient="records")


def sanitize_sql(text: str) -> str:
    try:
        text = re.sub(r"```[\s\S]*?\n", "", text)
        text = text.replace("```", "")

        match = re.search(r"\bSELECT\b[\s\S]*", text, re.IGNORECASE)
        if not match:
            raise ValueError("No SELECT found")

        text = match.group(0)

        statements = sqlparse.parse(text)

        for stmt in statements:
            if stmt.get_type() == "SELECT":
                sql = str(stmt).strip()

                sql = re.sub(r"--.*", "", sql)
                sql = re.sub(r"/\*[\s\S]*?\*/", "", sql)
                sql = re.sub(r"\s+", " ", sql)

                return sql.strip()

        raise ValueError("No valid SELECT statement")

    except Exception as e:
        raise ValueError(f"SQL sanitize error: {str(e)}")
