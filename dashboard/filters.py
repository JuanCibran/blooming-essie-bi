import streamlit as st
import pandas as pd
from datetime import date, timedelta


def date_filter(df: pd.DataFrame, date_col: str = "date"):
    """
    Renderiza selector de período en el sidebar y filtra el DataFrame.
    Retorna (df_filtrado, fecha_inicio, fecha_fin).
    """
    today = date.today()

    with st.sidebar:
        st.header("Período")
        periodo = st.radio(
            "Seleccioná un período",
            ["Este mes", "Mes anterior", "Últimos 7 días",
             "Últimos 30 días", "Últimos 90 días", "Este año", "Todo"],
            index=0,
        )

    first_of_month = today.replace(day=1)

    if periodo == "Este mes":
        start, end = first_of_month, today
    elif periodo == "Mes anterior":
        last_month_end = first_of_month - timedelta(days=1)
        start, end = last_month_end.replace(day=1), last_month_end
    elif periodo == "Últimos 7 días":
        start, end = today - timedelta(days=7), today
    elif periodo == "Últimos 30 días":
        start, end = today - timedelta(days=30), today
    elif periodo == "Últimos 90 días":
        start, end = today - timedelta(days=90), today
    elif periodo == "Este año":
        start, end = today.replace(month=1, day=1), today
    else:
        start = pd.to_datetime(df[date_col]).dt.date.min() if not df.empty else first_of_month
        end = today

    with st.sidebar:
        st.caption(f"{start.strftime('%d/%m/%Y')} → {end.strftime('%d/%m/%Y')}")

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col]).dt.date
    return df[(df[date_col] >= start) & (df[date_col] <= end)].copy(), start, end
