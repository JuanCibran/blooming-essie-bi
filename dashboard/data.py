import os
import pandas as pd
import streamlit as st
from google.cloud import bigquery

PROJECT = os.getenv("BIGQUERY_PROJECT_ID", "blooming-essie")
DATASET = os.getenv("BIGQUERY_DATASET_ID", "blooming_essie")

def get_client():
    creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if creds:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds
    return bigquery.Client(project=PROJECT)

def run_query(sql: str) -> pd.DataFrame:
    client = get_client()
    return client.query(sql).to_dataframe()

# Subquery que deduplica órdenes por order_id (el ETL append puede duplicar)
DEDUP_ORDERS = f"""
    SELECT * EXCEPT(rn) FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY created_at DESC) AS rn
        FROM `{PROJECT}.{DATASET}.orders`
    ) WHERE rn = 1
"""

# --- Revenue & Sales ---

@st.cache_data(ttl=3600)
def get_daily_revenue() -> pd.DataFrame:
    return run_query(f"""
        SELECT
          DATE(created_at) AS date,
          COUNT(*) AS total_orders,
          ROUND(SUM(total), 2) AS revenue,
          ROUND(AVG(total), 2) AS avg_order_value,
          ROUND(SUM(discount), 2) AS total_discounts
        FROM ({DEDUP_ORDERS})
        WHERE payment_status = 'paid'
        GROUP BY date
        ORDER BY date
    """)

@st.cache_data(ttl=3600)
def get_monthly_revenue() -> pd.DataFrame:
    return run_query(f"""
        SELECT
          FORMAT_DATE('%Y-%m', DATE(created_at)) AS month,
          COUNT(*) AS total_orders,
          ROUND(SUM(total), 2) AS revenue,
          ROUND(AVG(total), 2) AS avg_order_value
        FROM ({DEDUP_ORDERS})
        WHERE payment_status = 'paid'
        GROUP BY month
        ORDER BY month
    """)

@st.cache_data(ttl=3600)
def get_orders_by_status() -> pd.DataFrame:
    return run_query(f"""
        SELECT
          payment_status,
          COUNT(*) AS orders,
          ROUND(SUM(total), 2) AS value
        FROM ({DEDUP_ORDERS})
        GROUP BY payment_status
    """)

# --- Customer Analysis ---

@st.cache_data(ttl=3600)
def get_customer_segments() -> pd.DataFrame:
    # Segmentamos por total_spent ya que orders_count no viene de la API de Tienda Nube
    return run_query(f"""
        SELECT
          CASE
            WHEN total_spent = 0 THEN 'Sin compras'
            WHEN total_spent < 50000 THEN 'Bajo (< $50k)'
            WHEN total_spent < 200000 THEN 'Medio ($50k-$200k)'
            ELSE 'Alto (> $200k)'
          END AS segment,
          COUNT(*) AS customers,
          ROUND(SUM(total_spent), 2) AS revenue,
          ROUND(AVG(total_spent), 2) AS avg_spent
        FROM `{PROJECT}.{DATASET}.customers`
        GROUP BY segment
    """)

@st.cache_data(ttl=3600)
def get_top_customers() -> pd.DataFrame:
    return run_query(f"""
        SELECT
          name,
          email,
          ROUND(total_spent, 2) AS total_spent
        FROM `{PROJECT}.{DATASET}.customers`
        WHERE total_spent > 0
        ORDER BY total_spent DESC
        LIMIT 20
    """)

@st.cache_data(ttl=3600)
def get_unconverted_customers() -> pd.DataFrame:
    return run_query(f"""
        SELECT
          name,
          email,
          DATE(created_at) AS fecha_registro
        FROM `{PROJECT}.{DATASET}.customers`
        WHERE total_spent = 0
          AND email IS NOT NULL
          AND email != ''
        ORDER BY created_at DESC
    """)

# --- Product Performance ---

@st.cache_data(ttl=3600)
def get_product_performance() -> pd.DataFrame:
    return run_query(f"""
        SELECT
          product_name,
          sku,
          ROUND(price, 2) AS price,
          stock,
          CASE
            WHEN stock = 0 THEN 'Sin Stock'
            WHEN stock <= 2 THEN 'Stock Critico'
            WHEN stock <= 4 THEN 'Stock Bajo'
            ELSE 'OK'
          END AS stock_status,
          ROUND(price * stock, 2) AS inventory_value
        FROM `{PROJECT}.{DATASET}.products`
        WHERE published = TRUE
        ORDER BY stock ASC
    """)

# --- Ads Performance ---

@st.cache_data(ttl=3600)
def get_ads_performance() -> pd.DataFrame:
    return run_query(f"""
        SELECT
          date,
          campaign_name,
          impressions,
          clicks,
          ROUND(spend, 2) AS spend,
          ROUND(ctr, 2) AS ctr,
          ROUND(cpc, 2) AS cpc
        FROM `{PROJECT}.{DATASET}.facebook_campaign_insights`
        ORDER BY date DESC
    """)

@st.cache_data(ttl=3600)
def get_roas() -> pd.DataFrame:
    return run_query(f"""
        SELECT
          f.date,
          ROUND(f.spend, 2) AS ad_spend,
          ROUND(COALESCE(v.revenue, 0), 2) AS revenue,
          ROUND(COALESCE(v.revenue, 0) / NULLIF(f.spend, 0), 2) AS roas,
          COALESCE(v.total_orders, 0) AS orders
        FROM (
          SELECT date, SUM(spend) AS spend
          FROM `{PROJECT}.{DATASET}.facebook_campaign_insights`
          GROUP BY date
        ) f
        LEFT JOIN (
          SELECT DATE(created_at) AS date, SUM(total) AS revenue, COUNT(*) AS total_orders
          FROM `{PROJECT}.{DATASET}.orders`
          WHERE payment_status = 'paid'
          GROUP BY date
        ) v ON f.date = v.date
        ORDER BY f.date
    """)

def table_exists(table_name: str) -> bool:
    try:
        client = get_client()
        client.get_table(f"{PROJECT}.{DATASET}.{table_name}")
        return True
    except Exception:
        return False
