import hashlib
import time
import pandas as pd
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.serverside.event import Event
from facebook_business.adobjects.serverside.event_request import EventRequest
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.adobjects.serverside.custom_data import CustomData
from config.settings import (
    FACEBOOK_APP_ID,
    FACEBOOK_APP_SECRET,
    FACEBOOK_ACCESS_TOKEN,
    FACEBOOK_PIXEL_ID,
)

PIXEL_ID = FACEBOOK_PIXEL_ID


def _hash(value: str) -> str:
    """SHA-256 hash requerido por Meta para datos de usuario."""
    if not value:
        return None
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()


def _order_to_event(order: dict) -> Event:
    """Convierte una orden de Tienda Nube en un evento Purchase para Meta CAPI."""
    user_data = UserData(
        email=_hash(order.get("customer_email", "")),
        client_ip_address=None,
        client_user_agent=None,
    )

    custom_data = CustomData(
        value=float(order.get("total", 0)),
        currency=order.get("currency", "ARS"),
        order_id=str(order.get("order_id", "")),
    )

    # event_time debe ser Unix timestamp
    created_at = order.get("created_at")
    if hasattr(created_at, "timestamp"):
        event_time = int(created_at.timestamp())
    else:
        event_time = int(time.time())

    return Event(
        event_name="Purchase",
        event_time=event_time,
        event_id=str(order.get("order_id", "")),  # Para deduplicación con el Pixel
        event_source_url="https://bloomingessie.com",
        user_data=user_data,
        custom_data=custom_data,
    )


def send_purchase_events(orders_df: pd.DataFrame) -> int:
    """
    Envía eventos de compra a Meta Conversions API.
    Solo manda órdenes pagas. Retorna la cantidad de eventos enviados.
    """
    if not PIXEL_ID or not FACEBOOK_ACCESS_TOKEN:
        print("[!] Meta CAPI skipped — FACEBOOK_PIXEL_ID o FACEBOOK_ACCESS_TOKEN no configurados.")
        return 0

    FacebookAdsApi.init(
        app_id=FACEBOOK_APP_ID,
        app_secret=FACEBOOK_APP_SECRET,
        access_token=FACEBOOK_ACCESS_TOKEN,
    )

    paid_orders = orders_df[orders_df["payment_status"] == "paid"]

    if paid_orders.empty:
        print("[!] Meta CAPI: no hay órdenes pagas para enviar.")
        return 0

    events = [_order_to_event(row) for row in paid_orders.to_dict("records")]

    # Meta acepta hasta 1000 eventos por request — los mandamos en batches
    batch_size = 1000
    total_sent = 0

    for i in range(0, len(events), batch_size):
        batch = events[i : i + batch_size]
        request = EventRequest(
            pixel_id=PIXEL_ID,
            events=batch,
        )
        response = request.execute()
        total_sent += len(batch)
        print(f"  Meta CAPI: batch {i // batch_size + 1} enviado — {response.events_received} eventos recibidos.")

    return total_sent
