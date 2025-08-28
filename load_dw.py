# -*- coding: utf-8 -*-
import os
import sqlite3
import argparse
import pandas as pd
import numpy as np

# Esquema estrella
DDL_SQL = """
DROP TABLE IF EXISTS fact_application;
DROP TABLE IF EXISTS dim_candidate;
DROP TABLE IF EXISTS dim_experience;
DROP TABLE IF EXISTS dim_technology;
DROP TABLE IF EXISTS dim_seniority;
DROP TABLE IF EXISTS dim_country;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    application_date TEXT,
    year INTEGER,
    month INTEGER,
    day INTEGER
);

CREATE TABLE dim_country (
    country_key INTEGER PRIMARY KEY,
    country TEXT
);

CREATE TABLE dim_seniority (
    seniority_key INTEGER PRIMARY KEY,
    seniority TEXT
);

CREATE TABLE dim_technology (
    technology_key INTEGER PRIMARY KEY,
    technology TEXT
);

CREATE TABLE dim_experience (
    experience_key INTEGER PRIMARY KEY,
    experience_range TEXT
);

CREATE TABLE dim_candidate (
    candidate_key INTEGER PRIMARY KEY,
    email TEXT,
    first_name TEXT,
    last_name TEXT
);

CREATE TABLE fact_application (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_key INTEGER,
    date_key INTEGER,
    country_key INTEGER,
    seniority_key INTEGER,
    technology_key INTEGER,
    experience_key INTEGER,
    yoe REAL,
    code_challenge_score REAL,
    technical_interview_score REAL,
    hired INTEGER, -- 1 contratado, 0 no contratado
    FOREIGN KEY(candidate_key) REFERENCES dim_candidate(candidate_key),
    FOREIGN KEY(date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY(country_key) REFERENCES dim_country(country_key),
    FOREIGN KEY(seniority_key) REFERENCES dim_seniority(seniority_key),
    FOREIGN KEY(technology_key) REFERENCES dim_technology(technology_key),
    FOREIGN KEY(experience_key) REFERENCES dim_experience(experience_key)
);
"""

def build_dimensions(df):
    dim_date = df[["application_date"]].drop_duplicates().copy()
    dim_date["date_key"] = dim_date["application_date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["application_date"].dt.year
    dim_date["month"] = dim_date["application_date"].dt.month
    dim_date["day"] = dim_date["application_date"].dt.day

    dim_country = df[["country"]].drop_duplicates().copy()
    dim_country["country_key"] = np.arange(1, len(dim_country)+1)

    dim_seniority = df[["seniority"]].drop_duplicates().copy()
    dim_seniority["seniority_key"] = np.arange(1, len(dim_seniority)+1)

    dim_technology = df[["technology"]].drop_duplicates().copy()
    dim_technology["technology_key"] = np.arange(1, len(dim_technology)+1)

    labels = ["0-1","2-3","4-5","6-8","9+"]
    dim_experience = pd.DataFrame({"experience_range": labels})
    dim_experience["experience_key"] = np.arange(1, len(dim_experience)+1)

    dim_candidate = df[["email","first_name","last_name"]].drop_duplicates().copy()
    dim_candidate["candidate_key"] = np.arange(1, len(dim_candidate)+1)

    return {
        "dim_date": dim_date[["date_key","application_date","year","month","day"]],
        "dim_country": dim_country[["country_key","country"]],
        "dim_seniority": dim_seniority[["seniority_key","seniority"]],
        "dim_technology": dim_technology[["technology_key","technology"]],
        "dim_experience": dim_experience[["experience_key","experience_range"]],
        "dim_candidate": dim_candidate[["candidate_key","email","first_name","last_name"]]
    }

def build_fact(df, dims):
    # FKs
    date_map = dims["dim_date"].set_index("application_date")["date_key"].to_dict()
    country_map = dims["dim_country"].set_index("country")["country_key"].to_dict()
    seniority_map = dims["dim_seniority"].set_index("seniority")["seniority_key"].to_dict()
    technology_map = dims["dim_technology"].set_index("technology")["technology_key"].to_dict()
    experience_map = dims["dim_experience"].set_index("experience_range")["experience_key"].to_dict()
    candidate_map = dims["dim_candidate"].set_index("email")["candidate_key"].to_dict()

    fact = df.copy()
    fact["date_key"] = fact["application_date"].map(date_map)
    fact["country_key"] = fact["country"].map(country_map)
    fact["seniority_key"] = fact["seniority"].map(seniority_map)
    fact["technology_key"] = fact["technology"].map(technology_map)
    fact["experience_key"] = fact["experience_range"].map(experience_map)
    fact["candidate_key"] = fact["email"].map(candidate_map)

    # 🔥 hired = 1 si promedio > 7, else 0
    fact["hired"] = (((fact["code_challenge_score"] + fact["technical_interview_score"]) / 2) > 7).astype(int)

    return fact[[
        "candidate_key","date_key","country_key","seniority_key","technology_key","experience_key",
        "yoe","code_challenge_score","technical_interview_score","hired"
    ]]

def load_dw(df, db_path="etl_workshop_dw.sqlite"):
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    conn.executescript(DDL_SQL)

    dims = build_dimensions(df)
    fact = build_fact(df, dims)

    for name, ddf in dims.items():
        ddf.to_sql(name, conn, if_exists="append", index=False)
    fact.to_sql("fact_application", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    print(f"✅ Base de datos creada en {db_path} con columna 'hired' calculada por promedio.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crear DB Estrella con 'hired'")
    parser.add_argument("--csv", required=True, help="Ruta a candidates.csv")
    parser.add_argument("--out", default="etl_workshop_dw.sqlite", help="Ruta a DB SQLite de salida")
    args = parser.parse_args()

    # Usamos extract + transform de antes
    from extract import extract
    from transform import transform
    df = transform(extract(args.csv))
    load_dw(df, args.out)
