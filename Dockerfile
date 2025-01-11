# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Start application
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
