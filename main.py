
import os
import argparse
from config import OUT_DIR, KPI_SQL_PATH
from extract import extract
from transform import transform
from load_dw import load_dw
from run_kpis import run_kpis
from visualize import visualize


def main(csv_path: str, out_dir: str = OUT_DIR, sql_path: str = KPI_SQL_PATH):
    os.environ["OUT_DIR"] = out_dir
    os.makedirs(out_dir, exist_ok=True)

    # 1) Extract + Transform
    df = transform(extract(csv_path))

    # 2) Load DW
    load_dw(df)

    # 3) Guardar SQL base si no existe (opcional)
    if not os.path.exists(sql_path):
        with open(sql_path, "w", encoding="utf-8") as f:
            f.write(open("kpis.sql", "r", encoding="utf-8").read())

    # 4) Ejecutar KPIs
    run_kpis(out_dir=out_dir)

    # 5) Visualizar
    visualize()



    print("✅ Pipeline completo.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MAIN: Orquestar ETL completo")
    parser.add_argument("--csv", required=True, help="Ruta a candidates.csv")
    parser.add_argument("--out", default=OUT_DIR, help="Carpeta de salida")
    parser.add_argument("--sql", default=KPI_SQL_PATH, help="Ruta a kpis.sql destino")
    args = parser.parse_args()
    main(args.csv, args.out, args.sql)
