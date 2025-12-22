import csv
import os
import random
from datetime import datetime

from .schema_explorer import list_tables, get_table_schema

SAFE_SELECT_TEMPLATES = [
    "SELECT * FROM {table} LIMIT {limit};",
    "SELECT {column} FROM {table} WHERE {column} IS NOT NULL LIMIT {limit};",
    "SELECT COUNT(*) FROM {table};",
    "SELECT DISTINCT {column} FROM {table};",
    (
        "SELECT {column}, COUNT(*) FROM {table} GROUP BY {column} "
        "ORDER BY COUNT(*) DESC LIMIT {limit};"
    ),
    "SELECT * FROM {table} WHERE {column} LIKE 'A%';",
    "SELECT * FROM {table} ORDER BY {column} DESC LIMIT {limit};",
    "SELECT * FROM {table} WHERE {column} BETWEEN 10 AND 100;",
    (
        "SELECT * FROM {table} WHERE {column} IN "
        "(SELECT {column} FROM {table} LIMIT 5);"
    ),
    (
        "SELECT {column}, AVG({column}) FROM {table} GROUP BY {column} "
        "HAVING AVG({column}) > 10;"
    ),
    "SELECT * FROM {table} WHERE {column} = (SELECT MAX({column}) FROM {table});",
    "SELECT * FROM {table} WHERE {column} IS NULL;",
    "SELECT * FROM {table} WHERE {column} > 0 ORDER BY {column} ASC LIMIT {limit};",
    "SELECT {column} FROM {table} WHERE {column} LIKE '%test%';",
]

SAFE_JOIN_TEMPLATES = [
    (
        "SELECT {t1}.{c1}, {t2}.{c2} FROM {t1} JOIN {t2} "
        "ON {t1}.{c1} = {t2}.{c2} LIMIT {limit};"
    ),
    "SELECT COUNT(*) FROM {t1} LEFT JOIN {t2} ON {t1}.{c1} = {t2}.{c2};",
    (
        "SELECT {t1}.{c1}, {t2}.{c2} FROM {t1} INNER JOIN {t2} "
        "ON {t1}.{c1} = {t2}.{c2} WHERE {t1}.{c1} IS NOT NULL LIMIT {limit};"
    ),
    (
        "SELECT * FROM {t1} JOIN {t2} ON {t1}.{c1} = {t2}.{c2} "
        "WHERE {t1}.{c1} > 0 LIMIT {limit};"
    ),
]

SAFE_TEMPLATES = SAFE_SELECT_TEMPLATES + SAFE_JOIN_TEMPLATES

MALICIOUS_SYNTAX_TEMPLATES = [
    "SELEC FROM {table};",
    "SELECT * FORM {table};",
    "SELECT * FROM WHERE id = 1;",
    "SELECT * FROM {table} WHERE ;",
]

MALICIOUS_DDL_TEMPLATES = [
    "DROP TABLE {table};",
    "TRUNCATE TABLE {table};",
    "DELETE FROM {table};",
    "UPDATE {table} SET {column} = 'HACKED';",
    "INSERT INTO {table} VALUES (9999, 'Evil', 'Hacker');",
]

MALICIOUS_INJECTION_TEMPLATES = [
    "SELECT * FROM {table} WHERE {column} = '' OR '1'='1';",
    (
        "SELECT * FROM {table} WHERE {column} = '' "
        "UNION SELECT version(), current_user, now();--';"
    ),
    "SELECT * FROM {table}; DROP TABLE {table};--",
    "SELECT * FROM {table} WHERE {column} = ''; exec xp_cmdshell('dir'); --",
    "SELECT * FROM {table} UNION SELECT username, password FROM users; --",
]

MALICIOUS_RUNTIME_TEMPLATES = [
    "SELECT 1/0;",
    "SELECT * FROM non_existing_table;",
    "SELECT fake_column FROM {table};",
]

MALICIOUS_TEMPLATES = (
        MALICIOUS_SYNTAX_TEMPLATES
        + MALICIOUS_DDL_TEMPLATES
        + MALICIOUS_INJECTION_TEMPLATES
        + MALICIOUS_RUNTIME_TEMPLATES
)


def _get_random_column(table):
    columns = get_table_schema(table)
    if not columns:
        return "id"
    return random.choice(columns)["name"]


def _get_two_distinct_tables():
    tables = list_tables()
    if len(tables) < 2:
        return tables[0], tables[0]
    return random.sample(tables, 2)


def generate_safe_queries(num_queries=300):
    queries = []
    tables = list_tables()
    if not tables:
        raise ValueError("У базі даних немає таблиць")

    for _ in range(num_queries):
        template = random.choice(SAFE_TEMPLATES)
        table = random.choice(tables)
        column = _get_random_column(table)
        limit = random.randint(1, 50)

        if "{t1}" in template:
            t1, t2 = _get_two_distinct_tables()
            c1 = _get_random_column(t1)
            c2 = _get_random_column(t2)
            q = template.format(t1=t1, t2=t2, c1=c1, c2=c2, limit=limit)
        else:
            q = template.format(table=table, column=column, limit=limit)

        queries.append((q, 0))
    return queries


def generate_malicious_queries(num_queries=300):
    queries = []
    tables = list_tables()
    if not tables:
        raise ValueError("У базі даних немає таблиць")

    for _ in range(num_queries):
        template = random.choice(MALICIOUS_TEMPLATES)
        table = random.choice(tables)
        column = _get_random_column(table)
        q = template.format(table=table, column=column)
        queries.append((q, 1))
    return queries


def build_dataset(
        filename: str,
        num_safe=300,
        num_malicious=300,
        output_dir="datasets",
):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_path = os.path.join(output_dir, f"{filename}_{timestamp}.csv")

    safe_queries = generate_safe_queries(num_safe)
    malicious_queries = generate_malicious_queries(num_malicious)

    with open(full_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["query", "label"])
        for q, lbl in safe_queries + malicious_queries:
            writer.writerow([q, lbl])

    print(f"Датасет збережено: {full_path}")
    print(
        f"Кількість запитів: {len(safe_queries)} безпечних + "
        f"{len(malicious_queries)} шкідливих"
    )
    return full_path


if __name__ == "__main__":
    build_dataset(
        filename="universal_dataset",
        num_safe=200,
        num_malicious=200,
    )
