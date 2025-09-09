# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Обновляем систему и устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем скрипт в контейнер
COPY verify_gost2012.py /app/

# Клонируем pygost из репозитория
RUN git clone https://github.com/torquemada/pygost.git /app/pygost

# Устанавливаем зависимость asn1crypto
RUN pip install --no-cache-dir asn1crypto

# Экспортируем PYTHONPATH, чтобы Python находил pygost в папке проекта
ENV PYTHONPATH=/app/pygost

# По умолчанию запускаем Python
ENTRYPOINT ["python3", "/app/verify_gost2012.py"]
