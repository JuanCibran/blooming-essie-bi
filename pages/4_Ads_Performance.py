import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
import plotly.express as px
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
    import pandas as pd
    roas_df["date"] = pd.to_datetime(roas_df["date"]).dt.date
    roas_df = roas_df[(roas_df["date"] >= start) & (roas_df["date"] <= end)]

    if ads.empty:
        st.warning("Sin datos para el período seleccionado.")
        st.stop()

    # KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Gasto Total", f"${ads['spend'].sum():,.0f}")
    with col2:
        st.metric("Clicks Totales", f"{int(ads['clicks'].sum()):,}")
    with col3:
        st.metric("Impresiones", f"{int(ads['impressions'].sum()):,}")
    with col4:
        st.metric("CTR Promedio", f"{ads['ctr'].mean():.2f}%")
    with col5:
        avg_roas = roas_df['roas'].mean() if not roas_df.empty else 0
        st.metric("ROAS Promedio", f"{avg_roas:.2f}x",
                  delta="Bueno" if avg_roas >= 3 else "Bajo",
                  delta_color="normal" if avg_roas >= 3 else "inverse")

    st.divider()

    st.subheader("ROAS diario — Gasto vs Revenue")
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=roas_df["date"], y=roas_df["ad_spend"], name="Gasto en Ads", marker_color="#f8a4d0"))
    fig1.add_trace(go.Bar(x=roas_df["date"], y=roas_df["revenue"], name="Revenue", marker_color="#e91e8c"))
    fig1.add_trace(go.Scatter(x=roas_df["date"], y=roas_df["roas"], name="ROAS", yaxis="y2",
                              mode="lines+markers", line=dict(color="#9c1463", width=2)))
    fig1.update_layout(
        barmode="group",
        yaxis=dict(title="ARS"),
        yaxis2=dict(title="ROAS", overlaying="y", side="right"),
        hovermode="x unified",
        margin=dict(t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig1, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Gasto por campaña")
        camp = ads.groupby("campaign_name")["spend"].sum().reset_index().sort_values("spend", ascending=False)
        fig2 = px.bar(camp, x="spend", y="campaign_name", orientation="h",
                      labels={"spend": "Gasto (ARS)", "campaign_name": "Campaña"},
                      color_discrete_sequence=["#e91e8c"], text="spend")
        fig2.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig2.update_layout(margin=dict(t=10, b=10), yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

    with col_right:
        st.subheader("CTR por campaña")
        ctr_camp = ads.groupby("campaign_name")["ctr"].mean().reset_index().sort_values("ctr", ascending=False)
        fig3 = px.bar(ctr_camp, x="ctr", y="campaign_name", orientation="h",
                      labels={"ctr": "CTR (%)", "campaign_name": "Campaña"},
                      color_discrete_sequence=["#9c1463"], text="ctr")
        fig3.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig3.update_layout(margin=dict(t=10, b=10), yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Detalle por campaña")
    st.dataframe(
        ads.rename(columns={
            "date": "Fecha", "campaign_name": "Campaña", "adset_name": "Conjunto",
            "impressions": "Impresiones", "clicks": "Clicks",
            "spend": "Gasto", "ctr": "CTR %", "cpc": "CPC",
        }),
        use_container_width=True,
        hide_index=True,
    )

except Exception as e:
    st.error(f"Error: {e}")
