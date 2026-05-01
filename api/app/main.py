import os
from enum import Enum
from fastapi import FastAPI
import psycopg2
from datetime import date as Date, timedelta
from typing import Optional

app = FastAPI(title="AdTech Recommender API", version="1.0.0")

class ModelName(str, Enum):
    top_ctr = "top_ctr"
    top_product = "top_product"

def get_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        sslmode="require",
    )

@app.get("/recommendations/{adv}/{modelo}", summary="Recomendaciones del día", description="Retorna el ranking de productos recomendados para un advertiser y modelo dado. Si no se indica fecha, retorna las recomendaciones de hoy.")
def get_recommendations(adv: str, modelo: ModelName, date: Optional[Date] = None):
    run_date = date or Date.today()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product_id, score
        FROM recommendations
        WHERE advertiser_id = %s AND model_name = %s AND run_date = %s
        ORDER BY rank
    """, (adv, modelo, run_date))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {
        "advertiser_id": adv,
        "model_name": modelo,
        "date": str(run_date),
        "recommendations": [{"product_id": r[0], "score": r[1]} for r in rows],
    }

@app.get("/history/{adv}", summary="Historial de recomendaciones", description="Retorna las recomendaciones de los últimos 7 días disponibles para un advertiser, agrupadas por fecha y modelo.")
def get_history(adv: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT run_date, model_name, product_id, rank, score
        FROM recommendations
        WHERE advertiser_id = %s AND run_date >= %s
        ORDER BY run_date DESC, model_name, rank
    """, (adv, Date.today() - timedelta(days=7)))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"run_date": str(r[0]), "model_name": r[1], "product_id": r[2], "rank": r[3], "score": r[4]} for r in rows]

@app.get("/stats/", summary="Estadísticas generales", description="Retorna el total de advertisers y la cantidad de días con recomendaciones disponibles por advertiser.")
def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(DISTINCT advertiser_id) FROM recommendations")
    total_advertisers = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT advertiser_id, COUNT(DISTINCT run_date) as dias
        FROM recommendations
        GROUP BY advertiser_id
        ORDER BY dias DESC
    """)
    advertisers_por_dia = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return {
        "total_advertisers": total_advertisers,
        "advertisers_por_dia": [{"advertiser_id": r[0], "dias": r[1]} for r in advertisers_por_dia]
    }
