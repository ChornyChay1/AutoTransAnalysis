import streamlit as st
import pandas as pd
#todo 
#расширить kpi, добавить графики 

def render_kpi_tab():
    st.subheader("KPI-блок")
    df_clean = st.session_state.get('df_clean', pd.DataFrame())

    if df_clean.empty:
        st.info("Нет данных для расчёта KPI. Примените фильтры на вкладке 'Анализ'.")
        st.session_state['df_kpi'] = {}   
        return

    today = pd.Timestamp.today().normalize()

    # --- Горизонт расчёта ожидаемых поступлений  
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        N = st.number_input(
            "Горизонт расчёта ожидаемых поступлений (дней)",
            value=7,
            min_value=1,
            max_value=365
        )

    statuses = df_clean['Состояние инвойса'].astype(str).str.strip().str.lower()
    df_dates = pd.to_datetime(df_clean.get('Дата фактического зачисления', pd.Series([pd.NaT]*len(df_clean))),
                              dayfirst=True, errors='coerce')

    # --- Ожидаемые поступления 
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Ожидаемые поступления")
        if 'Сумма инвойса' in df_clean.columns:
            amounts = pd.to_numeric(df_clean['Сумма инвойса'], errors='coerce')
            expected_mask = (statuses == 'в процессе') & df_dates.notna() & (df_dates <= today + pd.Timedelta(days=N))
            expected_sum = amounts[expected_mask].sum()
            st.metric(f"Ожидаемые поступления за {N} дней", f"{expected_sum:,.2f} ₽")
        else:
            st.info("Нет данных для расчёта ожидаемых поступлений.")
            expected_sum = 0
    col1, col2 = st.columns(2)

    # --- Доля просроченных 
    with col1:
        st.markdown("### Просрочки")
        overdue_mask = (statuses != 'оплачен') & df_dates.notna() & (df_dates < today)
        overdue_count = overdue_mask.sum()
        overdue_share = overdue_count / len(df_clean) * 100 if len(df_clean) > 0 else 0
        st.metric("Доля просроченных инвойсов", f"{overdue_share:.1f}% ({overdue_count} шт)")

        # Доля просроченных по контрагентам
        df_client_overdue = pd.DataFrame()
        if 'Контрагент' in df_clean.columns and overdue_count > 0:
            overdue_by_client = df_clean.loc[overdue_mask].groupby('Контрагент').size()
            total_by_client = df_clean.groupby('Контрагент').size()
            share_by_client = (overdue_by_client / total_by_client * 100).round(1).astype(str) + "%"
            df_client_overdue = pd.DataFrame({
                "Контрагент": overdue_by_client.index,
                "Количество просроченных": overdue_by_client.values,
                "Доля просроченных": share_by_client.values
            }).sort_values("Доля просроченных", ascending=False)
            st.table(df_client_overdue)

    # --- Рейтинг контрагентов по оплате  
    df_payment_rating = pd.DataFrame()
    with col2:
        st.markdown("### Оплата")
        invoice_sum = pd.to_numeric(df_clean['Сумма инвойса'], errors='coerce')
        paid_sum = pd.to_numeric(df_clean['Сумма фактической оплаты'], errors='coerce')
        paid_mask = invoice_sum > 0 
        if paid_mask.sum() > 0: 
            avg_payment_ratio = (paid_sum[paid_mask] / invoice_sum[paid_mask]).mean()
            st.metric("Средний процент оплаты", f"{avg_payment_ratio*100:.1f}%")
        required_cols = ["Сумма фактической оплаты", "Сумма инвойса"]
        if all(col in df_clean.columns for col in required_cols) and 'Контрагент' in df_clean.columns:
            payment_ratio = df_clean.groupby('Контрагент').apply(
                lambda x: x['Сумма фактической оплаты'].sum() / x['Сумма инвойса'].sum()
                if x['Сумма инвойса'].sum() > 0 else 0
            )
            df_payment_rating = payment_ratio.sort_values(ascending=False).reset_index()
            df_payment_rating.columns = ["Контрагент", "Процент оплаты"]
            df_payment_rating["Процент оплаты"] = (df_payment_rating["Процент оплаты"] * 100).round(1).astype(str) + "%"
            # Создаём "скрытый" индекс для таблицы
            df_payment_display = df_payment_rating.copy()
            df_payment_display.index = [""] * len(df_payment_display)
            st.table(df_payment_display)

    #--Сохраняем состояние
    st.session_state['df_kpi'] = {
        "Ожидаемые поступления": pd.DataFrame([{"Ожидаемые поступления за N дней": f"{expected_sum:,.2f} ₽"}]),
        "Доля просроченных": pd.DataFrame([{"Доля просроченных инвойсов": f"{overdue_share:.1f}% ({overdue_count} шт)"}]),
        "Средний процент оплаты": pd.DataFrame([{"Средний процент оплаты": f"{avg_payment_ratio*100:.1f}%"}]),
        "Доля просроченных по контрагентам": df_client_overdue,
        "Рейтинг контрагентов по оплате": df_payment_rating
    }