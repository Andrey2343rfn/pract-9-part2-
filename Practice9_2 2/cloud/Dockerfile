FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY connector.py analytics.py ./
EXPOSE 5000
CMD ["python", "-u", "connector.py"]
