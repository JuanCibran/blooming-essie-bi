import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import plotly.express as px
from dashboard.data import get_customer_segments, get_top_customers, get_unconverted_customers

st.set_page_config(page_title="Customer Analysis", layout="wide")
st.title("Customer Analysis")
st.divider()

try:
    segments = get_customer_segments()
    top = get_top_customers()
    unconverted = get_unconverted_customers()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Clientes", f"{int(segments['customers'].sum())}")
    with col2:
        revenue_total = segments['revenue'].sum()
        st.metric("Revenue Total Clientes", f"${revenue_total:,.0f}")
    with col3:
        avg = segments['avg_spent'].mean()
        st.metric("Gasto Promedio por Cliente", f"${avg:,.0f}")
    with col4:
        st.metric("Oportunidades sin convertir", len(unconverted),
                  delta=f"{len(unconverted)} sin compra", delta_color="inverse")

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

    st.divider()

    # Oportunidades de conversión
    st.subheader(f"Oportunidades de conversion — se registraron pero nunca compraron ({len(unconverted)})")
    if unconverted.empty:
        st.success("Todos los clientes registrados compraron al menos una vez.")
    else:
        st.info("Estos clientes te dieron su email pero nunca compraron. Son candidatos ideales para una campaña de email o retargeting en Meta.")
        st.dataframe(
            unconverted.rename(columns={
                "name":            "Nombre",
                "email":           "Email",
                "fecha_registro":  "Se registró el",
            }),
            use_container_width=True,
            hide_index=True,
        )
        csv = unconverted.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Descargar lista para campaña (CSV)",
            data=csv,
            file_name="leads_sin_convertir.csv",
            mime="text/csv",
        )

except Exception as e:
    st.error(f"Error: {e}")
