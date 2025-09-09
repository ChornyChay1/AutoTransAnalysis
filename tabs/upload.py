import streamlit as st
import pandas as pd

def render_upload_tab():
    up = st.file_uploader("Загрузите CSV/Excel", type=["csv", "xlsx"])
    if up:
        if up.name.endswith(".csv"):
            df = pd.read_csv(up, encoding="utf-8", sep=None, engine="python")
        else:
            df = pd.read_excel(up)
         
        df.columns = [c.strip().replace('\ufeff', '') for c in df.columns]
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
         
        st.session_state.df = df
         
        required_cols = [
            "Номер инвойса",
            "Контрагент",
            "Сумма инвойса",
            "Состояние инвойса",
            "Сумма фактической оплаты",
            "Дата инвойса или его отправки",
            "Дата фактического зачисления",
            "Валюта инвойса",
            "Комментарий",
            "кросс-курс"
        ]
        
        #Проверяем наличие колонок
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"В датасете отсутствуют обязательные колонки: {', '.join(missing_cols)}. Очистка будет недоступна.")
        else:
            st.success("Все обязательные колонки присутствуют. Датасет готов к очистке.")
            st.write("### Первые 100 строк")
            st.dataframe(df.head(100), height=600)
    else:
        st.info("Загрузите файл, чтобы продолжить.")