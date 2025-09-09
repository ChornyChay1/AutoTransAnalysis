import streamlit as st
from io import BytesIO
import pandas as pd
from datetime import datetime
def render_analysis_tab():
    df_clean = st.session_state.get('df_clean', pd.DataFrame())
    params = st.session_state.get('clean_params', {})

    if df_clean.empty or not params:
        st.info("Сначала загрузите и очистите данные.")
        return

    df_filtered = df_clean.copy()
    #--Фильтры
    with st.expander("Фильтры", expanded=True): 
        if "Дата инвойса или его отправки" in df_filtered.columns:
            df_filtered["Дата инвойса или его отправки"] = pd.to_datetime(
                df_filtered["Дата инвойса или его отправки"], errors='coerce'
            )

            min_date = df_filtered["Дата инвойса или его отправки"].min()
            max_date = df_filtered["Дата инвойса или его отправки"].max()

            date_range = st.date_input(
                "Выберите период",
                value=(min_date, max_date) if pd.notna(min_date) and pd.notna(max_date) else None,
                min_value=min_date,
                max_value=max_date
            )

            if date_range and len(date_range) == 2:
                start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
                df_filtered = df_filtered[
                    (df_filtered["Дата инвойса или его отправки"] >= start_date) &
                    (df_filtered["Дата инвойса или его отправки"] <= end_date)
                ]
                 
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if "Контрагент" in df_filtered.columns:
                selected_clients = st.multiselect(
                    "Контрагент",
                    options=df_filtered["Контрагент"].dropna().unique()
                )
                if selected_clients:
                    df_filtered = df_filtered[df_filtered["Контрагент"].isin(selected_clients)]

        with col2:
            if "Страна" in df_filtered.columns:
                selected_countries = st.multiselect(
                    "Страна",
                    options=df_filtered["Страна"].dropna().unique()
                )
                if selected_countries:
                    df_filtered = df_filtered[df_filtered["Страна"].isin(selected_countries)]

        with col3:
            if "Валюта инвойса" in df_filtered.columns:
                selected_currency = st.multiselect(
                    "Валюта",
                    options=df_filtered["Валюта инвойса"].dropna().unique()
                )
                if selected_currency:
                    df_filtered = df_filtered[df_filtered["Валюта инвойса"].isin(selected_currency)]

        with col4:
            if "Менеджер" in df_filtered.columns:
                selected_managers = st.multiselect(
                    "Менеджер",
                    options=df_filtered["Менеджер"].dropna().unique()
                )
                if selected_managers:
                    df_filtered = df_filtered[df_filtered["Менеджер"].isin(selected_managers)]
                     
        if "Состояние инвойса" in df_filtered.columns:
            selected_status = st.multiselect(
                "Статус",
                options=df_filtered["Состояние инвойса"].dropna().unique()
            )
            if selected_status:
                df_filtered = df_filtered[df_filtered["Состояние инвойса"].isin(selected_status)]

    st.metric("Количество строк в базе", len(df_filtered))
    st.dataframe(df_filtered.head(100), height=500)

    st.session_state.filtered_df = df_filtered
    filtered_df = df_filtered

    #--Экспорт
    #todo 
    #добавить pdf и word 
    if not filtered_df.empty:
        st.markdown("### Экспорт данных")
        export_format = st.radio("Выберите формат для экспорта:", ["Excel", "CSV"], horizontal=True)

        if export_format == "Excel":
            output = BytesIO()
            filtered_df.to_excel(output, index=False)
            output.seek(0)
            st.download_button(
                "Скачать Excel",
                output,
                file_name="report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        elif export_format == "CSV":
            csv_data = filtered_df.to_csv(index=False, encoding="cp1251").encode("cp1251")
            st.download_button(
                "Скачать CSV",
                csv_data,
                file_name="report.csv",
                mime="text/csv"
            )
