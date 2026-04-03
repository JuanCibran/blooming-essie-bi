"""
Blooming Essie — Dashboard Setup
Crea las vistas en BigQuery y genera los links de Looker Studio.
Correr una sola vez: python3 dashboard/setup_dashboard.py
"""
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import bigquery
from config.settings import GOOGLE_APPLICATION_CREDENTIALS, BIGQUERY_PROJECT_ID, BIGQUERY_DATASET_ID

PROJECT = BIGQUERY_PROJECT_ID
DATASET = BIGQUERY_DATASET_ID

VIEWS = {
    "v_revenue_daily": """
        SELECT
          DATE(created_at) AS date,
          COUNT(*) AS total_orders,
          ROUND(SUM(total), 2) AS revenue,
          ROUND(AVG(total), 2) AS avg_order_value,
          ROUND(SUM(discount), 2) AS total_discounts,
          COUNT(DISTINCT customer_id) AS unique_customers
        FROM `{project}.{dataset}.orders`
        WHERE payment_status = 'paid'
        GROUP BY date
    """,
    "v_revenue_monthly": """
        SELECT
          FORMAT_DATE('%Y-%m', DATE(created_at)) AS month,
          COUNT(*) AS total_orders,
          ROUND(SUM(total), 2) AS revenue,
          ROUND(AVG(total), 2) AS avg_order_value,
          COUNT(DISTINCT customer_id) AS unique_customers,
          ROUND(SUM(discount), 2) AS total_discounts
        FROM `{project}.{dataset}.orders`
        WHERE payment_status = 'paid'
        GROUP BY month
    """,
    "v_customer_segments": """
        SELECT
          CASE
            WHEN orders_count = 1 THEN '1 - Nuevo'
            WHEN orders_count BETWEEN 2 AND 3 THEN '2 - Recurrente'
            WHEN orders_count >= 4 THEN '3 - Fiel'
          END AS segment,
          COUNT(*) AS customer_count,
          ROUND(SUM(total_spent), 2) AS total_revenue,
          ROUND(AVG(total_spent), 2) AS avg_spent,
          ROUND(AVG(orders_count), 1) AS avg_orders
        FROM `{project}.{dataset}.customers`
        GROUP BY segment
    """,
    "v_top_customers": """
        SELECT
          name,
          email,
          orders_count,
          ROUND(total_spent, 2) AS total_spent,
          ROUND(total_spent / NULLIF(orders_count, 0), 2) AS avg_order_value,
          DATE(created_at) AS customer_since,
          CASE
            WHEN orders_count = 1 THEN 'Nuevo'
            WHEN orders_count BETWEEN 2 AND 3 THEN 'Recurrente'
            ELSE 'Fiel'
          END AS segment
        FROM `{project}.{dataset}.customers`
        ORDER BY total_spent DESC
    """,
    "v_product_performance": """
        SELECT
          product_name,
          sku,
          ROUND(price, 2) AS price,
          stock,
          published,
          CASE
            WHEN stock = 0 THEN 'Sin Stock'
            WHEN stock <= 5 THEN 'Stock Crítico'
            WHEN stock <= 15 THEN 'Stock Bajo'
            ELSE 'OK'
          END AS stock_status,
          ROUND(price * stock, 2) AS inventory_value
        FROM `{project}.{dataset}.products`
        WHERE published = TRUE
        ORDER BY stock ASC
    """,
    "v_ads_performance": """
        SELECT
          date,
          campaign_name,
          adset_name,
          impressions,
          clicks,
          ROUND(spend, 2) AS spend,
          reach,
          ROUND(ctr, 2) AS ctr,
          ROUND(cpc, 2) AS cpc,
          ROUND(cpm, 2) AS cpm
        FROM `{project}.{dataset}.facebook_campaign_insights`
        ORDER BY date DESC, spend DESC
    """,
    "v_roas_daily": """
        SELECT
          f.date,
          ROUND(f.spend, 2) AS ad_spend,
          ROUND(COALESCE(v.revenue, 0), 2) AS revenue,
          ROUND(COALESCE(v.revenue, 0) / NULLIF(f.spend, 0), 2) AS roas,
          COALESCE(v.total_orders, 0) AS orders,
          ROUND(COALESCE(v.revenue, 0) / NULLIF(v.total_orders, 0), 2) AS avg_order_value
        FROM (
          SELECT date, ROUND(SUM(spend), 2) AS spend
          FROM `{project}.{dataset}.facebook_campaign_insights`
          GROUP BY date
        ) f
        LEFT JOIN (
          SELECT DATE(created_at) AS date, SUM(total) AS revenue, COUNT(*) AS total_orders
          FROM `{project}.{dataset}.orders`
          WHERE payment_status = 'paid'
          GROUP BY date
        ) v ON f.date = v.date
        ORDER BY f.date DESC
    """,
}

# Looker Studio Linking API — una URL por vista para conectar rápido
LOOKER_BASE = "https://lookerstudio.google.com/datasources/create"

DASHBOARD_PAGES = {
    "Página 1 — Revenue & Sales": {
        "views": ["v_revenue_daily", "v_revenue_monthly"],
        "charts": [
            "Scorecard: revenue (SUM)",
            "Scorecard: total_orders (SUM)",
            "Scorecard: avg_order_value (AVG)",
            "Gráfico de línea: date vs revenue",
            "Barras: month vs revenue (desde v_revenue_monthly)",
        ],
    },
    "Página 2 — Customer Analysis": {
        "views": ["v_customer_segments", "v_top_customers"],
        "charts": [
            "Torta: segment vs customer_count",
            "Barras: segment vs total_revenue",
            "Tabla: v_top_customers (name, orders_count, total_spent, segment)",
        ],
    },
    "Página 3 — Product Performance": {
        "views": ["v_product_performance"],
        "charts": [
            "Tabla: product_name, sku, price, stock, stock_status",
            "Barras horizontales: product_name vs stock (ordenado ASC)",
            "Scorecard: inventory_value (SUM)",
            "Torta: stock_status vs COUNT",
        ],
    },
    "Página 4 — Ads Performance": {
        "views": ["v_ads_performance", "v_roas_daily"],
        "charts": [
            "Línea: date vs roas (desde v_roas_daily)",
            "Barras dobles: date vs ad_spend + revenue",
            "Tabla: campaign_name, spend, clicks, ctr, cpc (desde v_ads_performance)",
            "Scorecard: roas promedio",
        ],
    },
}


def create_views(client: bigquery.Client):
    print("\n📊 Creando vistas en BigQuery...\n")
    for view_name, query_template in VIEWS.items():
        query = query_template.format(project=PROJECT, dataset=DATASET)
        view_id = f"{PROJECT}.{DATASET}.{view_name}"
        view = bigquery.Table(view_id)
        view.view_query = query
        try:
            client.delete_table(view_id, not_found_ok=True)
            client.create_table(view)
            print(f"  ✅ {view_name}")
        except Exception as e:
            print(f"  ❌ {view_name}: {e}")


def generate_looker_urls():
    print("\n🔗 Links para conectar vistas en Looker Studio:\n")
    for view_name in VIEWS:
        params = urllib.parse.urlencode({
            "connector": "bigQuery",
            "projectId": PROJECT,
            "datasetId": DATASET,
            "tableId": view_name,
            "type": "TABLE",
        })
        url = f"{LOOKER_BASE}?{params}"
        print(f"  {view_name}:")
        print(f"  {url}\n")


def print_dashboard_guide():
    print("\n📋 Guía de armado del dashboard:\n")
    print("  1. Abrí cada link de arriba → conecta la vista como datasource")
    print("  2. Andá a lookerstudio.google.com → Crear → Informe")
    print("  3. Agregá las datasources y armá los gráficos según esta guía:\n")
    for page, config in DASHBOARD_PAGES.items():
        print(f"  {page}")
        print(f"    Datasources: {', '.join(config['views'])}")
        for chart in config["charts"]:
            print(f"    • {chart}")
        print()


if __name__ == "__main__":
    if GOOGLE_APPLICATION_CREDENTIALS:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    client = bigquery.Client(project=PROJECT)
    create_views(client)
    generate_looker_urls()
    print_dashboard_guide()
    print("✅ Setup completo. Seguí la guía de arriba para armar el dashboard.")
