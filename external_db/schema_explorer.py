from sqlalchemy import inspect

from .db_connection import get_engine


def list_tables():
    engine = get_engine()
    if engine is None:
        raise ConnectionError("Немає активного з'єднання з базою даних")

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return tables


def get_table_schema(table_name: str):
    engine = get_engine()
    if engine is None:
        raise ConnectionError("Немає активного з'єднання з базою даних")

    inspector = inspect(engine)
    columns_info = inspector.get_columns(table_name)
    schema = [{"name": col["name"], "type": str(col["type"])} for col in columns_info]
    return schema


def get_full_schema():
    tables = list_tables()
    full_schema = {}
    for t in tables:
        full_schema[t] = get_table_schema(t)
    return full_schema


if __name__ == "__main__":
    try:
        tables = list_tables()
        print("Таблиці:", tables)
        if tables:
            schema = get_table_schema(tables[0])
            print(f"Структура таблиці {tables[0]}:", schema)
    except Exception as e:
        print("Помилка:", e)
