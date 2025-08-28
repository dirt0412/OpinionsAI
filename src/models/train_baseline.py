from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

CSV_EXT = Path("data/reviews_extended.csv")
CSV_BASIC = Path("data/reviews.csv")
MODEL_OUT = Path("models/baseline_tfidf_lr.joblib")
MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)

if CSV_EXT.exists():
    df = pd.read_csv(CSV_EXT)
elif CSV_BASIC.exists():
    df = pd.read_csv(CSV_BASIC)
else:
    raise FileNotFoundError("Brak data/reviews_extended.csv i data/reviews.csv")

# Oczekujemy kolumn 'text' i 'label'
if not {"text","label"}.issubset(df.columns):
    raise ValueError("CSV musi mieć kolumny 'text' i 'label'")

X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
)

pipe = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=50000, ngram_range=(1,2))),
    ("clf", LogisticRegression(max_iter=1000, n_jobs=-1))
])

pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
print(classification_report(y_test, y_pred))

joblib.dump(pipe, MODEL_OUT)
print(f"Zapisano model do {MODEL_OUT.resolve()}")
