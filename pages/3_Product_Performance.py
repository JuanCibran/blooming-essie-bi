import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from dashboard.data import get_product_performance

st.set_page_config(page_title="Product Performance", layout="wide")
st.title("Product Performance")
st.divider()

ROW_COLORS = {
    "Sin Stock":     "#fde8e8",
    "Stock Critico": "#fef3e2",
    "Stock Bajo":    "#fefce8",
    "OK":            "#ffffff",
}
TEXT_COLORS = {
    "Sin Stock":     "#c0392b",
    "Stock Critico": "#b7600a",
    "Stock Bajo":    "#7d6608",
    "OK":            "#1a6e35",
}

def render_html_table(df, status_col):
    headers = "".join(
        f"<th style='padding:8px 12px; text-align:left; border-bottom:2px solid #ddd; white-space:nowrap;'>{c}</th>"
        for c in df.columns
    )
    rows = ""
    for _, row in df.iterrows():
        status = row[status_col]
        bg = ROW_COLORS.get(status, "#fff")
        fg = TEXT_COLORS.get(status, "#333")
        cells = ""
        for col, val in row.items():
            if col == status_col:
                cells += f"<td style='padding:7px 12px; font-weight:600; color:{fg};'>{val}</td>"
            else:
                cells += f"<td style='padding:7px 12px; color:#222;'>{val}</td>"
        rows += f"<tr style='background:{bg};'>{cells}</tr>"

    return f"""
    <div style='overflow-x:auto; border:1px solid #e0e0e0; border-radius:8px;'>
    <table style='width:100%; border-collapse:collapse; font-size:14px;'>
        <thead style='background:#f5f5f5;'><tr>{headers}</tr></thead>
        <tbody>{rows}</tbody>
    </table>
    </div>
    """

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

    filtered = prod[prod["stock_status"].isin(status_filter)].sort_values("stock")

    display = filtered.rename(columns={
        "product_name":    "Producto",
        "sku":             "SKU",
        "stock":           "Stock",
        "stock_status":    "Estado",
        "price":           "Precio ($)",
        "inventory_value": "Valor Inventario ($)",
    })[["Producto", "SKU", "Stock", "Estado", "Precio ($)", "Valor Inventario ($)"]]

    st.markdown(render_html_table(display, "Estado"), unsafe_allow_html=True)

    st.write("")
    csv = display.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar CSV",
        data=csv,
        file_name="productos_blooming_essie.csv",
        mime="text/csv",
    )

except Exception as e:
    st.error(f"Error: {e}")
