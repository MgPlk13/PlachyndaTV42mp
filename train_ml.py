import re
import os
import pickle
import argparse
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import (
    classification_report,
    roc_auc_score
)


def normalize_sql(sql: str) -> str:
    s = sql.strip()
    s = re.sub(r"'.*?'", " VAL_STR ", s)
    s = re.sub(r'".*?"', " VAL_STR ", s)
    s = re.sub(r"\b\d+\b", " VAL_NUM ", s)
    s = re.sub(r"\b0x[0-9A-Fa-f]+\b", " VAL_NUM ", s)
    s = re.sub(r"\s+", " ", s)
    s = s.lower()
    return s


def train(csv_path, model_out="ml_model.pkl", test_size=0.2, random_state=42):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"{csv_path} not found. CSV must contain columns 'sql' and 'label'"
        )

    df = pd.read_csv(csv_path)
    if "sql" not in df.columns or "label" not in df.columns:
        raise ValueError("CSV must contain columns 'sql' and 'label'")

    df = df.dropna(subset=["sql", "label"])
    df["sql_norm"] = df["sql"].apply(normalize_sql)

    X = df["sql_norm"].tolist()
    y = df["label"].astype(int).tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    vect = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        analyzer="word",
    )
    X_train_vect = vect.fit_transform(X_train)
    X_test_vect = vect.transform(X_test)

    lr = LogisticRegression(max_iter=1000, solver="liblinear")
    param_grid = {"C": [0.01, 0.1, 1, 10]}
    grid = GridSearchCV(lr, param_grid, cv=5, scoring="f1", n_jobs=-1)
    grid.fit(X_train_vect, y_train)
    best = grid.best_estimator_

    y_pred = best.predict(X_test_vect)
    y_prob = best.predict_proba(X_test_vect)[:, 1]

    print("=== Classification Report (test) ===")
    print(classification_report(y_test, y_pred, digits=4))
    print("ROC AUC:", roc_auc_score(y_test, y_prob))

    with open(model_out, "wb") as f:
        pickle.dump((vect, best), f)
    print(f"Model saved to {model_out}")

    from sklearn.metrics import precision_recall_curve

    prec, rec, thr = precision_recall_curve(y_test, y_prob)
    for p, r, t in zip(prec[::-1], rec[::-1], thr[::-1]):
        if p >= 0.9:
            print("Candidate threshold for precision>=0.9 ->", t)
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to dataset CSV (columns: sql,label)",
    )
    parser.add_argument(
        "--out",
        default="ml_model.pkl",
        help="Output pickle file (vectorizer, model)",
    )
    args = parser.parse_args()
    train(args.csv, model_out=args.out)
