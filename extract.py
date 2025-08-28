# -*- coding: utf-8 -*-
import csv
import argparse
import pandas as pd

def detect_delimiter(csv_path: str, sample_size: int = 4096) -> str:
    with open(csv_path, "r", encoding="utf-8") as f:
        sample = f.read(sample_size)
    try:
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter
    except Exception:
        return ";"  # default común en exportaciones ES

def extract(csv_path: str) -> pd.DataFrame:
    delim = detect_delimiter(csv_path)
    df = pd.read_csv(csv_path, sep=delim)
    # Normaliza nombres de columnas
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EXTRACT: leer CSV")
    parser.add_argument("--csv", required=True, help="Ruta a candidates.csv")
    args = parser.parse_args()
    df = extract(args.csv)
    print(df.head(5).to_string(index=False))
