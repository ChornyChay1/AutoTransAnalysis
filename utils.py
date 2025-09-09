import re
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import streamlit as st

#todo 
#ускорить
#мы обращаемся к цб и запрашиваем кодировки по дате. процесс длительный 
def get_cb_rate(currency: str, date_str: str):
    try:
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
            try:
                dt = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        else:
            return None
        if currency.upper() == "RUB":
            return 1.0
        date_req = dt.strftime("%d/%m/%Y")
        url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_req}"
        r = requests.get(url)
        root = ET.fromstring(r.content)
        for val in root.findall("Valute"):
            if val.find("CharCode").text == currency:
                value = val.find("Value").text.replace(",", ".")
                nominal = val.find("Nominal").text
                return float(value) / float(nominal)
        return None
    except:
        return None
#кеширование 
#todo 
#добавить больше кеширование, чтобы не сбивать процесс после перезагрузки
@st.cache_data(show_spinner=False)
def get_cb_rate_cached(currency: str, date_str: str):
    return get_cb_rate(currency, date_str)

def parse_amount(x):
    if pd.isna(x) or str(x).strip() == "":
        return None
    try:
        s = str(x).replace("≈", "")
        s = re.sub(r"[^0-9,\.]", "", s)
        s = s.replace(",", ".")
        return float(s) if s else None
    except:
        return None

def parse_date(x):
    if pd.isna(x) or str(x).strip() == "":
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(x), fmt).strftime("%d.%m.%Y")
        except:
            continue
    return None
