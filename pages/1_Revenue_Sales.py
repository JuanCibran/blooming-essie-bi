import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import plotly.express as px
from dashboard.data import get_daily_revenue, get_monthly_revenue, get_orders_by_status
from dashboard.filters import date_filter

st.set_page_config(page_title="Revenue & Sales", layout="wide")
st.title("Revenue & Sales")
st.divider()

try:
    df_all = get_daily_revenue()
    daily, start, end = date_filter(df_all)

    monthly = get_monthly_revenue()
    status = get_orders_by_status()

    if daily.empty:
        st.warning("Sin datos para el período seleccionado. Probá con un rango más amplio.")
        st.stop()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ingresos del período", f"${daily['revenue'].sum():,.0f}")
    with col2:
        st.metric("Total Ordenes", f"{int(daily['total_orders'].sum())}")
    with col3:
        st.metric("Ticket Promedio", f"${daily['avg_order_value'].mean():,.0f}")
    with col4:
        st.metric("Descuentos Aplicados", f"${daily['total_discounts'].sum():,.0f}")

    st.divider()

    # Ingresos diarios
    st.subheader("Ingresos diarios")
    fig1 = px.line(
        daily, x="date", y="revenue", markers=True,
        labels={"date": "Fecha", "revenue": "Ingresos (ARS)"},
        color_discrete_sequence=["#e91e8c"],
    )
    fig1.update_traces(fill="tozeroy", fillcolor="rgba(233,30,140,0.08)")
    fig1.update_layout(margin=dict(t=10, b=10), hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Ingresos por mes")
        fig2 = px.bar(
            monthly, x="month", y="revenue",
            labels={"month": "Mes", "revenue": "Ingresos (ARS)"},
            color_discrete_sequence=["#e91e8c"],
            text="revenue",
        )
        fig2.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig2.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    with col_right:
        st.subheader("Ordenes por estado de pago")
        fig3 = px.pie(
            status, names="payment_status", values="orders",
            color_discrete_sequence=["#e91e8c", "#f8a4d0", "#9c1463", "#fce4f3"],
        )
        fig3.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig3, use_container_width=True)

    # Tabla detalle diario
    st.subheader("Detalle diario")
    st.dataframe(
        daily.sort_values("date", ascending=False).rename(columns={
            "date": "Fecha",
            "total_orders": "Ordenes",
            "revenue": "Ingresos",
            "avg_order_value": "Ticket Promedio",
            "total_discounts": "Descuentos",
        }),
        use_container_width=True,
        hide_index=True,
    )

except Exception as e:
    st.error(f"Error: {e}")
