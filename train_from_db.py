import re
import pickle
import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve

from config_db import ANALYTICS_DATABASE_URI


def normalize_sql(sql: str) -> str:
    s = sql.strip()
    s = re.sub(r"'.*?'", " VAL_STR ", s)
    s = re.sub(r'".*?"', " VAL_STR ", s)
    s = re.sub(r"\b\d+\b", " VAL_NUM ", s)
    s = re.sub(r"\b0x[0-9A-Fa-f]+\b", " VAL_NUM ", s)
    s = re.sub(r"\s+", " ", s)
    s = s.lower()
    return s


def train_from_db(model_out="ml_model.pkl"):
    engine = create_engine(ANALYTICS_DATABASE_URI)

    df = pd.read_sql("SELECT query, status FROM attack_logs", engine)

    if df.empty:
        print("⚠ Немає даних в attack_logs. Спочатку запустіть симуляцію.")
        return {"success": False, "message": "Немає даних для навчання"}

    df["label"] = df["status"].apply(lambda x: 1 if x == "blocked" else 0)
    df["sql_norm"] = df["query"].apply(normalize_sql)

    X = df["sql_norm"].tolist()
    y = df["label"].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    vect = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.95)
    X_train_vect = vect.fit_transform(X_train)
    X_test_vect = vect.transform(X_test)

    lr = LogisticRegression(
        max_iter=1000,
        solver="liblinear",
        class_weight="balanced",
    )

    param_grid = {"C": [0.01, 0.1, 1, 10]}
    grid = GridSearchCV(lr, param_grid, cv=5, scoring="f1", n_jobs=-1)
    grid.fit(X_train_vect, y_train)
    best = grid.best_estimator_

    y_pred = best.predict(X_test_vect)
    y_prob = best.predict_proba(X_test_vect)[:, 1]

    report = classification_report(y_test, y_pred, digits=4)
    roc = roc_auc_score(y_test, y_prob)

    with open(model_out, "wb") as f:
        pickle.dump((vect, best), f)
    print(f"Модель оновлена і збережена в {model_out}")

    threshold = None
    prec, rec, thr = precision_recall_curve(y_test, y_prob)
    for p, r, t in zip(prec[::-1], rec[::-1], thr[::-1]):
        if p >= 0.9:
            threshold = float(t)
            break

    return {
        "success": True,
        "message": f"Модель оновлена і збережена в {model_out}",
        "report": report,
        "roc_auc": roc,
        "threshold": threshold,
    }


if __name__ == "__main__":
    result = train_from_db()
    print(result["report"] if result["success"] else result["message"])
    if result["success"]:
        print("ROC AUC:", result["roc_auc"])
