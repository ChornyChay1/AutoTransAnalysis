import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Загрузка CSV
df = pd.read_csv("report.csv")

# Создадим бинарный таргет "Просрочен" = 1, остальные = 0
df["Просрочка"] = df["Состояние инвойса"].apply(lambda x: 1 if x.lower() == "просрочен" else 0)

# Посчитаем количество просрочек по INCOTERMS
overdue_counts = df.groupby("ИНКОТЕРМС")["Просрочка"].sum().reset_index()

# Сортировка для удобства визуализации
overdue_counts = overdue_counts.sort_values("Просрочка", ascending=False)

# Построим график
plt.figure(figsize=(8,5))
sns.barplot(data=overdue_counts, x="ИНКОТЕРМС", y="Просрочка", palette="rocket")
plt.title("Количество просроченных инвойсов по INCOTERMS")
plt.xlabel("INCOTERMS")
plt.ylabel("Количество просрочек")
plt.show()
