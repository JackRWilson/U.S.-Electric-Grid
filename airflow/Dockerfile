FROM apache/airflow:3.3.1-python3.12

USER root
RUN mkdir -p /opt/airflow/cache && chown airflow:root /opt/airflow/cache

USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.3.1/constraints-3.12.txt" \
    -r /requirements.txt
