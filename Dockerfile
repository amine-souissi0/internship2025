FROM python:3.9-slim

# Install Nginx and dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    certbot \
    python3-certbot-nginx \
    && rm -rf /var/lib/apt/lists/*

# Install Flask and other dependencies
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

# Add your Flask application
COPY . /app/

# Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports for Nginx and Flask
EXPOSE 80
EXPOSE 443

# Command to start both Flask and Nginx
CMD service nginx start && python app.py
