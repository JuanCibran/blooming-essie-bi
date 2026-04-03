import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
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

BADGE_STYLE = {
    "Sin Stock":     "background:#fde8e8; color:#c0392b; border:1.5px solid #c0392b;",
    "Stock Critico": "background:#fef3e2; color:#e67e22; border:1.5px solid #e67e22;",
    "Stock Bajo":    "background:#fefce8; color:#b7950b; border:1.5px solid #f1c40f;",
    "OK":            "background:#eafaf1; color:#27ae60; border:1.5px solid #27ae60;",
}

def product_cards(df: pd.DataFrame, cols: int = 4):
    rows = [df.iloc[i:i+cols] for i in range(0, len(df), cols)]
    for row in rows:
        columns = st.columns(cols)
        for col, (_, p) in zip(columns, row.iterrows()):
            status = p["stock_status"]
            border_color = COLOR_MAP.get(status, "#ccc")
            badge = BADGE_STYLE.get(status, "")
            stock_num = int(p["stock"])
            with col:
                st.markdown(f"""
                <div style="
                    border: 2px solid {border_color};
                    border-radius: 10px;
                    padding: 14px 12px;
                    margin-bottom: 10px;
                    min-height: 110px;
                ">
                    <div style="font-size:13px; font-weight:600; color:#222; margin-bottom:6px; line-height:1.3;">
                        {p['product_name']}
                    </div>
                    <div style="font-size:11px; color:#888; margin-bottom:8px;">SKU: {p['sku'] or '—'}</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:22px; font-weight:700; color:{border_color};">{stock_num}</span>
                        <span style="font-size:11px; font-weight:600; padding:3px 8px; border-radius:20px; {badge}">
                            {status}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)


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

    # Resumen
    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.subheader("Resumen de stock")
        summary = prod["stock_status"].value_counts().reset_index()
        summary.columns = ["Estado", "Productos"]
        summary["Estado"] = pd.Categorical(summary["Estado"], categories=order, ordered=True)
        summary = summary.sort_values("Estado")
        fig1 = px.bar(
            summary, x="Estado", y="Productos",
            color="Estado", color_discrete_map=COLOR_MAP, text="Productos",
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("Distribución de inventario")
        fig2 = px.pie(
            summary, names="Estado", values="Productos",
            color="Estado", color_discrete_map=COLOR_MAP,
        )
        fig2.update_traces(textinfo="percent+label")
        fig2.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Tarjetas de productos con problemas
    alertas = prod[prod["stock_status"].isin(["Sin Stock", "Stock Critico", "Stock Bajo"])] \
                .sort_values("stock")

    if alertas.empty:
        st.success("Todos los productos tienen stock suficiente.")
    else:
        tab1, tab2, tab3 = st.tabs([
            f"Sin Stock ({len(prod[prod['stock_status']=='Sin Stock'])})",
            f"Stock Critico ({len(prod[prod['stock_status']=='Stock Critico'])})",
            f"Stock Bajo ({len(prod[prod['stock_status']=='Stock Bajo'])})",
        ])
        with tab1:
            group = prod[prod["stock_status"] == "Sin Stock"]
            if group.empty:
                st.success("Ninguno.")
            else:
                product_cards(group)
        with tab2:
            group = prod[prod["stock_status"] == "Stock Critico"]
            if group.empty:
                st.success("Ninguno.")
            else:
                product_cards(group)
        with tab3:
            group = prod[prod["stock_status"] == "Stock Bajo"]
            if group.empty:
                st.success("Ninguno.")
            else:
                product_cards(group)

    st.divider()

    # Tabla completa
    st.subheader("Todos los productos")
    col_filter, _ = st.columns([2, 3])
    with col_filter:
        status_filter = st.multiselect("Filtrar por estado", options=order, default=order)

    filtered = prod[prod["stock_status"].isin(status_filter)].copy()

    def color_estado(val):
        styles = {
            "Sin Stock":     "background-color:#fde8e8; color:#c0392b; font-weight:bold",
            "Stock Critico": "background-color:#fef3e2; color:#e67e22; font-weight:bold",
            "Stock Bajo":    "background-color:#fefce8; color:#b7950b",
            "OK":            "background-color:#eafaf1; color:#27ae60",
        }
        return styles.get(val, "")

    display = filtered.rename(columns={
        "product_name": "Producto", "sku": "SKU", "price": "Precio",
        "stock": "Stock", "stock_status": "Estado", "inventory_value": "Valor Inventario",
    }).sort_values("Stock")

    st.dataframe(
        display.style.applymap(color_estado, subset=["Estado"]),
        use_container_width=True,
        hide_index=True,
    )

except Exception as e:
    st.error(f"Error: {e}")
