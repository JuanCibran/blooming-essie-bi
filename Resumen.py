import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from datetime import date, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px
from dashboard.data import get_daily_revenue, get_product_performance, get_orders_by_status, get_unconverted_customers

st.set_page_config(
    page_title="Blooming Essie — BI Dashboard",
    page_icon="🌸",
    layout="wide",
)

col_title, col_btn = st.columns([5, 1])
with col_title:
    st.title("Blooming Essie")
    st.caption(f"Actualizado: {date.today().strftime('%d/%m/%Y')}")
with col_btn:
    st.write("")
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()
st.divider()

try:
    daily_all = get_daily_revenue()
    prod = get_product_performance()
    status_df = get_orders_by_status()
    unconverted = get_unconverted_customers()

    # Períodos
    today = date.today()
    first_this_month = today.replace(day=1)
    first_last_month = (first_this_month - timedelta(days=1)).replace(day=1)
    last_last_month = first_this_month - timedelta(days=1)

    daily_all["date"] = pd.to_datetime(daily_all["date"].astype(str)).dt.date

    this_month = daily_all[daily_all["date"] >= first_this_month]
    last_month = daily_all[(daily_all["date"] >= first_last_month) & (daily_all["date"] <= last_last_month)]

    def delta_pct(curr, prev):
        if prev == 0:
            return None
        return f"{((curr - prev) / prev * 100):+.1f}%"

    # --- KPIs este mes vs mes anterior ---
    st.subheader("Este mes")
    col1, col2, col3, col4, col5 = st.columns(5)

    rev_curr = this_month["revenue"].sum()
    rev_prev = last_month["revenue"].sum()
    with col1:
        st.metric("Ingresos", f"${rev_curr:,.0f}", delta=delta_pct(rev_curr, rev_prev))

    ord_curr = int(this_month["total_orders"].sum())
    ord_prev = int(last_month["total_orders"].sum())
    with col2:
        st.metric("Ordenes", ord_curr, delta=delta_pct(ord_curr, ord_prev))

    aov_curr = this_month["avg_order_value"].mean() if not this_month.empty else 0
    aov_prev = last_month["avg_order_value"].mean() if not last_month.empty else 0
    with col3:
        st.metric("Ticket Promedio", f"${aov_curr:,.0f}", delta=delta_pct(aov_curr, aov_prev))

    with col4:
        sin_stock = len(prod[prod["stock_status"] == "Sin Stock"])
        critico = len(prod[prod["stock_status"] == "Stock Critico"])
        st.metric("Sin Stock / Critico", f"{sin_stock} / {critico}",
                  delta=f"Revisar" if sin_stock > 0 else None, delta_color="inverse")

    with col5:
        pending = status_df[status_df["payment_status"] == "pending"]["value"].sum()
        st.metric("Pendiente de cobro", f"${pending:,.0f}",
                  delta="Seguimiento" if pending > 0 else None, delta_color="inverse")

    st.divider()

    # --- Gráfico revenue este mes ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Ingresos acumulados — este mes")
        if this_month.empty:
            st.info("Sin ventas este mes todavía.")
        else:
            this_month_sorted = this_month.sort_values("date").copy()
            this_month_sorted["acumulado"] = this_month_sorted["revenue"].cumsum()
            fig = px.area(
                this_month_sorted, x="date", y="acumulado",
                labels={"date": "Fecha", "acumulado": "Ingresos acumulados (ARS)"},
                color_discrete_sequence=["#e91e8c"],
            )
            fig.update_layout(margin=dict(t=10, b=10), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Alertas")

        if sin_stock > 0:
            st.error(f"**{sin_stock} productos sin stock** — revisá Product Performance")
        if critico > 0:
            st.warning(f"**{critico} productos con stock critico** (1-2 unidades)")
        if pending > 0:
            st.warning(f"**${pending:,.0f} pendiente de cobro** — ordenes sin pagar")
        if len(unconverted) > 0:
            st.info(f"**{len(unconverted)} clientes sin convertir** — candidatos para campaña")
        if sin_stock == 0 and critico == 0 and pending == 0:
            st.success("Todo en orden, sin alertas.")

    st.divider()

    # --- Comparativa mensual ---
    st.subheader("Ingresos por mes — historico")
    monthly = daily_all.copy()
    monthly["month"] = pd.to_datetime(monthly["date"]).dt.strftime("%Y-%m")
    monthly_agg = monthly.groupby("month").agg(
        revenue=("revenue", "sum"),
        orders=("total_orders", "sum"),
    ).reset_index().sort_values("month")

    fig2 = px.bar(
        monthly_agg, x="month", y="revenue",
        labels={"month": "Mes", "revenue": "Ingresos (ARS)"},
        color_discrete_sequence=["#e91e8c"],
        text="revenue",
    )
    fig2.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig2.update_layout(margin=dict(t=30, b=10))
    st.plotly_chart(fig2, use_container_width=True)

    st.caption("Usá el menu de la izquierda para ver cada sección en detalle.")

except Exception as e:
    st.error(f"Error conectando a BigQuery: {e}")
    st.info("Verificá que el archivo .env tenga las credenciales correctas.")
