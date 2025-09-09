import streamlit as st
from tabs.upload import render_upload_tab
from tabs.clean import render_clean_tab
from tabs.analysis import render_analysis_tab
from tabs.kpi import render_kpi_tab
from tabs.risks import render_risks_tab
from tabs.final_report import render_final_report_tab  

st.set_page_config(page_title="MVP мониторинга выручки", layout="wide")
st.title("MVP мониторинга экспортной выручки")

tab_upload, tab_clean, tab_analysis, tab_kpi, tab_risks, tab_report = st.tabs([
    "Загрузка данных", "Очистка", "Фильтрация и экспорт", "KPI", "Риски", "Итоговый отчёт"
])

if "df" not in st.session_state:
    st.session_state.df = None

df = st.session_state.df
with tab_upload:
    render_upload_tab()
with tab_clean:
    render_clean_tab()
with tab_analysis:
    render_analysis_tab()
with tab_kpi:
    render_kpi_tab()
with tab_risks:
    render_risks_tab()
with tab_report:
    render_final_report_tab()
