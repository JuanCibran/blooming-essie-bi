import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import plotly.express as px
from dashboard.data import get_customer_segments, get_top_customers

st.set_page_config(page_title="Customer Analysis", layout="wide")
st.title("Customer Analysis")
st.divider()

try:
    segments = get_customer_segments()
    top = get_top_customers()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Clientes", f"{int(segments['customers'].sum())}")
    with col2:
        nuevos = segments[segments["segment"] == "Nuevo"]["customers"].sum()
        st.metric("Clientes Nuevos", f"{int(nuevos)}")
    with col3:
        recurrentes = segments[segments["segment"] != "Nuevo"]["customers"].sum()
        st.metric("Recurrentes + Fieles", f"{int(recurrentes)}")
    with col4:
        retention = recurrentes / segments["customers"].sum() * 100 if segments["customers"].sum() > 0 else 0
        st.metric("Tasa de Retención", f"{retention:.1f}%")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Clientes por segmento")
        fig1 = px.pie(
            segments, names="segment", values="customers",
            color_discrete_sequence=["#f8a4d0", "#e91e8c", "#9c1463"],
        )
        fig1.update_traces(textinfo="percent+label")
        fig1.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("Revenue por segmento")
        fig2 = px.bar(
            segments, x="segment", y="revenue",
            labels={"segment": "Segmento", "revenue": "Revenue (ARS)"},
            color="segment",
            color_discrete_sequence=["#f8a4d0", "#e91e8c", "#9c1463"],
            text="revenue",
        )
        fig2.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig2.update_layout(margin=dict(t=10, b=10), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Top clientes
    st.subheader("Top 20 clientes por revenue")
    fig3 = px.bar(
        top.head(10), x="name", y="total_spent",
        labels={"name": "Cliente", "total_spent": "Total Gastado (ARS)"},
        color_discrete_sequence=["#e91e8c"],
        text="total_spent",
    )
    fig3.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig3.update_layout(margin=dict(t=10, b=40))
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Tabla completa de clientes")
    st.dataframe(
        top.rename(columns={
            "name": "Nombre",
            "email": "Email",
            "orders_count": "Compras",
            "total_spent": "Total Gastado",
            "avg_order_value": "Ticket Promedio",
        }),
        use_container_width=True,
        hide_index=True,
    )

except Exception as e:
    st.error(f"Error: {e}")
