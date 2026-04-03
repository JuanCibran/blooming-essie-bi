"""
Blooming Essie BI — Daily ETL pipeline.
Pulls data from Tienda Nube and Facebook Ads, loads into BigQuery.
"""
import sys
from etl.tienda_nube import extract_orders, extract_products, extract_customers
from etl.facebook_ads import extract_campaign_insights
from etl.bigquery_loader import load_dataframe
from google.cloud import bigquery


def run():
    print("=== Blooming Essie BI Pipeline ===")

    # --- Tienda Nube ---
    print("\n[1/4] Extracting Tienda Nube orders...")
    orders_df = extract_orders(days_back=1)
    load_dataframe(orders_df, "orders")

    print("\n[2/4] Extracting Tienda Nube products...")
    products_df = extract_products()
    load_dataframe(
        products_df,
        "products",
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    print("\n[3/4] Extracting Tienda Nube customers...")
    customers_df = extract_customers()
    load_dataframe(
        customers_df,
        "customers",
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    # --- Facebook Ads ---
    print("\n[4/4] Extracting Facebook Ads insights...")
    fb_df = extract_campaign_insights(days_back=1)
    load_dataframe(fb_df, "facebook_campaign_insights")

    print("\n=== Pipeline complete ===")


if __name__ == "__main__":
    run()
