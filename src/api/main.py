from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import re
from typing import List, Dict
import joblib
import pandas as pd

# === CORS (frontend na 4200) ===
app = FastAPI(title="OpinionsAI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Model bazowy TFIDF+LR ===
MODEL_PATH = Path("models/baseline_tfidf_lr.joblib")
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Nie znaleziono modelu {MODEL_PATH}. Najpierw uruchom trening.")

model = joblib.load(MODEL_PATH)

class Inp(BaseModel):
    text: str

@app.get("/")
def root():
    return {"status": "ok", "model": str(MODEL_PATH)}

@app.post("/predict/baseline")
def predict_baseline(inp: Inp):
    pred = int(model.predict([inp.text])[0])
    proba = float(model.predict_proba([inp.text])[0][1]) if hasattr(model, "predict_proba") else None
    return {"label": pred, "proba_positive": proba}

# === Analiza aspektów (prosta: słowa-klucze + sentyment zdań) ===
ASPECTS: Dict[str, List[str]] = {
    "bateria": ["bateria", "czas pracy", "ładowanie", "powerbank"],
    "ekran": ["ekran", "display", "rozdzielczość", "kolory", "jasność"],
    "wydajność": ["wydajność", "szybkość", "lagi", "płynność"],
    "cena": ["cena", "koszt", "drogi", "tani", "opłacalny"],
    "dostawa": ["dostawa", "kurier", "przesyłka", "wysyłka"],
    "obsługa": ["obsługa", "support", "serwis", "reklamacja"],
}

def split_sentences(text: str) -> List[str]:
    # bardzo prosty split – na później możesz użyć spaCy
    return [s.strip() for s in re.split(r"[.!?]\s+", text) if s.strip()]

def detect_aspects(sent: str) -> List[str]:
    s = sent.lower()
    hits = []
    for asp, keys in ASPECTS.items():
        if any(k in s for k in keys):
            hits.append(asp)
    return hits

class AnalyzeOut(BaseModel):
    overall_label: int
    proba_positive: float | None
    aspects: List[Dict[str, object]]

@app.post("/analyze", response_model=AnalyzeOut)
def analyze(inp: Inp):
    # ocena ogólna
    pred = int(model.predict([inp.text])[0])
    proba = float(model.predict_proba([inp.text])[0][1]) if hasattr(model, "predict_proba") else None

    # aspekty po zdaniach
    sents = split_sentences(inp.text)
    aspect_votes: Dict[str, List[int]] = {a: [] for a in ASPECTS}
    aspect_snips: Dict[str, List[str]] = {a: [] for a in ASPECTS}

    for s in sents:
        asps = detect_aspects(s)
        if not asps:
            continue
        lab = int(model.predict([s])[0])  # sentyment zdania
        for a in asps:
            aspect_votes[a].append(lab)
            if len(aspect_snips[a]) < 3:
                aspect_snips[a].append(s)

    aspects_out = []
    for a, votes in aspect_votes.items():
        if not votes:
            continue
        score = sum(votes) / len(votes)  # 0..1 udział pozytywnych
        aspects_out.append({
            "name": a,
            "score": round(score, 3),
            "label": 1 if score >= 0.5 else 0,
            "examples": aspect_snips[a],
            "count": len(votes),
        })

    aspects_out.sort(key=lambda x: x["score"], reverse=True)
    return {"overall_label": pred, "proba_positive": proba, "aspects": aspects_out}

# === Trend miesięczny dla produktu na bazie reviews_extended.csv ===
EXT_CSV = Path("data/reviews_extended.csv")

@app.get("/trend/{product_id}")
def trend(product_id: str):
    if not EXT_CSV.exists():
        raise HTTPException(status_code=404, detail="Brak data/reviews_extended.csv – wygeneruj lub dodaj plik.")
    df = pd.read_csv(EXT_CSV, parse_dates=["timestamp"])
    dff = df[df["product_id"] == product_id].copy()
    if dff.empty:
        return {"product_id": product_id, "product_name": None, "points": []}
    dff["month"] = dff["timestamp"].dt.to_period("M").astype(str)
    summary = dff.groupby("month").agg(
        pos_rate=("label", "mean"),
        avg_rating=("rating", "mean"),
        count=("label", "size")
    ).reset_index().sort_values("month")
    product_name = dff["product_name"].iloc[0]
    points = [
        {"month": r["month"], "pos_rate": round(float(r["pos_rate"]), 3),
         "avg_rating": round(float(r["avg_rating"]), 2), "count": int(r["count"])}
        for _, r in summary.iterrows()
    ]
    return {"product_id": product_id, "product_name": product_name, "points": points}
