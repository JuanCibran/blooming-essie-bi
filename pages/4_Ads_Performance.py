import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from dashboard.data import get_ads_performance, get_roas, table_exists
from dashboard.filters import date_filter

st.set_page_config(page_title="Ads Performance", layout="wide")
st.title("Ads Performance")
st.divider()

if not table_exists("facebook_campaign_insights"):
    st.warning("Los datos de Facebook Ads todavia no estan cargados.")
    st.info("Configurá las credenciales de Facebook Ads en el archivo .env y volvé a correr el pipeline.")
    st.stop()

try:
    ads_all = get_ads_performance()
    roas_all = get_roas()

    ads, start, end = date_filter(ads_all)
    roas_df = roas_all.copy()
    roas_df["date"] = pd.to_datetime(roas_df["date"]).dt.date
    roas_df = roas_df[(roas_df["date"] >= start) & (roas_df["date"] <= end)]

    if ads.empty:
        st.warning("Sin datos para el período seleccionado.")
        st.stop()

    # --- KPIs globales ---
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    avg_roas = roas_df["roas"].mean() if not roas_df.empty else 0
    with col1:
        st.metric("Gasto Total", f"${ads['spend'].sum():,.0f}")
    with col2:
        st.metric("Impresiones", f"{int(ads['impressions'].sum()):,}")
    with col3:
        st.metric("Clicks", f"{int(ads['clicks'].sum()):,}")
    with col4:
        st.metric("CTR Promedio", f"{ads['ctr'].mean():.2f}%")
    with col5:
        st.metric("CPC Promedio", f"${ads['cpc'].mean():,.0f}")
    with col6:
        st.metric("ROAS Promedio", f"{avg_roas:.2f}x",
                  delta="Bueno" if avg_roas >= 3 else "Bajo",
                  delta_color="normal" if avg_roas >= 3 else "inverse")

    st.divider()

    # --- Métricas por campaña ---
    st.subheader("Por campaña")
    camp = (
        ads.groupby("campaign_name")
        .agg(spend=("spend", "sum"), impressions=("impressions", "sum"),
             clicks=("clicks", "sum"), ctr=("ctr", "mean"), cpc=("cpc", "mean"))
        .reset_index()
        .sort_values("spend", ascending=False)
    )
    for _, row in camp.iterrows():
        st.markdown(f"**{row['campaign_name']}**")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Gasto", f"${row['spend']:,.0f}")
        c2.metric("Impresiones", f"{int(row['impressions']):,}")
        c3.metric("Clicks", f"{int(row['clicks']):,}")
        c4.metric("CTR", f"{row['ctr']:.2f}%")
        c5.metric("CPC", f"${row['cpc']:,.0f}")

    st.divider()

    # --- ROAS diario: Gasto vs Revenue ---
    if not roas_df.empty:
        st.subheader("ROAS diario — Gasto vs Revenue")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=roas_df["date"], y=roas_df["ad_spend"], name="Gasto en Ads", marker_color="#f8a4d0"))
        fig.add_trace(go.Bar(x=roas_df["date"], y=roas_df["revenue"], name="Revenue", marker_color="#e91e8c"))
        fig.add_trace(go.Scatter(x=roas_df["date"], y=roas_df["roas"], name="ROAS", yaxis="y2",
                                 mode="lines+markers", line=dict(color="#9c1463", width=2)))
        fig.update_layout(
            barmode="group",
            yaxis=dict(title="ARS"),
            yaxis2=dict(title="ROAS", overlaying="y", side="right"),
            hovermode="x unified",
            margin=dict(t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

    # --- Detalle diario ---
    st.subheader("Detalle diario")
    st.dataframe(
        ads.rename(columns={
            "date": "Fecha", "campaign_name": "Campaña",
            "impressions": "Impresiones", "clicks": "Clicks",
            "spend": "Gasto", "ctr": "CTR %", "cpc": "CPC",
        }),
        use_container_width=True,
        hide_index=True,
    )

except Exception as e:
    st.error(f"Error: {e}")
