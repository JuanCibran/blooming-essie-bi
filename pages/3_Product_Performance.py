import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from dashboard.data import get_product_performance

st.set_page_config(page_title="Product Performance", layout="wide")
st.title("Product Performance")
st.divider()

INDICADOR = {
    "Sin Stock":     "🔴 Sin Stock",
    "Stock Critico": "🟠 Stock Critico",
    "Stock Bajo":    "🟡 Stock Bajo",
    "OK":            "🟢 OK",
}

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

    col_filter, _ = st.columns([2, 3])
    with col_filter:
        status_filter = st.multiselect(
            "Filtrar por estado",
            options=order,
            default=order,
        )

    filtered = prod[prod["stock_status"].isin(status_filter)].sort_values("stock").copy()
    filtered["estado"] = filtered["stock_status"].map(INDICADOR)

    display = filtered[["product_name", "sku", "stock", "estado", "price", "inventory_value"]].rename(columns={
        "product_name":    "Producto",
        "sku":             "SKU",
        "stock":           "Stock",
        "estado":          "Estado",
        "price":           "Precio",
        "inventory_value": "Valor Inventario",
    })

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Precio": st.column_config.NumberColumn(
                "Precio", format="$ %.2f",
            ),
            "Valor Inventario": st.column_config.NumberColumn(
                "Valor Inventario", format="$ %.2f",
            ),
            "Stock": st.column_config.NumberColumn(
                "Stock", format="%d uds",
            ),
        },
    )

    st.write("")
    import io, csv as _csv
    _csv_df = filtered[["product_name", "sku", "stock", "stock_status", "price"]].rename(columns={
        "product_name": "Producto", "sku": "SKU", "stock": "Stock",
        "stock_status": "Estado", "price": "Precio",
    })
    _buf = io.StringIO()
    _w = _csv.DictWriter(_buf, fieldnames=_csv_df.columns.tolist())
    _w.writeheader()
    _w.writerows(_csv_df.astype(str).to_dict("records"))
    st.download_button(
        label="Descargar CSV",
        data=_buf.getvalue().encode("utf-8"),
        file_name="productos_blooming_essie.csv",
        mime="text/csv",
    )

except Exception as e:
    st.error(f"Error: {e}")
