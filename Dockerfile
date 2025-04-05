FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create necessary directories
RUN mkdir -p uploads app/output app/static \
    && chmod -R 777 uploads app/output app/static

# Expose port
EXPOSE 5001

# Set environment variables for Flask
ENV FLASK_APP=app.web_app \
    FLASK_ENV=production \
    FLASK_DEBUG=0

CMD ["python", "run.py"]