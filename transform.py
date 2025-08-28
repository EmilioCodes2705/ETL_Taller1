# -*- coding: utf-8 -*-
import argparse
import pandas as pd
import numpy as np
from config import EXP_BINS, EXP_LABELS

EXPECTED_COLS = [
    "first_name","last_name","email","country","application_date",
    "yoe","seniority","technology","code_challenge_score","technical_interview_score"
]

def validate_columns(df: pd.DataFrame):
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

def transform(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df)
    # Fechas
    df["application_date"] = pd.to_datetime(df["application_date"], errors="coerce")
    # Numéricos
    for c in ["yoe","code_challenge_score","technical_interview_score"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # Regla Hired
    df["hired"] = ((df["code_challenge_score"] >= 7) &
                   (df["technical_interview_score"] >= 7)).astype(int)
    # Rangos experiencia
    df["experience_range"] = pd.cut(df["yoe"].fillna(-1), bins=EXP_BINS, labels=EXP_LABELS)
    return df

if __name__ == "__main__":
    import json, sys
    parser = argparse.ArgumentParser(description="TRANSFORM: limpiar/derivar campos")
    parser.add_argument("--csv", required=True)
    args = parser.parse_args()

    # Pequeño runner para demo: reusa extract para cargar
    from extract import extract
    raw = extract(args.csv)
    tdf = transform(raw)
    print(tdf.head(5).to_string(index=False))
