import csv
import random

OUT = "ml_sql_dataset.csv"
N_SAFE = 600
N_MAL = 400
random.seed(42)

safe_templates = [
    "SELECT {cols} FROM {table} WHERE {pk} = {val};",
    "SELECT {cols} FROM {table} LIMIT {n};",
    "SELECT {cols} FROM {table} ORDER BY {col} DESC LIMIT {n};",
    "SELECT {cols} FROM {table} WHERE {col} LIKE '%{term}%';",
    "SELECT COUNT(*) FROM {table};",
    "SELECT a.{c1}, b.{c2} FROM {t1} a JOIN {t2} b ON a.{fk}=b.{pk} WHERE a.{col} > {num};"
]

tables = {
    "actor": ["actor_id", "first_name", "last_name", "last_update"],
    "customer": ["customer_id", "first_name", "last_name", "email"],
    "film": ["film_id", "title", "description", "release_year"],
    "payment": ["payment_id", "customer_id", "amount", "payment_date"],
    "users": ["id", "username", "email", "created_at"]
}

mal_templates = [
    "'; DROP TABLE {table}; --",
    "' OR '1'='1'; --",
    "' UNION SELECT {cols} FROM {table} --",
    "'; UPDATE {table} SET {col} = {val} WHERE {pk} = {val}; --",
    "'; INSERT INTO {table} ({cols}) VALUES ({vals}); --",
    "'; SELECT pg_sleep(10); --",
    "'; EXEC xp_cmdshell('dir'); --",
    "' OR 1=1; --",
    "'; DELETE FROM {table} WHERE {pk} = {val}; --"
]


def rnd_col(t):
    return random.choice(tables[t])


def rnd_cols(t, k=2):
    cols = random.sample(tables[t], min(k, len(tables[t])))
    return ", ".join(cols)


def gen_safe(n):
    out = []
    for _ in range(n):
        t = random.choice(list(tables.keys()))
        tpl = random.choice(safe_templates)
        cols = rnd_cols(t, k=random.randint(1, 2))
        pk = tables[t][0]
        val = str(random.randint(1, 200))
        col = rnd_col(t)
        nlim = random.randint(1, 50)
        term = random.choice(["John", "Action", "2020", "Smith", "com"])
        t2 = random.choice(list(tables.keys()))
        c1 = rnd_col(t)
        c2 = rnd_col(t2)
        fk = rnd_col(t)
        out.append(tpl.format(
            cols=cols, table=t, pk=pk, val=val,
            col=col, n=nlim, term=term, t1=t, t2=t2,
            c1=c1, c2=c2, fk=fk, num=nlim
        ))
    return out


def gen_mal(n):
    out = []
    for _ in range(n):
        t = random.choice(list(tables.keys()))
        tpl = random.choice(mal_templates)
        cols = rnd_cols(t, k=random.randint(1, 2))
        pk = tables[t][0]
        val = str(random.randint(1, 200))
        col = rnd_col(t)
        vals = ", ".join(["'{}'".format(random.choice(["x", "admin", "test"])) for _ in range(2)])
        out.append(tpl.format(table=t, cols=cols, pk=pk, val=val, col=col, vals=vals))
    return out


if __name__ == "__main__":
    rows = []
    rows += [(q, 0) for q in gen_safe(N_SAFE)]
    rows += [(q, 1) for q in gen_mal(N_MAL)]
    random.shuffle(rows)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sql", "label"])
        for sql, lbl in rows:
            w.writerow([sql, lbl])
    print(f"Generated {len(rows)} rows -> {OUT}")
