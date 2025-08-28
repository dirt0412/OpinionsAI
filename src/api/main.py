from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from pathlib import Path

MODEL_PATH = Path("models/baseline_tfidf_lr.joblib")

app = FastAPI(title="OpinionsAI API")

class Inp(BaseModel):
    text: str

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Nie znaleziono modelu {MODEL_PATH}. Najpierw uruchom trening.")

model = joblib.load(MODEL_PATH)

@app.get("/")
def root():
    return {"status": "ok", "model": str(MODEL_PATH)}

@app.post("/predict/baseline")
def predict_baseline(inp: Inp):
    pred = int(model.predict([inp.text])[0])
    proba = float(model.predict_proba([inp.text])[0][1]) if hasattr(model, "predict_proba") else None
    return {"label": pred, "proba_positive": proba}
