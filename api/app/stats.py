from datetime import date as Date


def total_advertisers(cursor):
    cursor.execute("SELECT COUNT(DISTINCT advertiser_id) FROM recommendations")
    return {
        "descripcion": "Cantidad total de advertisers con al menos una recomendación",
        "valor": cursor.fetchone()[0],
    }


def advertisers_por_dia(cursor):
    cursor.execute("""
        SELECT advertiser_id, COUNT(DISTINCT run_date) as dias
        FROM recommendations
        GROUP BY advertiser_id
        ORDER BY dias DESC
    """)
    rows = cursor.fetchall()
    return {
        "descripcion": "Cantidad de dias con recomendaciones disponibles por advertiser",
        "por_advertiser": [{"advertiser_id": r[0], "dias": r[1]} for r in rows],
    }


def overlap_modelos(cursor):
    cursor.execute("""
        SELECT advertiser_id, run_date, product_id
        FROM recommendations WHERE model_name = 'top_ctr'
    """)
    ctr_rows = cursor.fetchall()

    cursor.execute("""
        SELECT advertiser_id, run_date, product_id
        FROM recommendations WHERE model_name = 'top_product'
    """)
    product_rows = cursor.fetchall()

    ctr_sets = {}
    for advertiser_id, run_date, product_id in ctr_rows:
        key = (advertiser_id, run_date)
        if key not in ctr_sets:
            ctr_sets[key] = set()
        ctr_sets[key].add(product_id)

    product_sets = {}
    for advertiser_id, run_date, product_id in product_rows:
        key = (advertiser_id, run_date)
        if key not in product_sets:
            product_sets[key] = set()
        product_sets[key].add(product_id)
    #(adv, fecha) -> set(product_id)

    overlap_por_advertiser = {}
    all_keys = set(ctr_sets.keys()) | set(product_sets.keys())
    for advertiser_id, run_date in all_keys:
        ctr_products = ctr_sets.get((advertiser_id, run_date), set())
        top_products = product_sets.get((advertiser_id, run_date), set())
        productos_en_comun = len(ctr_products & top_products)
        porcentaje_de_overlap = round(productos_en_comun * 100 / 20, 1)
        overlap_por_advertiser.setdefault(advertiser_id, []).append(porcentaje_de_overlap)

    por_advertiser = []
    for advertiser_id, dias in overlap_por_advertiser.items():
        promedio = round(sum(dias) / len(dias), 1)
        por_advertiser.append({
            "advertiser_id": advertiser_id,
            "porcentaje_de_overlap": promedio,
        })

    por_advertiser.sort(key=lambda x: -x["porcentaje_de_overlap"])

    return {
        "descripcion": "Porcentaje promedio de productos en común entre top_ctr y top_product (sobre 20)",
        "por_advertiser": por_advertiser,
    }



def sin_recomendaciones_recientes(cursor):
    DIAS_LIMITE = 3
    #ultima fecha de cada advertiser
    cursor.execute("""
        SELECT advertiser_id, MAX(run_date) as ultima_fecha
        FROM recommendations
        GROUP BY advertiser_id
    """)
    rows = cursor.fetchall()

    hoy = Date.today()
    sin_datos = []
    for advertiser_id, ultima_fecha in rows:
        dias_sin_datos = (hoy - ultima_fecha).days
        if dias_sin_datos > DIAS_LIMITE:
            sin_datos.append({
                "advertiser_id": advertiser_id,
                "ultima_fecha": str(ultima_fecha),
                "dias_sin_datos": dias_sin_datos,
            })

    sin_datos.sort(key=lambda x: x["dias_sin_datos"], reverse=True)

    return {
        "descripcion": f"Advertisers sin recomendaciones en los últimos {DIAS_LIMITE} días",
        "cantidad": len(sin_datos),
        "advertisers": sin_datos,
    }
