# Skrypt do wygenerowania próbnego zbioru danych (jeśli nie masz data/reviews.csv)
import random
import csv
from pathlib import Path


random.seed(42)


POSITIVE = [
"Świetny produkt, działa bez zarzutu!",
"Bardzo dobra jakość w stosunku do ceny.",
"Polecam, szybka dostawa i super obsługa.",
"Jestem zadowolony, wszystko zgodnie z opisem.",
"Najlepszy zakup w tym roku!"
]


NEGATIVE = [
"Słaba jakość, nie polecam.",
"Produkt przyszedł uszkodzony, dramat.",
"Pieniądze wyrzucone w błoto.",
"Obsługa klienta nie odpowiada.",
"Nie działa jak powinien, zwróciłem."
]


OUT = Path("data/reviews.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)


rows = []
for _ in range(2500):
    rows.append([random.choice(POSITIVE), 1])
    rows.append([random.choice(NEGATIVE), 0])


with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["text", "label"])
    w.writerows(rows)


print(f"Zapisano {len(rows)} wierszy do {OUT}")