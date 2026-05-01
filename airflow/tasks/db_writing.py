import pandas as pd
from sqlalchemy import create_engine
from airflow.models import Variable
from sqlalchemy import text

BUCKET_NAME = "storage_bucket_groppo"
PROCESSED_DIR = f"gs://{BUCKET_NAME}/data/processed"
DB_PORT = "5432"

def run():
    db_user = Variable.get("DB_USER")
    db_pass = Variable.get("DB_PASS")
    db_host = Variable.get("DB_HOST")
    db_name = Variable.get("DB_NAME")
    print("Leyendo archivos finales desde Storage...")
    ctr = pd.read_csv(f"{PROCESSED_DIR}/top_ctr.csv")
    prod = pd.read_csv(f"{PROCESSED_DIR}/top_product.csv")

    print("Uniendo resultados...")
    final_df = pd.concat([ctr, prod], ignore_index=True)

    final_df = final_df.sort_values(
        ["run_date", "advertiser_id", "model_name", "rank"]
    ).reset_index(drop=True)

    print("Validando columnas...")
    expected_cols = ["run_date", "advertiser_id", "model_name", "rank", "product_id", "score"]
    if list(final_df.columns) != expected_cols:
        raise ValueError(f"Columnas inesperadas: {list(final_df.columns)}")

    print("Guardando consolidado en Storage...")
    final_df.to_csv(f"{PROCESSED_DIR}/recommendations_ready.csv", index=False)

    print("Escribiendo en Cloud SQL (modo append para historial)...")
    engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{DB_PORT}/{db_name}")
    fecha_ejecucion = final_df['run_date'].iloc[0]
    with engine.begin() as conn:
       conn.execute(text(f"DELETE FROM recommendations WHERE run_date = '{fecha_ejecucion}'"))
    final_df.to_sql("recommendations", engine, if_exists="append", index=False)

    print("DBWriting terminado")
    print(f"Filas totales agregadas: {len(final_df)}")
