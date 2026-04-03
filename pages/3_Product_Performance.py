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

try:
    prod = get_product_performance()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Productos", f"{len(prod)}")
    with col2:
        sin_stock = len(prod[prod["stock_status"] == "Sin Stock"])
        st.metric("Sin Stock", f"{sin_stock}", delta=f"-{sin_stock}" if sin_stock > 0 else "OK", delta_color="inverse")
    with col3:
        critico = len(prod[prod["stock_status"] == "Stock Critico"])
        st.metric("Stock Critico", f"{critico}", delta=f"-{critico}" if critico > 0 else "OK", delta_color="inverse")
    with col4:
        st.metric("Valor de Inventario", f"${prod['inventory_value'].sum():,.0f}")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Estado del stock")
        stock_counts = prod["stock_status"].value_counts().reset_index()
        stock_counts.columns = ["Estado", "Cantidad"]
        color_map = {
            "Sin Stock": "#c0392b",
            "Stock Critico": "#e67e22",
            "Stock Bajo": "#f1c40f",
            "OK": "#27ae60",
        }
        fig1 = px.pie(
            stock_counts, names="Estado", values="Cantidad",
            color="Estado", color_discrete_map=color_map,
        )
        fig1.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("Productos con stock critico o sin stock")
        alertas = prod[prod["stock_status"].isin(["Sin Stock", "Stock Critico"])].head(15)
        if alertas.empty:
            st.success("Todos los productos tienen stock suficiente.")
        else:
            fig2 = px.bar(
                alertas, x="stock", y="product_name", orientation="h",
                labels={"stock": "Unidades", "product_name": "Producto"},
                color="stock_status",
                color_discrete_map=color_map,
            )
            fig2.update_layout(margin=dict(t=10, b=10), showlegend=True, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig2, use_container_width=True)

    # Tabla completa
    st.subheader("Todos los productos")
    status_filter = st.multiselect(
        "Filtrar por estado",
        options=prod["stock_status"].unique().tolist(),
        default=prod["stock_status"].unique().tolist(),
    )
    filtered = prod[prod["stock_status"].isin(status_filter)]
    st.dataframe(
        filtered.rename(columns={
            "product_name": "Producto",
            "sku": "SKU",
            "price": "Precio",
            "stock": "Stock",
            "stock_status": "Estado",
            "inventory_value": "Valor Inventario",
        }),
        use_container_width=True,
        hide_index=True,
    )

except Exception as e:
    st.error(f"Error: {e}")
