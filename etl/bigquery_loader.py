import os
import pandas as pd
from google.cloud import bigquery
from config.settings import (
    GOOGLE_APPLICATION_CREDENTIALS,
    BIGQUERY_PROJECT_ID,
    BIGQUERY_DATASET_ID,
)


def get_client() -> bigquery.Client:
    if GOOGLE_APPLICATION_CREDENTIALS:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
    return bigquery.Client(project=BIGQUERY_PROJECT_ID)


def ensure_dataset(client: bigquery.Client):
    dataset_ref = bigquery.Dataset(f"{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET_ID}")
    dataset_ref.location = "US"
    client.create_dataset(dataset_ref, exists_ok=True)
    print(f"Dataset `{BIGQUERY_DATASET_ID}` ready.")


TABLE_SCHEMAS = {
    "orders": [
        bigquery.SchemaField("order_id", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("payment_status", "STRING"),
        bigquery.SchemaField("shipping_status", "STRING"),
        bigquery.SchemaField("total", "FLOAT"),
        bigquery.SchemaField("subtotal", "FLOAT"),
        bigquery.SchemaField("discount", "FLOAT"),
        bigquery.SchemaField("currency", "STRING"),
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("customer_name", "STRING"),
        bigquery.SchemaField("customer_email", "STRING"),
    ],
    "products": [
        bigquery.SchemaField("product_id", "STRING"),
        bigquery.SchemaField("variant_id", "STRING"),
        bigquery.SchemaField("product_name", "STRING"),
        bigquery.SchemaField("sku", "STRING"),
        bigquery.SchemaField("price", "FLOAT"),
        bigquery.SchemaField("stock", "INTEGER"),
        bigquery.SchemaField("published", "BOOLEAN"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
    ],
    "customers": [
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("email", "STRING"),
        bigquery.SchemaField("phone", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("last_order_id", "STRING"),
        bigquery.SchemaField("orders_count", "INTEGER"),
        bigquery.SchemaField("total_spent", "FLOAT"),
    ],
    "abandoned_carts": [
        bigquery.SchemaField("checkout_id", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("completed_at", "TIMESTAMP"),
        bigquery.SchemaField("email", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("total", "FLOAT"),
        bigquery.SchemaField("currency", "STRING"),
    ],
    "facebook_campaign_insights": [
        bigquery.SchemaField("campaign_id", "STRING"),
        bigquery.SchemaField("campaign_name", "STRING"),
        bigquery.SchemaField("adset_name", "STRING"),
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("impressions", "INTEGER"),
        bigquery.SchemaField("clicks", "INTEGER"),
        bigquery.SchemaField("spend", "FLOAT"),
        bigquery.SchemaField("reach", "INTEGER"),
        bigquery.SchemaField("cpc", "FLOAT"),
        bigquery.SchemaField("cpm", "FLOAT"),
        bigquery.SchemaField("ctr", "FLOAT"),
    ],
}


def load_dataframe(
    df: pd.DataFrame,
    table_name: str,
    write_disposition: str = bigquery.WriteDisposition.WRITE_APPEND,
):
    """Load a DataFrame into a BigQuery table."""
    if df.empty:
        print(f"No data to load for `{table_name}`. Skipping.")
        return

    client = get_client()
    ensure_dataset(client)

    table_id = f"{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{table_name}"
    schema = TABLE_SCHEMAS.get(table_name)

    # Convert TIMESTAMP and DATE columns from string to datetime
    for field in schema:
        if field.name in df.columns:
            if field.field_type == "TIMESTAMP":
                df[field.name] = pd.to_datetime(df[field.name], utc=True, errors="coerce")
            elif field.field_type == "DATE":
                df[field.name] = pd.to_datetime(df[field.name], errors="coerce").dt.date

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=write_disposition,
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {len(df)} rows into `{table_id}`.")
