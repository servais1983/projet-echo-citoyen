FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PORT=5003

EXPOSE 5003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5003", "--reload"] 