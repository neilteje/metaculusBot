import pandas as pd
import re
import csv
import datetime

CUTOFF = datetime.date(2023, 10, 1)
date_pattern = re.compile(r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b")
with open("perplexityLeakage.csv") as f:
    reader = csv.reader(f)
    header = next(reader, None)
    for row in reader:
        if len(row) < 5:
            continue
        q, cutoff_date, cutoff_txt, unrestricted_txt = row[1:5]
        text = cutoff_txt + unrestricted_txt
        dates = []
        for y, m, d in date_pattern.findall(text):
            dt = datetime.date(int(y), int(m), int(d))
            if dt > CUTOFF:
                dates.append(str(dt))
        if dates:
            print(f"[Leakage]{q} cites post-cutoff dates: {', '.join(sorted(set(dates)))}")

df = pd.read_csv("perplexityLeakage.csv")
expected_cols = ["timestamp", "question", "cutoff_date", "cutoff_answer", "unrestricted_answer"]
if len(df.columns) < 5 or "cutoff_answer" not in df.columns:
    df.columns = expected_cols[:len(df.columns)]

def detect_leakage(row):
    cutoff = str(row.get("cutoff_answer", ""))
    unrestricted = str(row.get("unrestricted_answer", ""))
    text = (cutoff + unrestricted).lower()
    if "metaculus" in text or "forecast" in text or "question" in text:
        return False
    dates = [
        r"\b202[4-5][-/.]\d{1,2}[-/.]\d{1,2}\b", 
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s*202[4-5]\b"
    ]
    allRewgex = "|".join(dates)
    context_pattern = re.compile(r"(reported|updated|as of|since).{0,30}" + allRewgex)
    return bool(context_pattern.search(text))

df["leak_detected"] = df.apply(detect_leakage, axis=1)
print(df[["question", "leak_detected"]])
print(f"\nLeakage detected")