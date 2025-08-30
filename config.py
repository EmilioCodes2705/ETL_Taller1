# -*- coding: utf-8 -*-
import os

# Carpeta base de salida
OUT_DIR = os.environ.get("OUT_DIR", ".")

# Rutas de artefactos
DB_PATH = os.path.join(OUT_DIR, "etl_workshop_dw.sqlite")
PLOTS_DIR = os.path.join(OUT_DIR, "plots")
STAR_SCHEMA_IMG = os.path.join(OUT_DIR, "star_schema.png")
README_PATH = os.path.join(OUT_DIR, "README_ETL_Workshop.md")
KPI_SQL_PATH = os.path.join(OUT_DIR, "kpis_queries.sql")
KPI_DIR = os.path.join(OUT_DIR, "kpis")

# Países foco para KPI por país-año
FOCUS_COUNTRIES = ("USA", "Brazil", "Colombia", "Ecuador")

# Bandas de años de experiencia
EXP_BINS = [-1, 1, 3, 5, 8, 1000]
EXP_LABELS = ["0-1", "2-3", "4-5", "6-8", "9+"]

os.makedirs(KPI_DIR, exist_ok=True)
