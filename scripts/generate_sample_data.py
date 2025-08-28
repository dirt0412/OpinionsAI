# scripts/generate_sample_data.py
import argparse, csv, random
from pathlib import Path
from datetime import datetime, timedelta

random.seed(1337)

POSITIVE = [
    "Świetny produkt, polecam!", "Bardzo dobra jakość w stosunku do ceny.",
    "Działa bez zarzutu.", "Jestem zadowolony, wszystko zgodnie z opisem.",
    "Najlepszy zakup w tym roku!", "Obsługa klienta na plus.",
    "Szybka dostawa i dobra komunikacja.", "Solidne wykonanie, wygląda elegancko.",
    "Spełnia wszystkie oczekiwania.", "Cena adekwatna do jakości.",
    "Łatwa konfiguracja, intuicyjna obsługa.", "Dobre materiały, trwałe wykończenie.",
    "Zaskakująco wydajny.", "Bateria trzyma długo.", "Ekran bardzo wyraźny i jasny.",
    "Cicha praca urządzenia.", "Prosty montaż.", "Estetyczny design.",
    "Dobra relacja jakości do ceny.", "Idealny na prezent."
]

NEGATIVE = [
    "Słaba jakość, nie polecam.", "Produkt przyszedł uszkodzony, dramat.",
    "Pieniądze wyrzucone w błoto.", "Obsługa klienta nie odpowiada.",
    "Nie działa jak powinien, zwróciłem.", "Bardzo głośna praca urządzenia.",
    "Bateria szybko się rozładowuje.", "Ekran ma słabe kolory.",
    "Instrukcja niezrozumiała.", "Problemy z konfiguracją.",
    "Wysyłka trwała zbyt długo.", "Cena nieadekwatna do jakości."
]

PRODUCTS = [
    ("P001", "Smartfon Nova X1"), ("P002", "Laptop Aero 15"),
    ("P003", "Słuchawki Bass Pro"), ("P004", "Telewizor Vision 55\""),
    ("P005", "Smartwatch Pulse S"), ("P006", "Głośnik Bluetooth Wave"),
    ("P007", "Kamera Action Go"), ("P008", "Tablet Note 10"),
    ("P009", "Klawiatura Mech K"), ("P010", "Mysz Laser Pro"),
]
SOURCES = ["allegro", "amazon", "ceneo", "opineo", "mediaexpert", "euro", "komputronik"]

def rand_ts():
    start = datetime(2024,1,1); end = datetime(2025,8,28,23,59,59)
    dt = start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))
    return dt.strftime("%Y-%m-%dT%H:%M:%S")

def gen_basic(path: Path, total: int):
    pos = total // 2; neg = total - pos
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["text","label"])
        for _ in range(pos): w.writerow([random.choice(POSITIVE), 1])
        for _ in range(neg): w.writerow([random.choice(NEGATIVE), 0])
    print(f"[OK] Zapisano {total} wierszy do {path}")

def gen_extended(path: Path, total: int):
    pos = total // 2; neg = total - pos
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["product_id","product_name","timestamp","source","rating","text","label"])
        for _ in range(pos):
            pid, pname = random.choice(PRODUCTS)
            w.writerow([pid, pname, rand_ts(), random.choice(SOURCES), random.choice([4,5]), random.choice(POSITIVE), 1])
        for _ in range(neg):
            pid, pname = random.choice(PRODUCTS)
            w.writerow([pid, pname, rand_ts(), random.choice(SOURCES), random.choice([1,2]), random.choice(NEGATIVE), 0])
    print(f"[OK] Zapisano {total} wierszy do {path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--extended", action="store_true", help="generuj data/reviews_extended.csv")
    ap.add_argument("--basic", action="store_true", help="generuj data/reviews.csv")
    ap.add_argument("--size", type=int, default=5000, help="łączna liczba rekordów (domyślnie 5000)")
    args = ap.parse_args()

    if not args.extended and not args.basic:
        # jeśli nie podano flag – generuj oba
        args.extended = True; args.basic = True

    if args.basic:
        gen_basic(Path("data/reviews.csv"), args.size)
    if args.extended:
        gen_extended(Path("data/reviews_extended.csv"), args.size)
