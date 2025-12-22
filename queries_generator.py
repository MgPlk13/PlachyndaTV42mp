import random

SAFE_TEMPLATES = [
    "SELECT * FROM {table} LIMIT {limit};",
    (
        "SELECT {column} FROM {table} "
        "WHERE {column} IS NOT NULL LIMIT {limit};"
    ),
    "SELECT COUNT(*) FROM {table};",
    "SELECT DISTINCT {column} FROM {table};",
    (
        "SELECT {column}, COUNT(*) FROM {table} "
        "GROUP BY {column} ORDER BY COUNT(*) DESC LIMIT {limit};"
    ),
    "SELECT * FROM {table} WHERE {column} LIKE 'A%';",
    "SELECT * FROM {table} ORDER BY {column} DESC LIMIT {limit};",
]

MALICIOUS_TEMPLATES = [
    "SELEC FROM {table};",
    "SELECT * FORM {table};",
    "SELECT * FROM WHERE id = 1;",
    "SELECT * FROM {table} WHERE ;",
    "SELECT * FROM non_existing_table;",
    "SELECT fake_column FROM {table};",
    "DROP TABLE {table};",
    "DELETE FROM {table};",
    "TRUNCATE TABLE {table};",
    "UPDATE {table} SET {column} = 'HACKED';",
    "INSERT INTO {table} VALUES (9999, 'Evil', 'Hacker');",
    "SELECT 1/0;",
    "SELECT * FROM {table} WHERE {column} = 'abc';",
    "SELECT * FROM {table} WHERE {column} = '' OR '1'='1';",
    (
        "SELECT * FROM {table} WHERE {column} = '' "
        "UNION SELECT version(), current_user, now();--';"
    ),
    "SELECT * FROM {table}; DROP TABLE {table};--",
]

PAGILA_TABLES = [
    "actor",
    "film",
    "customer",
    "store",
    "payment",
    "rental",
    "category",
    "staff",
    "language",
    "inventory",
    "address",
]

PAGILA_COLUMNS = [
    "actor_id",
    "first_name",
    "last_name",
    "title",
    "release_year",
    "amount",
    "payment_id",
    "customer_id",
    "store_id",
    "name",
    "district",
]


def generate_safe_queries(n=100):
    queries = []
    for _ in range(n):
        template = random.choice(SAFE_TEMPLATES)
        table = random.choice(PAGILA_TABLES)
        column = random.choice(PAGILA_COLUMNS)
        limit = random.randint(1, 50)
        q = template.format(table=table, column=column, limit=limit)
        queries.append(q)
    return queries


def generate_malicious_queries(n=100):
    queries = []
    for _ in range(n):
        template = random.choice(MALICIOUS_TEMPLATES)
        table = random.choice(PAGILA_TABLES)
        column = random.choice(PAGILA_COLUMNS)
        q = template.format(table=table, column=column)
        queries.append(q)
    return queries


if __name__ == "__main__":
    safe = generate_safe_queries(5)
    mal = generate_malicious_queries(5)
    print("SAFE:", *safe, sep="\n- ")
    print("\nMALICIOUS:", *mal, sep="\n- ")
