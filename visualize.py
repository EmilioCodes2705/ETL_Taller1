# -*- coding: utf-8 -*-
import os
import argparse
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from config import DB_PATH, PLOTS_DIR

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def bar(df, x, y, title, out):
    plt.figure()
    plt.bar(df[x].astype(str), df[y])
    plt.title(title)
    plt.xlabel(x); plt.ylabel(y)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()

def line(df, x, y, title, out):
    plt.figure()
    plt.plot(df[x], df[y])
    plt.title(title)
    plt.xlabel(x); plt.ylabel(y)
    plt.tight_layout(); plt.savefig(out, dpi=150); plt.close()

def visualize(db_path: str = DB_PATH, out_dir: str = PLOTS_DIR):
    ensure_dir(out_dir)
    con = sqlite3.connect(db_path)

    q1 = """SELECT dt.technology, SUM(f.hired) AS hires
            FROM fact_application f
            JOIN dim_technology dt ON dt.technology_key = f.technology_key
            GROUP BY dt.technology ORDER BY hires DESC;"""
    q2 = """SELECT d.year, SUM(f.hired) AS hires
            FROM fact_application f
            JOIN dim_date d ON d.date_key = f.date_key
            GROUP BY d.year ORDER BY d.year;"""
    q3 = """SELECT s.seniority, SUM(f.hired) AS hires
            FROM fact_application f
            JOIN dim_seniority s ON s.seniority_key = f.seniority_key
            GROUP BY s.seniority ORDER BY hires DESC;"""
    q4 = """SELECT c.country, d.year, SUM(f.hired) AS hires
            FROM fact_application f
            JOIN dim_country c ON c.country_key = f.country_key
            JOIN dim_date d ON d.date_key = f.date_key
            WHERE c.country IN ('United States of America','Brazil','Colombia','Ecuador')
            GROUP BY c.country, d.year
            ORDER BY c.country, d.year;"""
    q5 = """SELECT e.experience_range, SUM(f.hired) AS hires
            FROM fact_application f
            JOIN dim_experience e ON e.experience_key = f.experience_key
            GROUP BY e.experience_range ORDER BY e.experience_range;"""

    df1 = pd.read_sql_query(q1, con)
    df2 = pd.read_sql_query(q2, con)
    df3 = pd.read_sql_query(q3, con)
    df4 = pd.read_sql_query(q4, con)
    df5 = pd.read_sql_query(q5, con)
    con.close()

    bar(df1, "technology", "hires", "Hires by Technology", os.path.join(out_dir, "hires_by_technology.png"))
    line(df2, "year", "hires", "Hires by Year", os.path.join(out_dir, "hires_by_year.png"))
    bar(df3, "seniority", "hires", "Hires by Seniority", os.path.join(out_dir, "hires_by_seniority.png"))

    # Country-year: líneas por país
    if not df4.empty:
        plt.figure()
        for country, sub in df4.groupby("country"):
            plt.plot(sub["year"], sub["hires"], label=country)
        plt.title("Hires by Country over Years (United States of America, Brazil, Colombia, Ecuador)")
        plt.xlabel("year"); plt.ylabel("hires")
        plt.legend(); plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "hires_by_country_over_years.png"), dpi=150)
        plt.close()

    bar(df5, "experience_range", "hires", "Hires by Experience Range", os.path.join(out_dir, "hires_by_experience.png"))
    print(f"Gráficas generadas en: {out_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VISUALIZE: generar gráficos de KPIs")
    parser.add_argument("--db", default=DB_PATH)
    parser.add_argument("--out", default=PLOTS_DIR)
    args = parser.parse_args()
    visualize(args.db, args.out)
