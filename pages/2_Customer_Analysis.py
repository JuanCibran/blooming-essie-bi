import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
import plotly.express as px
from dashboard.data import get_customer_segments, get_top_customers, get_unconverted_customers, get_abandoned_carts

st.set_page_config(page_title="Customer Analysis", layout="wide")
st.title("Customer Analysis")
st.divider()

try:
    segments = get_customer_segments()
    top = get_top_customers()
    unconverted = get_unconverted_customers()
    carts = get_abandoned_carts()

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
        st.metric("Oportunidades campaña", len(unconverted) + len(carts),
                  delta=f"{len(unconverted)} sin compra · {len(carts)} carritos",
                  delta_color="inverse")

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

    # Oportunidades de campaña — merge sin repetir emails
    import pandas as pd, io, csv as _csv

    leads_unconverted = unconverted[["name", "email"]].copy()
    leads_unconverted["origen"] = "Sin compras"
    leads_unconverted["monto"] = 0.0

    leads_carts = carts[["name", "email", "total"]].copy().rename(columns={"total": "monto"})
    leads_carts["origen"] = "Carrito abandonado"

    leads = pd.concat([leads_unconverted, leads_carts], ignore_index=True)
    # Deduplicar por email — priorizar carrito abandonado (más intención)
    leads = leads.sort_values("origen").drop_duplicates(subset="email", keep="first").reset_index(drop=True)

    st.subheader(f"Oportunidades de campaña ({len(leads)} contactos únicos)")

    if leads.empty:
        st.success("No hay oportunidades pendientes.")
    else:
        cart_value = carts["total"].sum() if not carts.empty else 0
        msg = f"**{len(leads)} contactos** para campañas"
        if len(unconverted) > 0:
            msg += f" — {len(unconverted)} nunca compraron"
        if not carts.empty:
            msg += f", {len(carts)} dejaron carritos (${cart_value:,.0f} en juego)"
        st.info(msg)

        st.dataframe(
            leads.rename(columns={
                "name":   "Nombre",
                "email":  "Email",
                "origen": "Origen",
                "monto":  "Monto carrito ($)",
            }),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Monto carrito ($)": st.column_config.NumberColumn(format="$ %.0f"),
            },
        )

        _buf = io.StringIO()
        _w = _csv.writer(_buf)
        _w.writerows([leads.columns.tolist()] + leads.astype(str).values.tolist())
        st.download_button(
            label="Descargar lista para campaña (CSV)",
            data=_buf.getvalue().encode("utf-8"),
            file_name="oportunidades_campana.csv",
            mime="text/csv",
        )

except Exception as e:
    st.error(f"Error: {e}")
