# Use a lightweight Python image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy application files
COPY files/ /app/files/
COPY files/templates /app/files/templates

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/files/requirements.txt

# Expose port
EXPOSE 5002

# Run the Flask app
CMD ["python", "/app/files/app.py"]
