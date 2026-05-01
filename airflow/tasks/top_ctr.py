import pandas as pd

BUCKET_NAME = "storage_bucket_groppo"
PROCESSED_DIR = f"gs://{BUCKET_NAME}/data/processed"

def run(ds):
    print("Leyendo datos filtrados...")
    ads = pd.read_csv(f"{PROCESSED_DIR}/{ds}/ads_views_filtered.csv")

    print("Calculando CTR...")
    ctr = ads.groupby(["advertiser_id", "product_id", "type"]).size().unstack(fill_value=0)

    if "click" not in ctr.columns:
        ctr["click"] = 0
    if "impression" not in ctr.columns:
        ctr["impression"] = 0

    ctr = ctr[ctr["impression"] > 0]
    ctr["score"] = ctr["click"] / ctr["impression"]
    ctr = ctr.reset_index()

    print("Generando ranking...")
    ctr = ctr.sort_values(["advertiser_id", "score"], ascending=[True, False])
    ctr["rank"] = ctr.groupby("advertiser_id").cumcount() + 1
    ctr = ctr[ctr["rank"] <= 20].copy()

    ctr["model_name"] = "top_ctr"
    ctr["run_date"] = ds

    ctr = ctr[["run_date", "advertiser_id", "model_name", "rank", "product_id", "score"]]

    print("Guardando resultados en Storage...")
    ctr.to_csv(f"{PROCESSED_DIR}/{ds}/top_ctr.csv", index=False)

    print("Top CTR terminado")
