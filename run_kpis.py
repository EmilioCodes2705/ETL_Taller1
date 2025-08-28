# -*- coding: utf-8 -*-
import os
import argparse
import sqlite3
import pandas as pd
from config import DB_PATH, KPI_SQL_PATH, OUT_DIR

def run_kpis(db_path: str = DB_PATH, sql_path: str = KPI_SQL_PATH, out_dir: str = OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Separamos por ; al final de cada sentencia conservando SQL multi-línea
    statements = [s.strip() for s in content.split(";") if s.strip()]
    con = sqlite3.connect(db_path)
    for i, stmt in enumerate(statements, start=1):
        try:
            df = pd.read_sql_query(stmt, con)
            df.to_csv(os.path.join(out_dir, f"kpi_{i:02d}.csv"), index=False, encoding="utf-8")
            print(f"KPI {i:02d} OK -> kpi_{i:02d}.csv")
        except Exception as e:
            print(f"KPI {i:02d} ERROR: {e}")
    con.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RUN KPIs: ejecutar consultas SQL y exportar CSVs")
    parser.add_argument("--db", default=DB_PATH)
    parser.add_argument("--sql", default=KPI_SQL_PATH)
    parser.add_argument("--out", default=OUT_DIR)
    args = parser.parse_args()
    run_kpis(args.db, args.sql, args.out)
