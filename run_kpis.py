# -*- coding: utf-8 -*-
from config import DB_PATH, KPI_SQL_PATH, KPI_DIR, OUT_DIR
import os
import argparse
import sqlite3
import pandas as pd

def run_kpis(db_path: str = DB_PATH, sql_path: str = KPI_SQL_PATH, kpi_dir: str = KPI_DIR):
    os.makedirs(kpi_dir, exist_ok=True)
    con = sqlite3.connect(db_path)
    with open(sql_path, "r", encoding="utf-8") as f:
        queries = f.read().split(";")
        for i, query in enumerate(queries):
            query = query.strip()
            if query and not query.startswith("--"):
                df = pd.read_sql_query(query, con)
                df.to_csv(os.path.join(kpi_dir, f'kpi_{i+1:02d}.csv'), index=False)
    con.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RUN KPIs: ejecutar consultas SQL y exportar CSVs")
    parser.add_argument("--db", default=DB_PATH)
    parser.add_argument("--sql", default=KPI_SQL_PATH)
    parser.add_argument("--out", default=OUT_DIR)
    args = parser.parse_args()
    run_kpis(args.db, args.sql, args.out)
