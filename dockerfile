# ���������� ����������� ����� Python 3.11
FROM python:3.11-slim

# ��������� ������� � ������������� ����������� �����������
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ������� ������� ����������
WORKDIR /app

# �������� ������ � ���������
COPY verify_gost2012.py /app/

# ��������� pygost �� �����������
RUN git clone https://github.com/torquemada/pygost.git /app/pygost

# ������������� ����������� asn1crypto
RUN pip install --no-cache-dir asn1crypto

# ������������ PYTHONPATH, ����� Python ������� pygost � ����� �������
ENV PYTHONPATH=/app/pygost

# �� ��������� ��������� Python
ENTRYPOINT ["python3", "/app/verify_gost2012.py"]
