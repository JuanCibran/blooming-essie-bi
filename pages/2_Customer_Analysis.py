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
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Clientes", f"{int(segments['customers'].sum())}")
    with col2:
        revenue_total = segments['revenue'].sum()
        st.metric("Revenue Total Clientes", f"${revenue_total:,.0f}")
    with col3:
        avg = segments['avg_spent'].mean()
        st.metric("Gasto Promedio por Cliente", f"${avg:,.0f}")

    st.divider()

    # Segmentos por gasto
    st.subheader("Clientes por nivel de gasto")
    fig = px.pie(
        segments, names="segment", values="customers",
        color_discrete_sequence=["#f8a4d0", "#e91e8c", "#9c1463", "#cccccc"],
    )
    fig.update_traces(textinfo="percent+label+value")
    fig.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Top 20 clientes
    st.subheader("Top 20 clientes por revenue")
    st.dataframe(
        top.rename(columns={
            "name":        "Cliente",
            "email":       "Email",
            "total_spent": "Total Gastado ($)",
        }),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Total Gastado ($)": st.column_config.NumberColumn(
                "Total Gastado", format="$ %.2f",
            ),
        },
    )

except Exception as e:
    st.error(f"Error: {e}")
