import urllib.parse

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

_current_engine = None
_current_uri = None


def build_postgres_uri(
        host: str,
        port: int,
        user: str,
        password: str,
        dbname: str,
) -> str:
    user_enc = urllib.parse.quote_plus(user)
    password_enc = urllib.parse.quote_plus(password)
    return (
        f"postgresql+psycopg2://{user_enc}:{password_enc}"
        f"@{host}:{port}/{dbname}"
    )


def build_mysql_uri(
        host: str,
        port: int,
        user: str,
        password: str,
        dbname: str,
) -> str:
    user_enc = urllib.parse.quote_plus(user)
    password_enc = urllib.parse.quote_plus(password)
    return (
        f"mysql+pymysql://{user_enc}:{password_enc}"
        f"@{host}:{port}/{dbname}"
    )


def build_sqlite_uri(file_path: str) -> str:
    return f"sqlite:///{file_path}"


def connect_from_params(
        db_type: str,
        host: str = None,
        port: int = None,
        dbname: str = None,
        user: str = None,
        password: str = None,
        file_path: str = None,
):
    global _current_engine, _current_uri

    try:
        if db_type == "postgresql":
            uri = build_postgres_uri(host, port, user, password, dbname)
        elif db_type == "mysql":
            uri = build_mysql_uri(host, port, user, password, dbname)
        elif db_type == "sqlite":
            if not file_path:
                return {
                    "success": False,
                    "message": "Не вказано шлях до SQLite файлу",
                }
            uri = build_sqlite_uri(file_path)
        else:
            return {
                "success": False,
                "message": f"Невідомий тип БД: {db_type}",
            }

        engine = create_engine(uri, echo=False)

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        _current_engine = engine
        _current_uri = uri
        print(f"Підключено до БД ({db_type}) → {uri}")
        return {
            "success": True,
            "message": f"Підключено до {db_type} БД",
        }

    except SQLAlchemyError as e:
        print(f"Помилка підключення: {e}")
        _current_engine = None
        _current_uri = None
        return {
            "success": False,
            "message": str(e),
        }


def connect_to_database(
        host: str,
        port: int,
        user: str,
        password: str,
        dbname: str,
):
    result = connect_from_params(
        db_type="postgresql",
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )
    return result["success"]


def get_engine():
    return _current_engine


def get_current_uri():
    return _current_uri


def disconnect():
    global _current_engine, _current_uri
    _current_engine = None
    _current_uri = None
    print("З'єднання з БД розірвано")
