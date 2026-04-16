# 1. Base image
FROM python:3.9-slim

# 2. Working directory
WORKDIR /app

# 3. Zaroori system dependencies (Updated for Slim image)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Requirements copy aur install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Saara code copy
COPY . .

# 6. Port expose
EXPOSE 8080

# 7. Command to run
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
