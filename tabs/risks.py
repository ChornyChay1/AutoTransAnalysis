import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score

#todo улучшить модель классификации
def render_risks_tab():
    df_filtered = st.session_state.get("filtered_df", pd.DataFrame())
    if df_filtered.empty:
        st.info("Сначала загрузите и очистите данные.")
        return

    df = df_filtered.copy()
    df["Дата инвойса или его отправки"] = pd.to_datetime(
        df["Дата инвойса или его отправки"], dayfirst=True, errors='coerce'
    )
    df["Возраст инвойса"] = (pd.Timestamp.today() - df["Дата инвойса или его отправки"]).dt.days.fillna(0)
    
    df_active = df[~df["Состояние инвойса"].isin(["Оплачен", "Просрочен", "Отменен"])].copy()
    
    features = [
        "Контрагент", "Страна", "Банк", "Канал продаж",
        "Возраст инвойса", "Сумма инвойса", "Сумма фактической оплаты", "Менеджер"
    ]
    display_cols = [
        "Номер инвойса", "Контрагент", "Страна", "Банк",
        "Канал продаж", "Менеджер", "Сумма инвойса",
        "Сумма фактической оплаты", "Возраст инвойса", "Состояние инвойса"
    ]

    df["Цель_просрочки"] = df["Состояние инвойса"].apply(lambda x: 1 if x == "Просрочен" else 0)
    df["Цель_отмены"] = df["Состояние инвойса"].apply(lambda x: 1 if x == "Отменен" else 0)

    # закодируем признаки чтобы случайный лес работал
    encoders = {}
    cat_cols = ["Контрагент", "Страна", "Банк", "Канал продаж", "Менеджер"]

    for col in cat_cols:
        le = LabelEncoder()
        df[col] = df[col].fillna("NA")
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    for col in cat_cols:
        le = encoders[col]
        df_active[col] = df_active[col].fillna("NA")
        df_active[col] = le.transform(df_active[col])

    # --- Подбор оптимального порога по F1-score
    def optimal_threshold(y_true, y_probs):
        thresholds = np.arange(0.1, 0.9, 0.01)
        f1_scores = [f1_score(y_true, (y_probs >= t).astype(int)) for t in thresholds]
        best_idx = np.argmax(f1_scores)
        return thresholds[best_idx]

    # --- Функция отображения метрик в колонках
    def show_metrics( y_true, probs, best_thresh): 
        col1, col2 = st.columns(2)
        with col1:
            st.metric("ROC-AUC", f"{roc_auc_score(y_true, probs):.3f}")
            st.metric("F1-score", f"{f1_score(y_true, (probs >= best_thresh).astype(int)):.3f}")
        with col2:
            st.metric("Precision", f"{precision_score(y_true, (probs >= best_thresh).astype(int)):.3f}")
            st.metric("Recall", f"{recall_score(y_true, (probs >= best_thresh).astype(int)):.3f}")

    # --- Модель риска просрочки(классификатор случайного леса)
    X_overdue = df[features]
    y_overdue = df["Цель_просрочки"]
    model_overdue = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    if len(np.unique(y_overdue)) > 1:
        model_overdue.fit(X_overdue, y_overdue)
        probs_train_overdue = model_overdue.predict_proba(X_overdue)[:,1]
        best_thresh_overdue = optimal_threshold(y_overdue, probs_train_overdue)
        probs_active_overdue = model_overdue.predict_proba(df_active[features])[:,1]
        df_active["Вероятность_просрочки"] = probs_active_overdue
        with st.expander("Метрики модели просрочки", expanded=True):
            show_metrics(y_overdue, probs_train_overdue, best_thresh_overdue)
    else:
        df_active["Вероятность_просрочки"] = 0
        st.info("Недостаточно данных для оценки просрочки.")

    # --- Модель риска отмены(классификатор случайного леса)
    X_cancel = df[features]
    y_cancel = df["Цель_отмены"]
    model_cancel = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    if len(np.unique(y_cancel)) > 1:
        model_cancel.fit(X_cancel, y_cancel)
        probs_train_cancel = model_cancel.predict_proba(X_cancel)[:,1]
        best_thresh_cancel = optimal_threshold(y_cancel, probs_train_cancel)
        probs_active_cancel = model_cancel.predict_proba(df_active[features])[:,1]
        df_active["Вероятность_отмены"] = probs_active_cancel
        with st.expander("Метрики модели отмены", expanded=False):
            show_metrics( y_cancel, probs_train_cancel, best_thresh_cancel)
    else:
        df_active["Вероятность_отмены"] = 0
        st.info("Недостаточно данных для оценки отмены.")

    # --- Отобразим таблицы
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Активные инвойсы: вероятность просрочки")
        st.dataframe(
            df_active[display_cols + ["Вероятность_просрочки"]]
            .sort_values("Вероятность_просрочки", ascending=False),
            height=500
        )
    with col2:
        st.markdown("### Активные инвойсы: вероятность отмены")
        st.dataframe(
            df_active[display_cols + ["Вероятность_отмены"]]
            .sort_values("Вероятность_отмены", ascending=False),
            height=500
        )

    # --- Сохраняем данные для отчёта 
    risks_report = {}

    if len(np.unique(y_overdue)) > 1:
        risks_report["Метрики модели просрочки"] = pd.DataFrame([{
            "ROC-AUC": roc_auc_score(y_overdue, probs_train_overdue),
            "F1-score": f1_score(y_overdue, (probs_train_overdue >= best_thresh_overdue).astype(int)),
            "Precision": precision_score(y_overdue, (probs_train_overdue >= best_thresh_overdue).astype(int)),
            "Recall": recall_score(y_overdue, (probs_train_overdue >= best_thresh_overdue).astype(int))
        }])

    if len(np.unique(y_cancel)) > 1:
        risks_report["Метрики модели отмены"] = pd.DataFrame([{
            "ROC-AUC": roc_auc_score(y_cancel, probs_train_cancel),
            "F1-score": f1_score(y_cancel, (probs_train_cancel >= best_thresh_cancel).astype(int)),
            "Precision": precision_score(y_cancel, (probs_train_cancel >= best_thresh_cancel).astype(int)),
            "Recall": recall_score(y_cancel, (probs_train_cancel >= best_thresh_cancel).astype(int))
        }])

    risks_report["Активные инвойсы: вероятность просрочки"] = (
        df_active[display_cols + ["Вероятность_просрочки"]]
        .sort_values("Вероятность_просрочки", ascending=False)
    )
    risks_report["Активные инвойсы: вероятность отмены"] = (
        df_active[display_cols + ["Вероятность_отмены"]]
        .sort_values("Вероятность_отмены", ascending=False)
    )

    st.session_state['df_risks'] = risks_report 
    st.info("Риски рассчитаны.")  
