import streamlit as st
import pandas as pd
from datetime import date, timedelta


def date_filter(df: pd.DataFrame, date_col: str = "date") -> tuple[pd.DataFrame, date, date]:
    """
    Renderiza selector de período en el sidebar y filtra el DataFrame.
    Retorna (df_filtrado, fecha_inicio, fecha_fin).
    """
    today = date.today()
    first_of_month = today.replace(day=1)

    with st.sidebar:
        st.header("Filtrar período")
        periodo = st.selectbox(
            "Período",
            ["Este mes", "Mes anterior", "Últimos 7 días", "Últimos 30 días",
             "Últimos 90 días", "Este año", "Todo"],
            index=0,
        )

        if periodo == "Este mes":
            start = first_of_month
            end = today
        elif periodo == "Mes anterior":
            last_month_end = first_of_month - timedelta(days=1)
            start = last_month_end.replace(day=1)
            end = last_month_end
        elif periodo == "Últimos 7 días":
            start = today - timedelta(days=7)
            end = today
        elif periodo == "Últimos 30 días":
            start = today - timedelta(days=30)
            end = today
        elif periodo == "Últimos 90 días":
            start = today - timedelta(days=90)
            end = today
        elif periodo == "Este año":
            start = today.replace(month=1, day=1)
            end = today
        else:
            start = df[date_col].min() if not df.empty else first_of_month
            end = today

        # Selector manual de rango
        custom = st.date_input(
            "O elegí rango personalizado",
            value=(start, end),
            max_value=today,
        )
        if isinstance(custom, (list, tuple)) and len(custom) == 2:
            start, end = custom[0], custom[1]

        st.caption(f"Mostrando: {start.strftime('%d/%m/%Y')} → {end.strftime('%d/%m/%Y')}")

    df[date_col] = pd.to_datetime(df[date_col]).dt.date
    mask = (df[date_col] >= start) & (df[date_col] <= end)
    return df[mask].copy(), start, end
