FROM python:3.12-slim

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY index.html /usr/share/nginx/html/apps/renta/index.html
COPY feedback_api.py /app/feedback_api.py

WORKDIR /app

ENV PORT=8080
EXPOSE 8080

CMD ["python3", "-m", "uvicorn", "feedback_api:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "warning"]
