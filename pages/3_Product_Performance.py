import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import streamlit as st
from dashboard.data import get_product_performance

st.set_page_config(page_title="Product Performance", layout="wide")
st.title("Product Performance")
st.divider()

try:
    prod = get_product_performance()
    order = ["Sin Stock", "Stock Critico", "Stock Bajo", "OK"]

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Productos", len(prod))
    with col2:
        sin_stock = len(prod[prod["stock_status"] == "Sin Stock"])
        st.metric("Sin Stock", sin_stock, delta=f"-{sin_stock}" if sin_stock > 0 else None, delta_color="inverse")
    with col3:
        critico = len(prod[prod["stock_status"] == "Stock Critico"])
        st.metric("Stock Critico", critico, delta=f"-{critico}" if critico > 0 else None, delta_color="inverse")
    with col4:
        st.metric("Valor de Inventario", f"${prod['inventory_value'].sum():,.0f}")

    st.divider()

    # --- Productos que necesitan reposición ---
    alertas = prod[prod["stock_status"].isin(["Sin Stock", "Stock Critico", "Stock Bajo"])] \
                .sort_values("stock")[["product_name", "sku", "stock", "stock_status", "price"]]

    st.subheader(f"Productos que necesitan reposicion ({len(alertas)})")

    if alertas.empty:
        st.success("Todos los productos tienen stock OK.")
    else:
        def highlight(row):
            if row["stock_status"] == "Sin Stock":
                return ["background-color:#fde8e8"] * len(row)
            elif row["stock_status"] == "Stock Critico":
                return ["background-color:#fef3e2"] * len(row)
            elif row["stock_status"] == "Stock Bajo":
                return ["background-color:#fefce8"] * len(row)
            return [""] * len(row)

        display = alertas.rename(columns={
            "product_name": "Producto",
            "sku":          "SKU",
            "stock":        "Stock actual",
            "stock_status": "Estado",
            "price":        "Precio",
        })

        st.dataframe(
            display.style.apply(highlight, axis=1),
            use_container_width=True,
            hide_index=True,
            height=500,
        )

        # Exportar como CSV para enviar al proveedor
        csv = display.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Descargar lista para proveedor (CSV)",
            data=csv,
            file_name="reposicion_blooming_essie.csv",
            mime="text/csv",
        )

    st.divider()

    # --- Todos los productos ---
    st.subheader("Todos los productos")

    col_filter, _ = st.columns([2, 3])
    with col_filter:
        status_filter = st.multiselect("Filtrar por estado", options=order, default=order)

    filtered = prod[prod["stock_status"].isin(status_filter)].copy()

    display_all = filtered.rename(columns={
        "product_name":    "Producto",
        "sku":             "SKU",
        "price":           "Precio",
        "stock":           "Stock",
        "stock_status":    "Estado",
        "inventory_value": "Valor Inventario",
    }).sort_values("Stock")

    st.dataframe(
        display_all.style.apply(highlight, axis=1),
        use_container_width=True,
        hide_index=True,
    )

except Exception as e:
    st.error(f"Error: {e}")
