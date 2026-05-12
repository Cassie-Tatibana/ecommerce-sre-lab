FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY simulator ./simulator
COPY exporter ./exporter

EXPOSE 8000

CMD ["python", "-m", "exporter.server"]
