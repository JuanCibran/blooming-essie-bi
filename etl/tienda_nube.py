import requests
import pandas as pd
from datetime import datetime, timedelta
from config.settings import TIENDANUBE_BASE_URL, TIENDANUBE_HEADERS


def fetch_all_pages(endpoint: str, params: dict = None) -> list:
    """Paginate through all results from a Tienda Nube endpoint."""
    results = []
    page = 1
    params = params or {}

    while True:
        params["page"] = page
        params["per_page"] = 200
        response = requests.get(
            f"{TIENDANUBE_BASE_URL}/{endpoint}",
            headers=TIENDANUBE_HEADERS,
            params=params,
        )
        if response.status_code == 404:
            break
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        results.extend(data)
        page += 1

    return results


def extract_orders(days_back: int = 1) -> pd.DataFrame:
    """Pull orders created in the last N days."""
    since = (datetime.utcnow() - timedelta(days=days_back)).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    raw = fetch_all_pages("orders", params={"created_at_min": since})

    rows = []
    for o in raw:
        rows.append(
            {
                "order_id": str(o.get("id")),
                "created_at": o.get("created_at"),
                "status": o.get("status"),
                "payment_status": o.get("payment_status"),
                "shipping_status": o.get("shipping_status"),
                "total": float(o.get("total", 0)),
                "subtotal": float(o.get("subtotal", 0)),
                "discount": float(o.get("discount", 0)),
                "currency": o.get("currency"),
                "customer_id": str(o.get("customer", {}).get("id", "")),
                "customer_name": o.get("customer", {}).get("name", ""),
                "customer_email": o.get("customer", {}).get("email", ""),
            }
        )

    return pd.DataFrame(rows)


def extract_products() -> pd.DataFrame:
    """Pull all products."""
    raw = fetch_all_pages("products")

    rows = []
    for p in raw:
        for variant in p.get("variants", [{}]):
            rows.append(
                {
                    "product_id": str(p.get("id")),
                    "variant_id": str(variant.get("id", "")),
                    "product_name": p.get("name", {}).get("es", ""),
                    "sku": variant.get("sku", ""),
                    "price": float(variant.get("price", 0)),
                    "stock": int(variant.get("stock", 0) or 0),
                    "published": p.get("published"),
                    "created_at": p.get("created_at"),
                    "updated_at": p.get("updated_at"),
                }
            )

    return pd.DataFrame(rows)


def extract_customers() -> pd.DataFrame:
    """Pull all customers."""
    raw = fetch_all_pages("customers")

    rows = []
    for c in raw:
        rows.append(
            {
                "customer_id": str(c.get("id")),
                "name": c.get("name", ""),
                "email": c.get("email", ""),
                "phone": c.get("phone", ""),
                "created_at": c.get("created_at"),
                "last_order_id": str(c.get("last_order_id", "") or ""),
                "orders_count": int(c.get("orders_count", 0) or 0),
                "total_spent": float(c.get("total_spent", 0) or 0),
            }
        )

    return pd.DataFrame(rows)
