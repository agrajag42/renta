FROM python:3.12-slim

# Install nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Remove default nginx config
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application files
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/friends/renta/index.html
COPY feedback_api.py /app/feedback_api.py
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

WORKDIR /app

ENV PORT=8080
EXPOSE 8080

CMD ["/app/start.sh"]
