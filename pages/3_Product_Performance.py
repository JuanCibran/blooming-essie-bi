import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import plotly.express as px
from dashboard.data import get_product_performance

st.set_page_config(page_title="Product Performance", layout="wide")
st.title("Product Performance")
st.divider()

COLOR_MAP = {
    "Sin Stock":     "#c0392b",
    "Stock Critico": "#e67e22",
    "Stock Bajo":    "#f1c40f",
    "OK":            "#27ae60",
}

try:
    prod = get_product_performance()

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

    # --- Resumen visual ---
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("Resumen de stock")
        summary = prod["stock_status"].value_counts().reset_index()
        summary.columns = ["Estado", "Productos"]
        # Orden lógico
        order = ["Sin Stock", "Stock Critico", "Stock Bajo", "OK"]
        summary["Estado"] = pd.Categorical(summary["Estado"], categories=order, ordered=True)
        summary = summary.sort_values("Estado")

        fig1 = px.bar(
            summary, x="Estado", y="Productos",
            color="Estado", color_discrete_map=COLOR_MAP,
            text="Productos",
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("Productos que necesitan reposicion")
        alertas = prod[prod["stock_status"].isin(["Sin Stock", "Stock Critico", "Stock Bajo"])] \
                    .sort_values("stock").head(20)
        if alertas.empty:
            st.success("Todos los productos tienen stock suficiente.")
        else:
            fig2 = px.bar(
                alertas, x="stock", y="product_name", orientation="h",
                color="stock_status", color_discrete_map=COLOR_MAP,
                labels={"stock": "Unidades en stock", "product_name": ""},
                text="stock",
            )
            fig2.update_traces(textposition="outside")
            fig2.update_layout(
                showlegend=True,
                margin=dict(t=10, b=10, l=10),
                yaxis={"categoryorder": "total ascending"},
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # --- Tabla con colores ---
    st.subheader("Todos los productos")

    col_filter, _ = st.columns([2, 3])
    with col_filter:
        status_filter = st.multiselect(
            "Filtrar por estado",
            options=order,
            default=order,
        )

    filtered = prod[prod["stock_status"].isin(status_filter)].copy()

    # Color de fondo por estado
    def color_row(val):
        colors = {
            "Sin Stock":     "background-color: #fde8e8; color: #c0392b; font-weight: bold",
            "Stock Critico": "background-color: #fef3e2; color: #e67e22; font-weight: bold",
            "Stock Bajo":    "background-color: #fefce8; color: #b7950b",
            "OK":            "",
        }
        return colors.get(val, "")

    display = filtered.rename(columns={
        "product_name":    "Producto",
        "sku":             "SKU",
        "price":           "Precio",
        "stock":           "Stock",
        "stock_status":    "Estado",
        "inventory_value": "Valor Inventario",
    }).sort_values("Stock")

    st.dataframe(
        display.style.applymap(color_row, subset=["Estado"]),
        use_container_width=True,
        hide_index=True,
    )

except Exception as e:
    st.error(f"Error: {e}")
