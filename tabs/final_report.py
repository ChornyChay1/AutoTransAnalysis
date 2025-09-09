import streamlit as st
import pandas as pd
from io import BytesIO
    #todo
    #добавить графики, сводные таблицы
def render_final_report_tab():
    st.subheader("Формирование итогового отчёта (Excel)")
    df_raw = st.session_state.get("df")
    if not isinstance(df_raw, pd.DataFrame):
        df_raw = pd.DataFrame()

    df_clean = st.session_state.get("df_clean")
    if not isinstance(df_clean, pd.DataFrame):
        df_clean = pd.DataFrame()

    df_filtered = st.session_state.get("filtered_df")
    if not isinstance(df_filtered, pd.DataFrame):
        df_filtered = pd.DataFrame()

    df_risks = st.session_state.get("df_risks")
    if not isinstance(df_risks, dict):    
        df_risks = {}

    df_kpi = st.session_state.get("df_kpi")
    if not isinstance(df_kpi, dict):     
        df_kpi = {}

    clean_log = st.session_state.get("clean_log")
    if not isinstance(clean_log, list):
        clean_log = []

    if df_raw.empty and df_clean.empty and df_filtered.empty and not df_risks and not df_kpi and not clean_log:
        st.info("Нет данных для формирования отчёта. Загрузите и очистите файлы.")
        return

    if st.button("Сформировать Excel-отчёт"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            if not df_raw.empty:
                df_raw.to_excel(writer, sheet_name="Исходные данные", index=False)
            if not df_clean.empty:
                df_clean.to_excel(writer, sheet_name="Очищенные данные", index=False)
            if not df_filtered.empty:
                df_filtered.to_excel(writer, sheet_name="Фильтрованные данные", index=False)

            workbook = writer.book

            # Общие форматы
            header_fmt   = workbook.add_format({'bold': True, 'bg_color': '#DDEBF7', 'border': 1})
            bold_fmt     = workbook.add_format({'bold': True})
            percent_fmt  = workbook.add_format({'num_format': '0.0%', 'border': 1})
            money_fmt    = workbook.add_format({'num_format': '#,##0.00" ₽"', 'border': 1})
            text_fmt     = workbook.add_format({'border': 1, 'text_wrap': True})

            # --- KPI ---
            if df_kpi:
                worksheet = workbook.add_worksheet("KPI")
                writer.sheets["KPI"] = worksheet

                row_pos = 0
                worksheet.write(row_pos, 0, "KPI-отчёт", header_fmt)
                row_pos += 2

                for block_name, block_data in df_kpi.items():
                    worksheet.write(row_pos, 0, block_name, bold_fmt)
                    row_pos += 1

                    if isinstance(block_data, pd.DataFrame) and not block_data.empty:
                        block_data = block_data.reset_index(drop=True)
                        block_data.to_excel(writer, sheet_name="KPI", startrow=row_pos, startcol=0, index=False)

                        for col_num, value in enumerate(block_data.columns.values):
                            worksheet.write(row_pos, col_num, value, header_fmt)

                        for r in range(len(block_data)):
                            for c, col_name in enumerate(block_data.columns):
                                cell_val = block_data.iloc[r, c]
                                if "сумма" in col_name.lower():
                                    try:
                                        worksheet.write(row_pos+1+r, c, float(str(cell_val).replace("₽","").replace(" ","")), money_fmt)
                                    except:
                                        worksheet.write(row_pos+1+r, c, str(cell_val), text_fmt)
                                elif "процент" in col_name.lower():
                                    try:
                                        val = float(str(cell_val).replace("%",""))/100
                                        worksheet.write(row_pos+1+r, c, val, percent_fmt)
                                    except:
                                        worksheet.write(row_pos+1+r, c, str(cell_val), text_fmt)
                                else:
                                    worksheet.write(row_pos+1+r, c, cell_val, text_fmt)

                        row_pos += len(block_data) + 3
                    else:
                        val = block_data
                        try:
                            num = float(val)
                            if "процент" in block_name.lower():
                                worksheet.write(row_pos, 0, num/100, percent_fmt)
                            else:
                                worksheet.write(row_pos, 0, num, money_fmt)
                        except:
                            worksheet.write(row_pos, 0, str(val), text_fmt)
                        row_pos += 3

                for i in range(worksheet.dim_colmax + 1):
                    worksheet.set_column(i, i, 25)
 
            #--Риски
            if df_risks:
                worksheet = workbook.add_worksheet("Риски")
                writer.sheets["Риски"] = worksheet

                row_pos = 0
                worksheet.write(row_pos, 0, "Анализ рисков", header_fmt)
                row_pos += 2

                for block_name, block_data in df_risks.items():
                    worksheet.write(row_pos, 0, block_name, bold_fmt)
                    row_pos += 1

                    if isinstance(block_data, pd.DataFrame) and not block_data.empty:
                        block_data = block_data.reset_index(drop=True)
                        block_data.to_excel(writer, sheet_name="Риски", startrow=row_pos, startcol=0, index=False)

                        for col_num, value in enumerate(block_data.columns.values):
                            worksheet.write(row_pos, col_num, value, header_fmt)

                        for r in range(len(block_data)):
                            for c, col_name in enumerate(block_data.columns):
                                cell_val = block_data.iloc[r, c]
                                if "сумма" in col_name.lower():
                                    try:
                                        worksheet.write(row_pos+1+r, c, float(str(cell_val).replace("₽","").replace(" ","")), money_fmt)
                                    except:
                                        worksheet.write(row_pos+1+r, c, str(cell_val), text_fmt)
                                elif "процент" in col_name.lower():
                                    try:
                                        val = float(str(cell_val).replace("%",""))/100
                                        worksheet.write(row_pos+1+r, c, val, percent_fmt)
                                    except:
                                        worksheet.write(row_pos+1+r, c, str(cell_val), text_fmt)
                                else:
                                    worksheet.write(row_pos+1+r, c, cell_val, text_fmt)

                        row_pos += len(block_data) + 3
                    else:
                        val = block_data
                        try:
                            num = float(val)
                            if "процент" in block_name.lower():
                                worksheet.write(row_pos, 0, num/100, percent_fmt)
                            else:
                                worksheet.write(row_pos, 0, num, money_fmt)
                        except:
                            worksheet.write(row_pos, 0, str(val), text_fmt)
                        row_pos += 3

                for i in range(worksheet.dim_colmax + 1):
                    worksheet.set_column(i, i, 25)

            #--Журнал
            if clean_log:
                log_df = pd.DataFrame({"Журнал очистки": clean_log})
                log_df.to_excel(writer, sheet_name="Лог очистки", index=False)

        st.download_button(
            label="Скачать итоговый отчёт (Excel)",
            data=output.getvalue(),
            file_name="final_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
