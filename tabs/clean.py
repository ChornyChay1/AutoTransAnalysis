import streamlit as st
from utils import parse_amount, parse_date, get_cb_rate_cached
from datetime import datetime
import pandas as pd
def render_clean_tab():
    df = st.session_state.df
    #todo
    #сейчас очистка направлена на существующих образец данных 
    #для работы необходимо учесть и другие возможные помехи в данных, проверять их и исправлять
    if df is not None:
        st.subheader("Параметры очистки")
        col1, col2, col3 = st.columns(3)
        with col1:
            fill_cross = st.checkbox("Заполнять пустые кросс-курсы", value=True, key="fill_cross")
            convert_amounts = st.checkbox("Преобразовать суммы", value=True, key="convert_amounts")
        with col2:
            convert_dates = st.checkbox("Преобразовать даты", value=True, key="convert_dates")
            drop_duplicates = st.checkbox("Удалять дубликаты", value=True, key="drop_duplicates")
        with col3:
            adjust_statuses = st.checkbox("Корректировка статусов", value=True, key="adjust_statuses")

        # Инициализация лога в session_state
        if "clean_log" not in st.session_state:
            st.session_state.clean_log = []

        if st.button("Применить очистку"):
            st.session_state.clean_params = {
                "fill_cross": fill_cross,
                "convert_amounts": convert_amounts,
                "convert_dates": convert_dates,
                "drop_duplicates": drop_duplicates,
                "adjust_statuses": adjust_statuses
            }

            df_clean = df.copy()
            df_clean.columns = [col[:1].upper() + col[1:] if col else col for col in df_clean.columns]

            def add_log(msg):
                """Добавляем запись в лог с текущим временем"""
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.clean_log.append(f"[{now}] {msg}")


            if convert_amounts:
                for col in ["Сумма инвойса", "Сумма фактической оплаты"]:
                    if col in df_clean.columns:
                        df_clean[col] = df_clean[col].apply(parse_amount)
                        add_log(f"Преобразование сумм в колонке '{col}' выполнено.")

            if convert_dates:
                for date_col in ["Дата инвойса или его отправки", "Дата фактического зачисления"]:
                    if date_col in df_clean.columns:
                        # parse_date теперь возвращает datetime или None
                        df_clean[date_col] = df_clean[date_col].apply(parse_date)
                        add_log(f"Преобразование дат в колонке '{date_col}' выполнено.")

            if drop_duplicates and "Номер инвойса" in df_clean.columns:
                before = len(df_clean)
                df_clean = df_clean.drop_duplicates(subset=["Номер инвойса"])
                after = len(df_clean)
                add_log(f"Удаление дубликатов по 'Номер инвойса': удалено {before-after} строк.")

            if fill_cross and all(col in df_clean.columns for col in ["Кросс-курс", "Валюта инвойса", "Дата инвойса или его отправки"]):
                total = len(df_clean)
                changed = 0
                progress = st.progress(0)
                for i, row in df_clean.iterrows():
                    if pd.isna(row["Кросс-курс"]) or row["Кросс-курс"] == "":
                        rate = get_cb_rate_cached(row["Валюта инвойса"], row["Дата инвойса или его отправки"])
                        if rate:
                            df_clean.at[i, "Кросс-курс"] = rate
                            changed += 1
                    progress.progress(min(int((i + 1) / total * 100), 100))
                progress.empty()
                add_log(f"Заполнение пустых кросс-курсов: изменено {changed} строк.")
                df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors='coerce')

            if adjust_statuses and all(col in df_clean.columns for col in ["Состояние инвойса", "Сумма фактической оплаты", "Дата фактического зачисления", "Комментарий"]):
                changed = 0
                for i, row in df_clean.iterrows():
                    status = str(row["Состояние инвойса"]).strip().lower()
                    comment = str(row["Комментарий"]).lower() if pd.notna(row["Комментарий"]) else ""
                    amount = row["Сумма фактической оплаты"]
                    date = row["Дата фактического зачисления"]
                    new_status = status
                    if status == "оплачен":
                        if "ожидаем swift" in comment or "пересчёт кросс-курса" in comment or pd.isna(amount) or pd.isna(date):
                            new_status = "в процессе"
                    elif status == "частично оплачен":
                        if pd.isna(amount) or pd.isna(date):
                            new_status = "в процессе"
                    if new_status != status:
                        df_clean.at[i, "Состояние инвойса"] = new_status
                        changed += 1
                add_log(f"Корректировка статусов инвойсов: изменено {changed} строк.")

            st.session_state.df_clean = df_clean
            st.success("Очистка выполнена. Данные ниже:")

        if "df_clean" in st.session_state:
            st.write("### Очищенные данные")
            st.dataframe(st.session_state.df_clean.head(100), height=600)

            if st.session_state.clean_log:
                st.subheader("Лог очистки данных")
                with st.expander("Журнал очистки данных", expanded=True):
                    st.markdown("\n".join([f"- {item}" for item in st.session_state.clean_log]))
                    log_text = "\n".join(st.session_state.clean_log)
                    st.download_button("Скачать лог в формате TXT", log_text, file_name="clean_log.txt", mime="text/plain")
    else:
        st.info("Сначала загрузите данные на вкладке Загрузка данных.")
