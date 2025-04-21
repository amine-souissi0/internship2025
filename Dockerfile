# Use a Python base image
FROM python:3.9-slim

# Install Nginx
RUN apt-get update && apt-get install -y nginx openssl

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app

# Install dependencies from requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . /app

# Copy the Nginx configuration file
COPY ./nginx.conf /etc/nginx/nginx.conf

# Copy the SSL certificates into the container
COPY ./certbot/self-signed.crt /etc/ssl/certs/self-signed.crt
COPY ./certbot/self-signed.key /etc/ssl/private/self-signed.key

# Expose the ports your application will run on
EXPOSE 5000 443

# Command to run the application
CMD ["python", "run.py"]
