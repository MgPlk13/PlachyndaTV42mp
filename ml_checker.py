import os
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sqlalchemy import create_engine, text

from config_db import DATABASE_URI

ML_LOW_THRESHOLD = 0.5
ML_HIGH_THRESHOLD = 0.8


class MLChecker:
    MODEL_FILE = "ml_model.pkl"

    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression()
        self.engine = create_engine(DATABASE_URI)

        if os.path.exists(self.MODEL_FILE):
            with open(self.MODEL_FILE, "rb") as f:
                self.vectorizer, self.model = pickle.load(f)
        else:
            self.vectorizer = TfidfVectorizer()
            self.model = LogisticRegression()

    def predict(self, sql: str):
        try:
            X = self.vectorizer.transform([sql])
            prob = self.model.predict_proba(X)[0][1]
            is_suspicious = prob >= ML_LOW_THRESHOLD
            return is_suspicious, prob
        except Exception:
            return False, 0.0

    def sandbox_execute(self, sql: str):
        try:
            with self.engine.begin() as conn:
                result = conn.execute(text(sql))
                rows = [dict(row) for row in result]
            return rows
        except Exception as e:
            return {"error": str(e)}

    def train(self, X_train, y_train):
        X_vect = self.vectorizer.fit_transform(X_train)
        self.model.fit(X_vect, y_train)
        with open(self.MODEL_FILE, "wb") as f:
            pickle.dump((self.vectorizer, self.model), f)
