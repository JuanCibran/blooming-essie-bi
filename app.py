import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from dashboard.data import get_daily_revenue, get_customer_segments, get_product_performance, table_exists

st.set_page_config(
    page_title="Blooming Essie — BI Dashboard",
    page_icon="🌸",
    layout="wide",
)

st.title("Blooming Essie")
st.caption("Business Intelligence Dashboard")
st.divider()

# KPIs principales
try:
    df = get_daily_revenue()
    seg = get_customer_segments()
    prod = get_product_performance()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Ingresos Totales", f"${df['revenue'].sum():,.0f}")
    with col2:
        st.metric("Total Ordenes", f"{int(df['total_orders'].sum())}")
    with col3:
        st.metric("Ticket Promedio", f"${df['avg_order_value'].mean():,.0f}")
    with col4:
        total_customers = seg["customers"].sum()
        st.metric("Total Clientes", f"{int(total_customers)}")
    with col5:
        sin_stock = len(prod[prod["stock_status"] == "Sin Stock"])
        st.metric("Sin Stock", f"{sin_stock}", delta=f"-{sin_stock}" if sin_stock > 0 else None, delta_color="inverse")

    st.divider()

    import plotly.express as px

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Ingresos diarios")
        fig = px.line(df, x="date", y="revenue", markers=True,
                      labels={"date": "Fecha", "revenue": "Ingresos (ARS)"},
                      color_discrete_sequence=["#e91e8c"])
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Clientes por segmento")
        fig2 = px.pie(seg, names="segment", values="customers",
                      color_discrete_sequence=["#f8a4d0", "#e91e8c", "#9c1463"])
        fig2.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.caption("Usá el menu de la izquierda para ver cada sección en detalle.")

except Exception as e:
    st.error(f"Error conectando a BigQuery: {e}")
    st.info("Verificá que el archivo .env tenga las credenciales correctas.")
